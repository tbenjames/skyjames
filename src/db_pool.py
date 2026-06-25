"""
SkyJames - Database Connection Pooling
"""

import sqlite3
import threading
from contextlib import contextmanager
from queue import Queue

class ConnectionPool:
    def __init__(self, db_path="data/skyjames.db", max_connections=10):
        self.db_path = db_path
        self.max_connections = max_connections
        self.pool = Queue(maxsize=max_connections)
        self.lock = threading.Lock()
        self._created = 0
        
        # Initialize pool
        for _ in range(max_connections):
            self._create_connection()
    
    def _create_connection(self):
        """Create a new database connection"""
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self.pool.put(conn)
            self._created += 1
            return conn
        except Exception as e:
            print(f"Error creating connection: {e}")
            return None
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool"""
        conn = self.pool.get()
        try:
            yield conn
        finally:
            self.pool.put(conn)
    
    def get_stats(self):
        """Get pool statistics"""
        return {
            'total_connections': self._created,
            'available': self.pool.qsize(),
            'max_connections': self.max_connections
        }

# Global connection pool
db_pool = ConnectionPool()
