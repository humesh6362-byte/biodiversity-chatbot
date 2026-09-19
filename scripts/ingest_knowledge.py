#!/usr/bin/env python
"""Convenience wrapper: `python scripts/ingest_knowledge.py`"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.knowledge.ingest import run

if __name__ == "__main__":
    run()
