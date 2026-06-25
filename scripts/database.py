"""
SkyJames - Database Integration
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

class SkyJamesDB:
    def __init__(self, db_path="data/skyjames.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                frame_number INTEGER,
                left_lane TEXT,
                right_lane TEXT,
                objects_detected INTEGER,
                safety_status BOOLEAN,
                processing_time REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_time DATETIME,
                total_frames INTEGER,
                avg_fps REAL,
                project TEXT DEFAULT 'SkyJames'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metric_name TEXT,
                metric_value REAL,
                session_id TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ SkyJames database initialized")
    
    def log_detection(self, frame_number, left_lane, right_lane, 
                     objects_detected, safety_status, processing_time):
        """Log a detection result"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO detections 
            (frame_number, left_lane, right_lane, objects_detected, 
             safety_status, processing_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (frame_number, json.dumps(left_lane), json.dumps(right_lane),
              objects_detected, safety_status, processing_time))
        
        conn.commit()
        conn.close()
    
    def start_session(self, session_id):
        """Start a new session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions (session_id, start_time, project)
            VALUES (?, CURRENT_TIMESTAMP, 'SkyJames')
        ''', (session_id,))
        
        conn.commit()
        conn.close()
        return session_id
    
    def end_session(self, session_id, total_frames, avg_fps):
        """End a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE sessions 
            SET end_time = CURRENT_TIMESTAMP,
                total_frames = ?,
                avg_fps = ?
            WHERE session_id = ?
        ''', (total_frames, avg_fps, session_id))
        
        conn.commit()
        conn.close()
    
    def get_stats(self, days=7):
        """Get statistics for the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_detections,
                AVG(processing_time) as avg_time,
                SUM(CASE WHEN safety_status = 1 THEN 1 ELSE 0 END) as safe_frames,
                AVG(objects_detected) as avg_objects
            FROM detections
            WHERE timestamp > datetime('now', '-' || ? || ' days')
        ''', (days,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'total_detections': result[0],
                'avg_processing_time': result[1],
                'safe_frames': result[2],
                'avg_objects': result[3]
            }
        return {}

if __name__ == "__main__":
    # Test database
    db = SkyJamesDB()
    db.start_session("skyjames_test_001")
    db.log_detection(0, [100, 200], [300, 400], 3, True, 0.05)
    db.end_session("skyjames_test_001", 100, 25.5)
    print("Stats:", db.get_stats())
