import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional, Any

class ModuleDatabase:
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "data" / "zaiyan.db"
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                type TEXT,
                description TEXT,
                author TEXT,
                platform TEXT,
                options TEXT,
                last_used TIMESTAMP
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS exploits (
                id INTEGER PRIMARY KEY,
                cve TEXT,
                module_name TEXT,
                target TEXT,
                success BOOLEAN,
                timestamp TIMESTAMP
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS loot (
                id INTEGER PRIMARY KEY,
                session_id TEXT,
                type TEXT,
                data TEXT,
                timestamp TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_module(self, name: str, module: Any):
        """Register module in database"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        
        platform = json.dumps(getattr(module, "PLATFORM", ["generic"]))
        options = json.dumps(getattr(module, "options", {}))
        
        c.execute('''
            INSERT OR REPLACE INTO modules 
            (name, type, description, author, platform, options)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            name,
            getattr(module, "MODULE_TYPE", "unknown"),
            getattr(module, "DESCRIPTION", ""),
            getattr(module, "AUTHOR", "Anonymous-beta"),
            platform,
            options
        ))
        
        conn.commit()
        conn.close()
    
    def log_exploit(self, cve: str, module: str, target: str, success: bool):
        """Log exploit attempt"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO exploits (cve, module_name, target, success, timestamp)
            VALUES (?, ?, ?, ?, datetime('now'))
        ''', (cve, module, target, success))
        
        conn.commit()
        conn.close()
    
    def store_loot(self, session_id: str, loot_type: str, data: str):
        """Store harvested data"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO loot (session_id, type, data, timestamp)
            VALUES (?, ?, ?, datetime('now'))
        ''', (session_id, loot_type, data))
        
        conn.commit()
        conn.close()
    
    def get_modules_by_type(self, module_type: str) -> List[Dict[str, Any]]:
        """Get modules filtered by type"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        
        c.execute('''
            SELECT name, type, description, author, platform 
            FROM modules WHERE type = ?
        ''', (module_type,))
        
        results = []
        for row in c.fetchall():
            results.append({
                "name": row[0],
                "type": row[1],
                "description": row[2],
                "author": row[3],
                "platform": json.loads(row[4])
            })
        
        conn.close()
        return results
