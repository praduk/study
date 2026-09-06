#!/usr/bin/env python3
"""Convenience launcher for Study."""

from pathlib import Path

from study_app.cli import main

if __name__ == "__main__":
    main(Path(__file__).resolve().parent)
