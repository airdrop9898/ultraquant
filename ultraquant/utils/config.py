"""Configuration loader — .env file + environment variables."""

import os
from pathlib import Path


def load_config(env_path: str = ".env") -> dict:
    config = {}
    env_file = Path(env_path)
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip().lower()] = value.strip().strip('"').strip("'")

    env_map = {
        "MIMO_API_KEY": "mimo_api_key",
        "MIMO_BASE_URL": "mimo_base_url",
        "MIMO_MODEL": "mimo_model",
        "TRADING_MODE": "trading_mode",
        "RISK_MAX_POSITION_PCT": "risk_max_position_pct",
        "RISK_MAX_DRAWDOWN_PCT": "risk_max_drawdown_pct",
    }
    for env_key, cfg_key in env_map.items():
        val = os.environ.get(env_key)
        if val:
            config[cfg_key] = val

    return config
