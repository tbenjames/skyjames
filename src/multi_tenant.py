"""
SkyJames - Multi-Tenant System
"""

import json
import os
import uuid
from datetime import datetime

class TenantManager:
    def __init__(self, config_path="config/tenants.json"):
        self.config_path = config_path
        self._init_tenants()
    
    def _init_tenants(self):
        os.makedirs("config", exist_ok=True)
        if not os.path.exists(self.config_path):
            tenants = {
                "demo": {
                    "name": "Demo Tenant",
                    "api_key": "demo_key_123",
                    "created": datetime.now().isoformat(),
                    "limits": {
                        "max_videos": 100,
                        "max_users": 5,
                        "storage": "1GB"
                    },
                    "features": ["lane_detection", "object_detection"]
                }
            }
            with open(self.config_path, "w") as f:
                json.dump(tenants, f, indent=2)
    
    def get_tenant(self, api_key):
        with open(self.config_path, "r") as f:
            tenants = json.load(f)
        for tenant_id, tenant in tenants.items():
            if tenant.get("api_key") == api_key:
                return tenant_id, tenant
        return None, None
    
    def create_tenant(self, name, features=None, limits=None):
        tenant_id = str(uuid.uuid4())[:8]
        with open(self.config_path, "r") as f:
            tenants = json.load(f)
        
        tenants[tenant_id] = {
            "name": name,
            "api_key": f"{tenant_id}_key_{datetime.now().timestamp()}",
            "created": datetime.now().isoformat(),
            "limits": limits or {"max_videos": 100, "max_users": 5},
            "features": features or ["lane_detection"]
        }
        
        with open(self.config_path, "w") as f:
            json.dump(tenants, f, indent=2)
        
        return tenant_id
