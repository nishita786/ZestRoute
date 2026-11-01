"""Quick inspection helper for raw and processed ZestRoute datasets."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "orders.csv"
PROCESSED_PATH = ROOT / "data" / "processed" / "clean_orders.csv"


def inspect(path: Path, label: str) -> None:
    print("=" * 60)
    print(label)
    print("=" * 60)
    if not path.exists():
        print(f"File not found: {path}")
        return

    frame = pd.read_csv(path)
    print(f"Path: {path}")
    print(f"Shape: {frame.shape}")
    print("\nFIRST 5 ROWS")
    print(frame.head())
    print("\nCOLUMN NAMES")
    print(list(frame.columns))
    print("\nDTYPES")
    print(frame.dtypes)
    print("\nMISSING VALUES")
    print(frame.isnull().sum())
    print()


def main() -> None:
    inspect(RAW_PATH, "RAW ORDERS")
    inspect(PROCESSED_PATH, "PROCESSED ORDERS")


if __name__ == "__main__":
    main()
