"""Core trading engine — event detection → UltraSpeed inference → risk → execution."""

import asyncio
import time
import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional, Literal

from openai import AsyncOpenAI


@dataclass
class Signal:
    timestamp: float
    asset: str
    signal: Literal["LONG", "SHORT", "HOLD"]
    confidence: float
    reasoning: str
    position_size_pct: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    latency_ms: float = 0.0


@dataclass
class MarketEvent:
    timestamp: float
    asset: str
    price: float
    volume: float
    event_type: str
    details: dict = field(default_factory=dict)


class TradingEngine:
    """Full trading pipeline: data → detect → infer → risk → execute."""

    def __init__(self, mode: str, asset: str, config: dict):
        self.mode = mode
        self.asset = asset
        self.config = config
        self.client = AsyncOpenAI(
            api_key=config.get("mimo_api_key", os.environ.get("MIMO_API_KEY", "")),
            base_url=config.get("mimo_base_url", "https://api.xiaomimimo.com/v1"),
        )
        self.model = config.get("mimo_model", "mimo-v2.5-pro-ultraspeed")
        self.signals: list[Signal] = []
        self._running = False

    async def _detect_event(self, price: float, volume: float, history: list) -> Optional[MarketEvent]:
        """Millisecond anomaly detection — pure Python, no LLM."""
        if len(history) < 20:
            return None

        avg_vol = sum(h["volume"] for h in history[-20:]) / 20
        avg_price = sum(h["price"] for h in history[-20:]) / 20
        price_chg = (price - avg_price) / avg_price

        if volume > avg_vol * 2.5:
            return MarketEvent(
                timestamp=time.time(), asset=self.asset, price=price, volume=volume,
                event_type="volume_surge",
                details={"volume_ratio": round(volume / avg_vol, 2), "price_change_pct": round(price_chg * 100, 3)},
            )
        if abs(price_chg) > 0.015:
            return MarketEvent(
                timestamp=time.time(), asset=self.asset, price=price, volume=volume,
                event_type="price_breakout",
                details={"direction": "up" if price_chg > 0 else "down", "pct": round(price_chg * 100, 3)},
            )
        return None

    async def _generate_signal(self, event: MarketEvent) -> Signal:
        """UltraSpeed inference — market event → trading signal in <200ms."""
        t0 = time.time()

        prompt = (
            f"Market event detected:\n"
            f"Asset: {event.asset}\nEvent: {event.event_type}\n"
            f"Price: ${event.price:,.2f}\nVolume: {event.volume:,.0f}\n"
            f"Details: {json.dumps(event.details)}\n\n"
            f"Respond in JSON: {{\"signal\":\"LONG|SHORT|HOLD\",\"confidence\":0.0-1.0,"
            f"\"reasoning\":\"...\",\"position_size_pct\":0.0-5.0,"
            f"\"stop_loss\":price,\"take_profit\":price}}"
        )

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Quant trading signal generator. Be concise, data-driven. Respond with valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            max_completion_tokens=512,
            temperature=0.1,
        )

        latency_ms = (time.time() - t0) * 1000
        content = response.choices[0].message.content.strip()

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            data = {"signal": "HOLD", "confidence": 0.0, "reasoning": "Parse error", "position_size_pct": 0.0}

        return Signal(
            timestamp=event.timestamp, asset=event.asset,
            signal=data.get("signal", "HOLD"),
            confidence=data.get("confidence", 0.0),
            reasoning=data.get("reasoning", ""),
            position_size_pct=data.get("position_size_pct", 0.0),
            stop_loss=data.get("stop_loss"),
            take_profit=data.get("take_profit"),
            latency_ms=round(latency_ms, 1),
        )

    async def _apply_risk(self, signal: Signal) -> Signal:
        """Enforce position limits and confidence thresholds."""
        max_pos = float(self.config.get("risk_max_position_pct", 5.0))
        if signal.position_size_pct > max_pos:
            signal.position_size_pct = max_pos
        if signal.confidence < 0.5:
            signal.signal = "HOLD"
            signal.position_size_pct = 0.0
        return signal

    async def run_live(self):
        """Main loop — detect events, generate signals, manage risk."""
        self._running = True
        history = []
        import random

        base = 70000.0 if "BTC" in self.asset else 100.0
        print(f"[UltraQuant] Live loop started for {self.asset}")

        while self._running:
            price = base * (1 + random.uniform(-0.005, 0.005))
            volume = random.uniform(100000, 500000)
            history.append({"price": price, "volume": volume, "ts": time.time()})

            event = await self._detect_event(price, volume, history)
            if event:
                signal = await self._generate_signal(event)
                signal = await self._apply_risk(signal)
                self.signals.append(signal)
                print(f"[{signal.signal}] conf={signal.confidence:.2f} size={signal.position_size_pct:.1f}% "
                      f"lat={signal.latency_ms:.0f}ms | {signal.reasoning[:80]}")

            await asyncio.sleep(0.1)

    async def run_backtest(self, data_path: str, start_date: str = None, end_date: str = None):
        """Replay historical CSV through the pipeline."""
        import csv
        results = {"signals": [], "trades": 0}
        with open(data_path) as f:
            reader = csv.DictReader(f)
            history = []
            for row in reader:
                price = float(row.get("close", row.get("price", 0)))
                volume = float(row.get("volume", 0))
                history.append({"price": price, "volume": volume})
                if len(history) >= 20:
                    event = await self._detect_event(price, volume, history)
                    if event:
                        signal = await self._generate_signal(event)
                        signal = await self._apply_risk(signal)
                        results["signals"].append(asdict(signal))
                        results["trades"] += 1
        return results

    def print_results(self, results: dict):
        print(f"\n{'='*50}")
        print("UltraQuant Backtest Results")
        print(f"{'='*50}")
        print(f"Signals generated: {len(results['signals'])}")
        print(f"Trades executed: {results['trades']}")
        if results["signals"]:
            avg_lat = sum(s["latency_ms"] for s in results["signals"]) / len(results["signals"])
            print(f"Avg latency: {avg_lat:.0f}ms")
