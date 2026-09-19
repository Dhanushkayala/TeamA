"""Market Regime Classification and Regime-Conditioned Performance Analysis."""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional

from quant_platform.indicators.moving_averages import calculate_sma
from quant_platform.indicators.oscillators import calculate_atr
from quant_platform.indicators.risk_metrics import (
    calculate_annualized_volatility,
    calculate_sharpe_ratio,
    calculate_drawdown_series,
    calculate_max_drawdown,
)


class RegimeClassifier:
    """
    Classifies market state into 4 regimes strictly using historical expanding/rolling data:
    - Bull / Low Volatility (Green)
    - Bull / High Volatility (Cyan/Yellow)
    - Bear / Low Volatility (Orange)
    - Bear / High Volatility (Red)
    """

    REGIMES = [
        "Bull / Low Volatility",
        "Bull / High Volatility",
        "Bear / Low Volatility",
        "Bear / High Volatility",
    ]

    REGIME_COLORS = {
        "Bull / Low Volatility": "rgba(16, 185, 129, 0.20)",   # Subtle green
        "Bull / High Volatility": "rgba(245, 158, 11, 0.20)",  # Subtle amber
        "Bear / Low Volatility": "rgba(235, 104, 52, 0.20)",   # Subtle orange
        "Bear / High Volatility": "rgba(239, 68, 68, 0.25)",   # Subtle red
        "Unclassified": "rgba(150, 150, 150, 0.10)",
    }

    @classmethod
    def classify(
        cls,
        df: pd.DataFrame,
        trend_sma_window: int = 200,
        vol_atr_window: int = 14,
        vol_threshold_quantile: float = 0.50,
        min_history: int = 60,
    ) -> pd.DataFrame:
        """
        Classify each date into market regime with NO look-ahead leakage.
        
        Rules:
        - Trend: Bull if Close > SMA(trend_sma_window), else Bear.
        - Volatility: ATR(vol_atr_window). Compared to expanding median ATR up to that day.
        """
        result = df.copy()
        close = result["close"]

        # 1. Trend Filter
        sma = calculate_sma(close, window=trend_sma_window)
        # For dates with < trend_sma_window bars, fallback to expanding mean or shorter SMA
        sma_fallback = close.expanding(min_periods=min_history).mean()
        effective_sma = sma.combine_first(sma_fallback)

        is_bull = close > effective_sma

        # 2. Volatility Filter (ATR vs expanding quantile)
        atr = calculate_atr(result, window=vol_atr_window)
        
        # Expanding quantile of past ATR (no future leakage)
        expanding_vol_thresh = atr.expanding(min_periods=min_history).quantile(vol_threshold_quantile)
        is_high_vol = atr > expanding_vol_thresh

        # 3. Combine into discrete 4 regimes
        regime_series = pd.Series("Unclassified", index=df.index)
        
        bull_low = is_bull & (~is_high_vol) & effective_sma.notna() & expanding_vol_thresh.notna()
        bull_high = is_bull & is_high_vol & effective_sma.notna() & expanding_vol_thresh.notna()
        bear_low = (~is_bull) & (~is_high_vol) & effective_sma.notna() & expanding_vol_thresh.notna()
        bear_high = (~is_bull) & is_high_vol & effective_sma.notna() & expanding_vol_thresh.notna()

        regime_series[bull_low] = "Bull / Low Volatility"
        regime_series[bull_high] = "Bull / High Volatility"
        regime_series[bear_low] = "Bear / Low Volatility"
        regime_series[bear_high] = "Bear / High Volatility"

        result["sma_trend"] = effective_sma
        result["atr"] = atr
        result["vol_threshold"] = expanding_vol_thresh
        result["regime"] = regime_series

        return result

    @classmethod
    def evaluate_regime_performance(
        cls,
        classified_df: pd.DataFrame,
        strategy_daily_returns: pd.Series,
        periods_per_year: int = 252,
        risk_free_rate: float = 0.04,
    ) -> pd.DataFrame:
        """
        Evaluate returns, volatility, Sharpe ratio, and drawdown broken down by market regime.
        """
        aligned_returns = strategy_daily_returns.reindex(classified_df.index).fillna(0.0)
        regimes = classified_df["regime"]

        rows = []
        for reg in cls.REGIMES:
            mask = (regimes == reg)
            reg_rets = aligned_returns[mask]
            count_days = int(mask.sum())
            
            if count_days < 5:
                rows.append({
                    "Regime": reg,
                    "Days": count_days,
                    "Time in Regime (%)": round((count_days / len(classified_df)) * 100, 1),
                    "Cumulative Return (%)": 0.0,
                    "Annualized Return (%)": 0.0,
                    "Annualized Vol (%)": 0.0,
                    "Sharpe Ratio": 0.0,
                    "Max Drawdown (%)": 0.0,
                    "Win Rate (%)": 0.0,
                })
                continue

            cum_ret = float((1.0 + reg_rets).prod() - 1.0)
            ann_ret = float(reg_rets.mean() * periods_per_year)
            ann_vol = calculate_annualized_volatility(reg_rets, periods_per_year=periods_per_year)
            sharpe = calculate_sharpe_ratio(reg_rets, risk_free_rate=risk_free_rate, periods_per_year=periods_per_year)
            
            # Cumulative series in regime for drawdown
            cum_path = (1.0 + reg_rets).cumprod()
            mdd = calculate_max_drawdown(cum_path)
            
            win_days = (reg_rets > 0).sum()
            win_rate = (win_days / len(reg_rets)) if len(reg_rets) > 0 else 0.0

            rows.append({
                "Regime": reg,
                "Days": count_days,
                "Time in Regime (%)": round((count_days / len(classified_df)) * 100, 1),
                "Cumulative Return (%)": round(cum_ret * 100, 2),
                "Annualized Return (%)": round(ann_ret * 100, 2),
                "Annualized Vol (%)": round(float(ann_vol) * 100, 2),
                "Sharpe Ratio": round(float(sharpe), 2),
                "Max Drawdown (%)": round(float(mdd) * 100, 2),
                "Win Rate (%)": round(win_rate * 100, 1),
            })

        return pd.DataFrame(rows)
