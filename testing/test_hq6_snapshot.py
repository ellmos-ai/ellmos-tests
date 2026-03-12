#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HQ6 Test 1: Snapshot erstellen
"""
import sys
from pathlib import Path

# BACH Strawberry laden
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "BACH_strawberry" / "system"))

from core.distribution import DistributionManager

# Root = BACH_strawberry/
root = Path(__file__).parent.parent.parent / "BACH_strawberry"
dm = DistributionManager(root)

print("Creating snapshot...")
try:
    snapshot_id = dm.create_snapshot("test_snapshot_hq6_runde27")
    print(f"✓ Snapshot created: {snapshot_id}")
except Exception as e:
    print(f"✗ FEHLER: {e}")
    import traceback
    traceback.print_exc()
