"""
build_hydrogen_apparatus.py — Alias wrapper for build_hydrogen_evolution.py
"""
import sys
from pathlib import Path

# Add directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_hydrogen_evolution import main

if __name__ == '__main__':
    main()
