#!/usr/bin/env python3
"""
Simple seed script - Run this to seed test users
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.seed_users import create_seed_users, check_existing_users

if __name__ == "__main__":
    print("🌱 Seeding test users...")
    create_seed_users()
    print("\n✅ Done!")
