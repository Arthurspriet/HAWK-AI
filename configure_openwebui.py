#!/usr/bin/env python3
"""
Configure HAWK-AI in Open WebUI database directly
"""
import sys
import sqlite3
import json
from pathlib import Path

# Open WebUI database path
DB_PATH = Path.home() / "HAWK-AI/open-webui/backend/data/webui.db"

# HAWK-AI configuration
HAWK_AI_CONFIG = {
    "ENABLE_OPENAI_API": True,
    "OPENAI_API_BASE_URLS": ["http://127.0.0.1:8000/v1"],
    "OPENAI_API_KEYS": ["hawk-ai-key"],
    "OPENAI_API_CONFIGS": {
        "0": {
            "name": "HAWK-AI",
            "prefix_id": "hawk",
            "enable": True
        }
    }
}

def main():
    if not DB_PATH.exists():
        print(f"❌ Database not found at: {DB_PATH}")
        print("Please check the Open WebUI installation path.")
        return 1
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if config table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='config'")
        if not cursor.fetchone():
            print("❌ Config table not found in database")
            return 1
        
        # Get existing config
        cursor.execute("SELECT id, data FROM config LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            config_id, data_str = result
            data = json.loads(data_str) if data_str else {}
            print(f"✓ Found existing config (ID: {config_id})")
        else:
            data = {}
            config_id = None
            print("✓ No existing config, will create new")
        
        # Update with HAWK-AI configuration
        data.update(HAWK_AI_CONFIG)
        
        # Save back to database
        data_json = json.dumps(data)
        
        if config_id:
            cursor.execute("UPDATE config SET data = ? WHERE id = ?", (data_json, config_id))
        else:
            cursor.execute("INSERT INTO config (data, version) VALUES (?, 0)", (data_json,))
        
        conn.commit()
        conn.close()
        
        print("\n✅ HAWK-AI configuration saved successfully!")
        print("\n📋 Configuration:")
        print(f"   URL: {HAWK_AI_CONFIG['OPENAI_API_BASE_URLS'][0]}")
        print(f"   Key: {HAWK_AI_CONFIG['OPENAI_API_KEYS'][0]}")
        print("\n🔄 Please restart Open WebUI backend:")
        print("   1. Stop the backend (Ctrl+C in the terminal)")
        print("   2. Start it again")
        print("   3. Refresh your browser")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

