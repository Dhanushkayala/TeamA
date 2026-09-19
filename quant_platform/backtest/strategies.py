"""Strategy implementations generating clear trading signals."""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Any, Type

from quant_platform.indicators.moving_averages import calculate_sma, calculate_ema
from quant_platform.indicators.oscillators import calculate_zscore, calculate_bollinger_bands


class BaseStrategy(ABC):
    """Abstract Base Class for quantitative trading strategies."""

    name: str = "Base Strategy"
    description: str = ""

    def __init__(self, **params):
        self.params = params

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate raw trading signals from OHLCV data.
        
        Returns:
            pd.Series with values:
            1.0: Long
            0.0: Flat / Cash
        """
        pass

    def get_param_schema(self) -> Dict[str, Any]:
        """Return parameter metadata for UI controls."""
        return {}


class SMACrossoverStrategy(BaseStrategy):
    """
    Simple Moving Average (SMA) Crossover Strategy:
    - Long when Fast SMA > Slow SMA
    - Flat when Fast SMA <= Slow SMA
    """

    name = "SMA Crossover"
    description = "Enters long when the fast simple moving average crosses above the slow moving average, and exits to cash when it crosses below."

    def __init__(self, fast_period: int = 20, slow_period: int = 50):
        super().__init__(fast_period=fast_period, slow_period=slow_period)
        self.fast_period = int(fast_period)
        self.slow_period = int(slow_period)

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        close = df["close"]
        fast_sma = calculate_sma(close, window=self.fast_period)
        slow_sma = calculate_sma(close, window=self.slow_period)

        signal = pd.Series(0.0, index=df.index)
        # Condition: Fast > Slow
        long_condition = (fast_sma > slow_sma) & fast_sma.notna() & slow_sma.notna()
        signal[long_condition] = 1.0
        return signal


class EMATrendStrategy(BaseStrategy):
    """
    Exponential Moving Average (EMA) Trend Strategy:
    - Long when Fast EMA > Slow EMA
    - Flat when Fast EMA <= Slow EMA
    """

    name = "EMA Trend"
    description = "Captures directional momentum using fast and slow exponential moving averages, giving higher weight to recent prices."

    def __init__(self, fast_span: int = 12, slow_span: int = 26):
        super().__init__(fast_span=fast_span, slow_span=slow_span)
        self.fast_span = int(fast_span)
        self.slow_span = int(slow_span)

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        close = df["close"]
        fast_ema = calculate_ema(close, span=self.fast_span)
        slow_ema = calculate_ema(close, span=self.slow_span)

        signal = pd.Series(0.0, index=df.index)
        long_condition = (fast_ema > slow_ema) & fast_ema.notna() & slow_ema.notna()
        signal[long_condition] = 1.0
        return signal


class MomentumStrategy(BaseStrategy):
    """
    Time-Series Momentum Strategy:
    - Long when Price Return over Lookback period > Threshold
    - Flat otherwise
    """

    name = "Momentum"
    description = "Enters long when the cumulative price return over a lookback window exceeds a defined threshold percentage."

    def __init__(self, lookback: int = 60, threshold_pct: float = 0.0):
        super().__init__(lookback=lookback, threshold_pct=threshold_pct)
        self.lookback = int(lookback)
        # Convert user-supplied percentage (e.g. 0.5 for 0.5%, 2.0 for 2.0%) to decimal
        self.threshold = float(threshold_pct) / 100.0

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        close = df["close"]
        roc = close.pct_change(periods=self.lookback)

        signal = pd.Series(0.0, index=df.index)
        long_condition = (roc > self.threshold) & roc.notna()
        signal[long_condition] = 1.0
        return signal



class MeanReversionStrategy(BaseStrategy):
    """
    Mean Reversion Strategy (Z-Score / Bollinger):
    - Enters long when Z-Score falls below entry threshold (oversold)
    - Exits to cash when Z-Score rises back to exit threshold (reversion to mean)
    """

    name = "Mean Reversion"
    description = "Identifies oversold conditions via rolling Z-score and holds until prices revert back towards the historical rolling mean."

    def __init__(self, lookback: int = 20, entry_z: float = -1.5, exit_z: float = 0.0):
        super().__init__(lookback=lookback, entry_z=entry_z, exit_z=exit_z)
        self.lookback = int(lookback)
        self.entry_z = float(entry_z)
        self.exit_z = float(exit_z)

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        close = df["close"]
        zscore = calculate_zscore(close, window=self.lookback)

        signals = np.zeros(len(df), dtype=float)
        in_position = False

        z_vals = zscore.values
        for i in range(len(df)):
            z = z_vals[i]
            if np.isnan(z):
                signals[i] = 0.0
                continue

            if not in_position:
                if z <= self.entry_z:
                    in_position = True
                    signals[i] = 1.0
                else:
                    signals[i] = 0.0
            else:
                if z >= self.exit_z:
                    in_position = False
                    signals[i] = 0.0
                else:
                    signals[i] = 1.0

        return pd.Series(signals, index=df.index)


STRATEGY_REGISTRY: Dict[str, Type[BaseStrategy]] = {
    "SMA Crossover": SMACrossoverStrategy,
    "EMA Trend": EMATrendStrategy,
    "Momentum": MomentumStrategy,
    "Mean Reversion": MeanReversionStrategy,
}
