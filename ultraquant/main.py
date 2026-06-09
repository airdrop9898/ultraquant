"""UltraQuant entry point — real-time trading signal generator."""

import asyncio
import argparse
import os

from ultraquant.engine import TradingEngine
from ultraquant.utils.config import load_config


def parse_args():
    parser = argparse.ArgumentParser(description="UltraQuant — MiMo UltraSpeed Trading Signals")
    parser.add_argument("--mode", choices=["paper", "live", "backtest"], default="paper")
    parser.add_argument("--asset", default="BTC-USD", help="Trading pair (BTC-USD, ETH-USD, AAPL)")
    parser.add_argument("--data", help="CSV data file for backtest mode")
    parser.add_argument("--start", help="Backtest start date (YYYY-MM-DD)")
    parser.add_argument("--end", help="Backtest end date (YYYY-MM-DD)")
    parser.add_argument("--config", default=".env", help="Config file path")
    return parser.parse_args()


async def main():
    args = parse_args()
    config = load_config(args.config)

    engine = TradingEngine(mode=args.mode, asset=args.asset, config=config)

    if args.mode == "backtest":
        if not args.data:
            print("Error: --data required for backtest mode")
            return
        results = await engine.run_backtest(data_path=args.data, start_date=args.start, end_date=args.end)
        engine.print_results(results)
    else:
        print(f"[UltraQuant] Starting {args.mode} mode for {args.asset}")
        print(f"[UltraQuant] UltraSpeed: {config.get('mimo_base_url', 'https://api.xiaomimimo.com/v1')}")
        print(f"[UltraQuant] Model: {config.get('mimo_model', 'mimo-v2.5-pro-ultraspeed')}")
        await engine.run_live()


if __name__ == "__main__":
    asyncio.run(main())
