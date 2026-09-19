"""Disk caching layer using Parquet for fast offline access."""

import os
from pathlib import Path
import pandas as pd
from typing import Optional
from quant_platform.config import CACHE_DIR


class DiskCache:
    """Manages local parquet-based caching for asset time series."""

    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, symbol: str) -> Path:
        # Sanitize symbol for file names (e.g., GC=F -> GC_F, BTC/USD -> BTC_USD)
        clean_name = symbol.replace("/", "_").replace("=", "_").replace("^", "_")
        return self.cache_dir / f"{clean_name}.parquet"

    def get(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Optional[pd.DataFrame]:
        """Retrieve cached DataFrame if it covers the requested date range."""
        path = self._get_path(symbol)
        if not path.exists():
            return None
        
        try:
            df = pd.read_parquet(path)
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)
            df = df.sort_index()

            # Check if cache covers the requested range
            if start_date:
                req_start = pd.to_datetime(start_date)
                if df.index[0] > req_start:
                    return None  # Cache does not go far back enough
            if end_date:
                req_end = pd.to_datetime(end_date)
                if df.index[-1] < req_end:
                    # Note: today or last trading day may be acceptable, but if significant gap, re-fetch
                    pass
            
            # Slice to requested date range
            if start_date:
                df = df[df.index >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df.index <= pd.to_datetime(end_date)]
            
            return df if not df.empty else None
        except Exception:
            return None

    def put(self, symbol: str, df: pd.DataFrame) -> None:
        """Save DataFrame to parquet cache."""
        if df.empty:
            return
        path = self._get_path(symbol)
        try:
            # Merge with existing cache if available
            if path.exists():
                existing_df = pd.read_parquet(path)
                if not isinstance(existing_df.index, pd.DatetimeIndex):
                    existing_df.index = pd.to_datetime(existing_df.index)
                combined = pd.concat([existing_df, df])
                combined = combined[~combined.index.duplicated(keep="last")].sort_index()
                combined.to_parquet(path)
            else:
                df.to_parquet(path)
        except Exception as e:
            # Non-fatal caching failure
            pass

    def clear(self) -> None:
        """Clear all cached files."""
        for file in self.cache_dir.glob("*.parquet"):
            try:
                file.unlink()
            except Exception:
                pass
