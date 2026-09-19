"""Multi-asset alignment engine ensuring common calendar without lookahead bias."""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional
import logging

logger = logging.getLogger(__name__)


class MultiAssetAligner:
    """
    Aligns multiple asset OHLCV time series to a unified trading calendar.
    
    Rules:
    - Reindexes all assets to the primary trading-day calendar (intersection or standard NYSE/business days).
    - Missing values on trading days (e.g. holidays or weekend carryover) are forward-filled ONLY (ffill).
    - NEVER back-fills (bfill) as that leaks future price information.
    - Accurately tracks and reports fill counts per asset.
    """

    @staticmethod
    def get_unified_calendar(asset_dfs: Dict[str, pd.DataFrame], calendar_mode: str = "equity") -> pd.DatetimeIndex:
        """
        Derives common calendar index.
        - 'equity': uses the trading days of traditional market assets (e.g., NVDA / Gold), or business days.
        - 'union': union of all dates across all assets.
        - 'intersection': dates present in all assets.
        """
        if not asset_dfs:
            return pd.DatetimeIndex([])

        if calendar_mode == "equity":
            # Priority: NVDA or Gold calendar (traditional market days)
            for preferred in ["NVIDIA", "Gold"]:
                if preferred in asset_dfs and not asset_dfs[preferred].empty:
                    return asset_dfs[preferred].index.sort_values()
            
            # Fallback to business day range
            all_min = min(df.index.min() for df in asset_dfs.values() if not df.empty)
            all_max = max(df.index.max() for df in asset_dfs.values() if not df.empty)
            return pd.bdate_range(start=all_min, end=all_max)

        elif calendar_mode == "union":
            all_dates = set()
            for df in asset_dfs.values():
                if not df.empty:
                    all_dates.update(df.index)
            return pd.DatetimeIndex(sorted(list(all_dates)))

        elif calendar_mode == "intersection":
            common = None
            for df in asset_dfs.values():
                if not df.empty:
                    if common is None:
                        common = set(df.index)
                    else:
                        common = common.intersection(set(df.index))
            return pd.DatetimeIndex(sorted(list(common or [])))

        raise ValueError(f"Unknown calendar mode: {calendar_mode}")

    @classmethod
    def align(
        cls,
        asset_dfs: Dict[str, pd.DataFrame],
        calendar_mode: str = "equity",
    ) -> Tuple[Dict[str, pd.DataFrame], pd.DataFrame, Dict[str, int]]:
        """
        Aligns a dictionary of asset OHLCV DataFrames.

        Returns:
            aligned_dfs: Dict[str, pd.DataFrame] with matching DatetimeIndex.
            aligned_close: pd.DataFrame with close prices of all assets.
            fill_stats: Dict[str, int] count of forward-filled bars per asset.
        """
        if not asset_dfs:
            return {}, pd.DataFrame(), {}

        # 1. Determine common target calendar
        common_idx = cls.get_unified_calendar(asset_dfs, calendar_mode=calendar_mode)
        if len(common_idx) == 0:
            return {}, pd.DataFrame(), {}

        # Trim common index to overlapping start/end to avoid leading NaNs
        starts = [df.index.min() for df in asset_dfs.values() if not df.empty]
        latest_start = max(starts)
        common_idx = common_idx[common_idx >= latest_start]

        aligned_dfs: Dict[str, pd.DataFrame] = {}
        close_dict: Dict[str, pd.Series] = {}
        fill_stats: Dict[str, int] = {}

        for name, df in asset_dfs.items():
            if df.empty:
                continue

            # Reindex to target calendar
            reindexed = df.reindex(common_idx)

            # Count missing values prior to forward-filling
            missing_close_count = int(reindexed["close"].isna().sum())

            # Forward fill only (NEVER bfill!)
            # Price columns forward-filled, volume filled with 0
            price_cols = [c for c in ["open", "high", "low", "close"] if c in reindexed.columns]
            reindexed[price_cols] = reindexed[price_cols].ffill()

            if "volume" in reindexed.columns:
                reindexed["volume"] = reindexed["volume"].fillna(0.0)

            # Drop any remaining unfillable leading NaNs if start precedes asset's first bar
            reindexed = reindexed.dropna(subset=["close"])

            aligned_dfs[name] = reindexed
            close_dict[name] = reindexed["close"]
            fill_stats[name] = missing_close_count
            logger.info(f"Asset '{name}' aligned to {len(reindexed)} bars. Forward-filled: {missing_close_count} bars.")

        # Build unified close dataframe on common index
        aligned_close = pd.DataFrame(close_dict).dropna()
        
        # Ensure all individual aligned dfs match the exact final aligned_close index
        final_idx = aligned_close.index
        for name in list(aligned_dfs.keys()):
            aligned_dfs[name] = aligned_dfs[name].reindex(final_idx).ffill()

        return aligned_dfs, aligned_close, fill_stats
