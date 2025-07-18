#!/usr/bin/env python3
"""
Test script to verify the database viewer functionality
"""

import sqlite3
import os
import sys
import pytest
from pathlib import Path

# Adicionar src ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_database_connection():
    """Test database connection and table listing"""
    db_path = "data/db/esocial_20250609_003630.db"
    
    print(f"Testing database: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables found: {tables}")
        
        # Test each table
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"Table {table}: {count} records")
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            print(f"  Columns: {column_names}")
        
        conn.close()
        print("\n Database viewer functionality test PASSED!")
        return True
        
    except Exception as e:
        print(f" Database test FAILED: {e}")
        return False

if __name__ == "__main__":
    test_database_connection()
