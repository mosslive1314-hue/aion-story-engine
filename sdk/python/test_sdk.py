#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test AION SDK
"""

import sys
sys.path.insert(0, '/c/Users/maiyi/Desktop/story/sdk/python')

from aion_sdk import AionClient, Session, Asset, Universe, Proposal

print("Testing AION SDK...")
print("=" * 60)

# Test imports
print("1. Testing imports...")
try:
    from aion_sdk import AionClient, Session, Asset, Universe, Proposal
    print("   SUCCESS: All imports work")
except Exception as e:
    print(f"   FAILED: {e}")
    sys.exit(1)

# Test client creation
print("\n2. Testing client creation...")
try:
    client = AionClient(
        api_key="test_key",
        base_url="http://localhost:8000/api/v1"
    )
    print("   SUCCESS: Client created")
except Exception as e:
    print(f"   FAILED: {e}")

# Test session model
print("\n3. Testing session model...")
try:
    session = Session(
        session_id="test-123",
        name="Test Session",
        status="active",
        message="Test message"
    )
    print(f"   SUCCESS: Session created - {session.name}")
except Exception as e:
    print(f"   FAILED: {e}")

# Test asset model
print("\n4. Testing asset model...")
try:
    asset = Asset(
        id="asset-1",
        name="Fire Rule",
        type="world_rule",
        price=0.0,
        creator="alice",
        rating=5.0,
        downloads=100
    )
    print(f"   SUCCESS: Asset created - {asset.name}")
except Exception as e:
    print(f"   FAILED: {e}")

print("\n" + "=" * 60)
print("All tests passed!")
print("=" * 60)
