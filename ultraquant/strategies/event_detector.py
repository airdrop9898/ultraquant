"""High-performance event detection — pure Python, no LLM dependency."""

import time
from collections import deque

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class EventDetector:
    """Sliding-window anomaly detector for price and volume streams."""

    def __init__(self, window_size: int = 100, volume_threshold: float = 2.5, price_threshold: float = 0.015):
        self.window_size = window_size
        self.volume_threshold = volume_threshold
        self.price_threshold = price_threshold
        self.prices = deque(maxlen=window_size)
        self.volumes = deque(maxlen=window_size)

    def update(self, price: float, volume: float, timestamp: float = None) -> dict | None:
        """Feed new tick, return event dict if anomaly detected."""
        self.prices.append(price)
        self.volumes.append(volume)

        if len(self.prices) < 20:
            return None

        recent_prices = list(self.prices)[-20:]
        recent_volumes = list(self.volumes)[-20:]

        avg_vol = sum(recent_volumes) / 20
        vol_ratio = volume / avg_vol if avg_vol > 0 else 0

        avg_price = sum(recent_prices) / 20
        price_pct = (price - avg_price) / avg_price

        # Volume surge
        if vol_ratio > self.volume_threshold:
            return {
                "type": "volume_surge",
                "timestamp": timestamp or time.time(),
                "price": price, "volume": volume,
                "volume_ratio": round(vol_ratio, 2),
                "price_vs_sma20": round(price_pct * 100, 3),
            }

        # Price breakout
        if abs(price_pct) > self.price_threshold:
            return {
                "type": "price_breakout",
                "timestamp": timestamp or time.time(),
                "price": price, "volume": volume,
                "direction": "bullish" if price_pct > 0 else "bearish",
                "breakout_pct": round(price_pct * 100, 3),
            }

        # Bollinger Band breach
        if HAS_NUMPY and len(recent_prices) >= 20:
            std = float(np.std(recent_prices))
            upper = avg_price + 2 * std
            lower = avg_price - 2 * std
            if price > upper or price < lower:
                return {
                    "type": "bband_breach",
                    "timestamp": timestamp or time.time(),
                    "price": price,
                    "band": "upper" if price > upper else "lower",
                    "std_dev": round(std, 2),
                }

        return None
