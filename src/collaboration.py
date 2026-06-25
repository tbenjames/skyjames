"""
SkyJames - Real-time Collaboration (Simplified)
"""

import json
import time
from datetime import datetime
import threading

class CollaborationManager:
    def __init__(self):
        self.rooms = {}
        self.participants = {}
        self.messages = []
        self.running = False
    
    def create_room(self, room_id):
        """Create a collaboration room"""
        if room_id not in self.rooms:
            self.rooms[room_id] = {
                'created': datetime.now().isoformat(),
                'participants': [],
                'messages': []
            }
            print(f"📁 Room created: {room_id}")
        return self.rooms[room_id]
    
    def join_room(self, room_id, user_name):
        """Join a collaboration room"""
        if room_id not in self.rooms:
            self.create_room(room_id)
        
        if user_name not in self.rooms[room_id]['participants']:
            self.rooms[room_id]['participants'].append(user_name)
            print(f"👤 {user_name} joined room: {room_id}")
        
        return self.rooms[room_id]
    
    def leave_room(self, room_id, user_name):
        """Leave a collaboration room"""
        if room_id in self.rooms:
            if user_name in self.rooms[room_id]['participants']:
                self.rooms[room_id]['participants'].remove(user_name)
                print(f"👤 {user_name} left room: {room_id}")
    
    def send_message(self, room_id, user_name, message):
        """Send a message to a room"""
        if room_id in self.rooms:
            msg = {
                'user': user_name,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            self.rooms[room_id]['messages'].append(msg)
            print(f"💬 {user_name}: {message}")
            return msg
        return None
    
    def get_messages(self, room_id, limit=50):
        """Get messages from a room"""
        if room_id in self.rooms:
            return self.rooms[room_id]['messages'][-limit:]
        return []
    
    def get_participants(self, room_id):
        """Get participants in a room"""
        if room_id in self.rooms:
            return self.rooms[room_id]['participants']
        return []
    
    def get_rooms(self):
        """Get all rooms"""
        return list(self.rooms.keys())
    
    def get_stats(self):
        """Get collaboration stats"""
        return {
            'total_rooms': len(self.rooms),
            'total_participants': sum(len(r['participants']) for r in self.rooms.values()),
            'rooms': self.get_rooms()
        }

# Global collaboration manager
collab_manager = CollaborationManager()

# Test function
def test_collaboration():
    print("🚀 Testing Collaboration...")
    
    # Create rooms
    collab_manager.create_room("project_alpha")
    collab_manager.create_room("project_beta")
    
    # Join rooms
    collab_manager.join_room("project_alpha", "Alice")
    collab_manager.join_room("project_alpha", "Bob")
    collab_manager.join_room("project_beta", "Charlie")
    
    # Send messages
    collab_manager.send_message("project_alpha", "Alice", "Hello everyone!")
    collab_manager.send_message("project_alpha", "Bob", "Hi Alice!")
    collab_manager.send_message("project_beta", "Charlie", "Working on project beta")
    
    # Get stats
    stats = collab_manager.get_stats()
    print("\n📊 Collaboration Stats:")
    print(f"  Total Rooms: {stats['total_rooms']}")
    print(f"  Total Participants: {stats['total_participants']}")
    print(f"  Rooms: {stats['rooms']}")
    
    # Get messages
    print("\n💬 Messages in project_alpha:")
    for msg in collab_manager.get_messages("project_alpha"):
        print(f"  {msg['user']}: {msg['message']} ({msg['timestamp']})")
    
    return collab_manager

if __name__ == "__main__":
    test_collaboration()
