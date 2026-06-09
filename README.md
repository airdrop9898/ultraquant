# UltraQuant — Real-Time Quantitative Trading Signals

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MiMo UltraSpeed](https://img.shields.io/badge/MiMo-UltraSpeed-orange.svg)](https://platform.xiaomimimo.com)

Real-time quantitative trading signal generator powered by **MiMo-V2.5-Pro-UltraSpeed**. Processes market data streams at millisecond latency, generates AI-driven trading signals, and closes the decision loop before market moves propagate.

**Core advantage:** UltraSpeed's 1000 tokens/s inference turns breaking news and price anomalies into actionable signals in under 200ms — where traditional LLM-based tools take 2-10 seconds.

## Architecture

```
Market Data (WebSocket)
    │
    ▼
┌─────────────────────┐
│  Event Detector     │  Price/volume anomaly detection (<1ms, pure Python)
└─────────┬───────────┘
          │ anomaly detected
          ▼
┌─────────────────────┐
│  UltraSpeed Engine  │  MiMo V2.5 Pro UltraSpeed — signal generation (<200ms)
└─────────┬───────────┘
          │ signal
          ▼
┌─────────────────────┐
│  Risk Manager       │  Position sizing, stop-loss, drawdown limits
└─────────┬───────────┘
          │ order
          ▼
┌─────────────────────┐
│  Execution Engine   │  Paper trading (default) or live via broker API
└─────────────────────┘
```

## Features

- **Millisecond event detection** — sliding-window anomaly scanner (price spikes, volume surges, Bollinger breaches)
- **UltraSpeed AI reasoning** — 1000 tok/s for instant signal generation with structured JSON output
- **Multi-asset support** — stocks, crypto, forex via pluggable connectors
- **Streaming architecture** — async WebSocket ingestion, zero-copy buffers
- **Paper trading default** — test strategies risk-free before going live
- **Risk management** — Kelly criterion sizing, max drawdown limits, position caps
- **Backtest engine** — replay historical CSV data through the same pipeline
- **Performance tracking** — P&L, Sharpe ratio, win rate, latency metrics

## Quick Start

```bash
git clone https://github.com/airdrop9898/ultraquant.git
cd ultraquant
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your MIMO_API_KEY

# Paper trading
python -m ultraquant.main --mode paper --asset BTC-USD

# Backtest
python -m ultraquant.main --mode backtest --data ./data/BTC_1m.csv
```

## Signal Output

```json
{
  "timestamp": "2026-06-09T14:32:01.234Z",
  "asset": "BTC-USD",
  "signal": "LONG",
  "confidence": 0.82,
  "reasoning": "Price broke 4h resistance at $71,200 with 2.8x volume. RSI 62 — momentum without overbought. Negative funding rate suggests short squeeze.",
  "position_size_pct": 3.2,
  "stop_loss": 70800,
  "take_profit": 72500,
  "latency_ms": 187
}
```

## Why UltraSpeed?

| Capability | Standard LLM | UltraSpeed (1000 tok/s) |
|---|---|---|
| News → Signal | 3-8 seconds | <200ms |
| Multi-factor analysis | 5-12 seconds | <300ms |
| Real-time risk check | Not viable | <100ms |
| Alpha decay | 80-95% lost | <5% lost |

## Configuration

```env
MIMO_API_KEY=your_key_here
MIMO_BASE_URL=https://api.xiaomimimo.com/v1
MIMO_MODEL=mimo-v2.5-pro-ultraspeed
TRADING_MODE=paper
RISK_MAX_POSITION_PCT=5.0
RISK_MAX_DRAWDOWN_PCT=15.0
```

## Requirements

- Python 3.10+
- MiMo API key (UltraSpeed tier)
- NumPy, OpenAI SDK, websockets

## License

MIT
