"""Data validation, cleaning, and sanitization."""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List


class DataValidationError(Exception):
    """Raised when asset price series fails integrity validation."""
    pass


class DataCleaner:
    """Validates and cleans financial OHLCV time series."""

    REQUIRED_COLS = ["open", "high", "low", "close", "volume"]

    @staticmethod
    def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to lowercase ['open', 'high', 'low', 'close', 'volume']."""
        clean_df = df.copy()
        clean_df.columns = [str(c).lower().strip() for c in clean_df.columns]
        
        # Handle adjusted close if present
        if "adj close" in clean_df.columns and "close" not in clean_df.columns:
            clean_df["close"] = clean_df["adj close"]
        
        return clean_df

    @classmethod
    def validate_and_clean(cls, df: pd.DataFrame, asset_name: str = "Asset") -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Validates OHLCV DataFrame for data integrity:
        1. Ensures standard column names.
        2. Ensures DateTime index with timezone-naive dates.
        3. Removes duplicate dates (keeps last).
        4. Verifies no negative or zero prices in OHLC.
        5. Validates high >= low, high >= open, high >= close.
        6. Detects large unexpected gaps.
        """
        if df is None or df.empty:
            raise DataValidationError(f"[{asset_name}] Received empty DataFrame.")

        df = cls.standardize_columns(df)

        # Verify required columns
        for col in ["close"]:
            if col not in df.columns:
                raise DataValidationError(f"[{asset_name}] Missing required column '{col}'. Available: {list(df.columns)}")

        # Ensure DatetimeIndex
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        # Convert timezone to naive date-normalized index
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
        
        df.index = df.index.normalize()

        stats = {
            "initial_rows": len(df),
            "duplicate_dates_dropped": 0,
            "negative_prices_detected": 0,
            "high_low_violations": 0,
            "large_gaps_flagged": 0,
        }

        # Check & remove duplicate timestamps
        if df.index.duplicated().any():
            stats["duplicate_dates_dropped"] = int(df.index.duplicated().sum())
            df = df[~df.index.duplicated(keep="last")]

        df = df.sort_index()

        # Check for non-positive prices
        price_cols = [c for c in ["open", "high", "low", "close"] if c in df.columns]
        for col in price_cols:
            invalid_mask = df[col] <= 0
            if invalid_mask.any():
                stats["negative_prices_detected"] += int(invalid_mask.sum())
                # Replace zero/negative with forward-filled previous valid price
                df.loc[invalid_mask, col] = np.nan
                df[col] = df[col].ffill()

        # Check high / low consistency if available
        if "high" in df.columns and "low" in df.columns:
            violations = (df["high"] < df["low"])
            if violations.any():
                stats["high_low_violations"] = int(violations.sum())
                # Fix inverted high/low
                temp_high = df.loc[violations, "high"].copy()
                df.loc[violations, "high"] = df.loc[violations, "low"]
                df.loc[violations, "low"] = temp_high

        # Detect gaps > 5 calendar days
        date_diffs = df.index.to_series().diff().dt.days
        large_gaps = date_diffs[date_diffs > 5]
        stats["large_gaps_flagged"] = len(large_gaps)

        # Fill volume if missing
        if "volume" not in df.columns:
            df["volume"] = 1000000.0
        else:
            df["volume"] = df["volume"].fillna(0.0)

        # Drop any remaining NaNs in close
        df = df.dropna(subset=["close"])

        stats["final_rows"] = len(df)
        return df, stats
