"""Multi-source asset data fetcher (Alpaca, yfinance, local cache, synthetic fallback)."""

import os
import datetime
import logging
import numpy as np
import pandas as pd
from typing import Optional, Dict, Tuple

from quant_platform.config import (
    APCA_API_KEY_ID,
    APCA_API_SECRET_KEY,
    APCA_PAPER,
    DEFAULT_ASSETS,
)
from quant_platform.data.cache import DiskCache
from quant_platform.data.cleaner import DataCleaner, DataValidationError

logger = logging.getLogger(__name__)


class DataFetcher:
    """Fetches multi-asset OHLCV data using Alpaca with yfinance and cached fallbacks."""

    def __init__(self, use_cache: bool = True):
        self.use_cache = use_cache
        self.cache = DiskCache()
        self._alpaca_client = None
        self._alpaca_crypto_client = None
        self._init_alpaca()

    def _init_alpaca(self):
        """Initialize Alpaca Historical Data clients if credentials are present."""
        if APCA_API_KEY_ID and APCA_API_SECRET_KEY:
            try:
                from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
                self._alpaca_client = StockHistoricalDataClient(
                    api_key=APCA_API_KEY_ID,
                    secret_key=APCA_API_SECRET_KEY,
                )
                self._alpaca_crypto_client = CryptoHistoricalDataClient(
                    api_key=APCA_API_KEY_ID,
                    secret_key=APCA_API_SECRET_KEY,
                )
                logger.info("Alpaca data clients initialized successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize Alpaca clients: {e}")
                self._alpaca_client = None
                self._alpaca_crypto_client = None

    def fetch_alpaca_stock(self, symbol: str, start: str, end: str) -> Optional[pd.DataFrame]:
        """Fetch stock OHLCV from Alpaca."""
        if not self._alpaca_client:
            return None
        try:
            from alpaca.data.requests import StockBarsRequest
            from alpaca.data.timeframe import TimeFrame

            req = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Day,
                start=pd.to_datetime(start),
                end=pd.to_datetime(end),
            )
            bars = self._alpaca_client.get_stock_bars(req)
            df = bars.df
            if isinstance(df.index, pd.MultiIndex):
                df = df.xs(symbol, level=0)
            return df
        except Exception as e:
            logger.warning(f"Alpaca stock fetch failed for {symbol}: {e}")
            return None

    def fetch_alpaca_crypto(self, symbol: str, start: str, end: str) -> Optional[pd.DataFrame]:
        """Fetch crypto OHLCV from Alpaca."""
        if not self._alpaca_crypto_client:
            return None
        try:
            from alpaca.data.requests import CryptoBarsRequest
            from alpaca.data.timeframe import TimeFrame

            req = CryptoBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Day,
                start=pd.to_datetime(start),
                end=pd.to_datetime(end),
            )
            bars = self._alpaca_crypto_client.get_crypto_bars(req)
            df = bars.df
            if isinstance(df.index, pd.MultiIndex):
                df = df.xs(symbol, level=0)
            return df
        except Exception as e:
            logger.warning(f"Alpaca crypto fetch failed for {symbol}: {e}")
            return None

    def fetch_yfinance(self, symbol: str, start: str, end: str) -> Optional[pd.DataFrame]:
        """Fetch OHLCV from Yahoo Finance."""
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start, end=end, auto_adjust=True)
            if df is not None and not df.empty:
                return df
            # Fallback download method
            df = yf.download(symbol, start=start, end=end, progress=False, auto_adjust=True)
            if df is not None and not df.empty:
                # If MultiIndex columns from newer yfinance
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [col[0] for col in df.columns]
                return df
        except Exception as e:
            logger.warning(f"yfinance fetch failed for {symbol}: {e}")
        return None

    def generate_synthetic_data(self, asset_name: str, symbol: str, start: str, end: str) -> pd.DataFrame:
        """
        Generate realistic synthetic financial time series using Geometric Brownian Motion.
        Used when offline or when external APIs are rate limited.
        """
        dates = pd.date_range(start=start, end=end, freq="D")
        n = len(dates)
        if n == 0:
            dates = pd.date_range(start="2020-01-01", end="2026-01-01", freq="D")
            n = len(dates)

        # Asset-specific calibration parameters (drift, vol, start_price)
        calibrations = {
            "Gold": {"s0": 1550.0, "mu": 0.08, "sigma": 0.14, "seed": 42},
            "Bitcoin": {"s0": 7200.0, "mu": 0.55, "sigma": 0.65, "seed": 101},
            "NVIDIA": {"s0": 15.0, "mu": 0.70, "sigma": 0.48, "seed": 777},
        }

        calib = calibrations.get(asset_name, {"s0": 100.0, "mu": 0.10, "sigma": 0.25, "seed": hash(asset_name) % 10000})
        np.random.seed(calib["seed"])

        dt = 1 / 252.0
        # Simulated log returns with student-t fat tails
        shocks = np.random.standard_t(df=5, size=n) * (calib["sigma"] * np.sqrt(dt) * np.sqrt(3/5))
        log_returns = (calib["mu"] - 0.5 * calib["sigma"]**2) * dt + shocks
        
        # Accumulate price path
        price_path = calib["s0"] * np.exp(np.cumsum(log_returns))
        
        # Build plausible OHLCV
        df = pd.DataFrame(index=dates)
        noise_high = 1 + np.abs(np.random.normal(0, 0.008, n))
        noise_low = 1 - np.abs(np.random.normal(0, 0.008, n))
        noise_open = 1 + np.random.normal(0, 0.004, n)

        df["close"] = price_path
        df["open"] = price_path * noise_open
        df["high"] = np.maximum(df["open"], df["close"]) * noise_high
        df["low"] = np.minimum(df["open"], df["close"]) * noise_low
        df["volume"] = np.random.lognormal(14, 0.6, n)

        return df

    def fetch_asset(
        self,
        asset_name: str,
        symbol: Optional[str] = None,
        start_date: str = "2020-01-01",
        end_date: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        Fetch asset data through prioritized multi-tiered fallback:
        1. Local Disk Cache
        2. Alpaca (if available for asset class)
        3. Yahoo Finance
        4. Synthetic Fallback
        """
        if end_date is None:
            end_date = datetime.date.today().isoformat()

        # Determine primary and fallback symbols from default config
        cfg = DEFAULT_ASSETS.get(asset_name, {})
        primary_sym = symbol or cfg.get("symbol", asset_name)
        alpaca_sym = cfg.get("alpaca_symbol")
        fallback_sym = cfg.get("fallback_symbol", primary_sym)
        asset_class = cfg.get("asset_class", "Equity")

        source_info = {"asset": asset_name, "symbol": primary_sym, "source": "unknown"}

        # 1. Check local cache
        if self.use_cache:
            cached = self.cache.get(primary_sym, start_date=start_date, end_date=end_date)
            if cached is not None and not cached.empty:
                try:
                    clean_df, _ = DataCleaner.validate_and_clean(cached, asset_name)
                    source_info["source"] = "Local Parquet Cache"
                    return clean_df, source_info
                except Exception:
                    pass

        df = None

        # 2. Try Alpaca if applicable
        if alpaca_sym:
            if asset_class == "Crypto":
                df = self.fetch_alpaca_crypto(alpaca_sym, start_date, end_date)
                if df is not None and not df.empty:
                    source_info["source"] = "Alpaca Crypto API"
            else:
                df = self.fetch_alpaca_stock(alpaca_sym, start_date, end_date)
                if df is not None and not df.empty:
                    source_info["source"] = "Alpaca Market Data API"

        # 3. Try yfinance
        if df is None or df.empty:
            df = self.fetch_yfinance(primary_sym, start_date, end_date)
            if df is not None and not df.empty:
                source_info["source"] = "Yahoo Finance"
            elif fallback_sym and fallback_sym != primary_sym:
                df = self.fetch_yfinance(fallback_sym, start_date, end_date)
                if df is not None and not df.empty:
                    source_info["source"] = f"Yahoo Finance ({fallback_sym})"

        # 4. Deterministic Synthetic fallback if network unavailable
        if df is None or df.empty:
            logger.info(f"Using synthetic data generator for {asset_name}")
            df = self.generate_synthetic_data(asset_name, primary_sym, start_date, end_date)
            source_info["source"] = "Calibrated Synthetic Engine (Offline Fallback)"

        # Clean & Validate
        clean_df, clean_stats = DataCleaner.validate_and_clean(df, asset_name)
        source_info.update(clean_stats)

        # Cache for future runs
        if self.use_cache:
            self.cache.put(primary_sym, clean_df)

        return clean_df, source_info
