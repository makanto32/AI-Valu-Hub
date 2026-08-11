#!/usr/bin/env python3
"""Build medallion artifacts (bronze/silver/gold) from current API database records."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

from app.fabric_medallion import run_medallion_pipeline


if __name__ == "__main__":
    result = run_medallion_pipeline()
    print("Medallion pipeline generated:")
    for key, value in result.items():
        print(f"- {key}: {value}")
