"""
SkyJames - Tableau Integration
"""

import json
import requests
from datetime import datetime

class TableauIntegration:
    def __init__(self, server_url=None):
        self.server_url = server_url
        self.access_token = None
        self.site_id = None
    
    def authenticate(self, username, password, site_id=''):
        """Authenticate with Tableau Server"""
        try:
            url = f"{self.server_url}/api/3.0/auth/signin"
            data = {
                'credentials': {
                    'name': username,
                    'password': password,
                    'site': {'contentUrl': site_id or ''}
                }
            }
            response = requests.post(url, json=data)
            if response.status_code == 200:
                self.access_token = response.headers.get('X-Tableau-Auth')
                self.site_id = response.json()['credentials']['site']['id']
                return True
        except:
            pass
        return False
    
    def create_data_source(self, name, data):
        """Create a data source in Tableau"""
        if not self.access_token:
            return False
        
        try:
            url = f"{self.server_url}/api/3.0/sites/{self.site_id}/datasources"
            headers = {'X-Tableau-Auth': self.access_token}
            # Convert data to Tableau format
            payload = {
                'datasource': {
                    'name': name,
                    'description': f"Created from SkyJames at {datetime.now().isoformat()}"
                }
            }
            response = requests.post(url, headers=headers, json=payload)
            return response.status_code == 201
        except:
            pass
        return False
    
    def update_data_source(self, datasource_id, data):
        """Update Tableau data source"""
        if not self.access_token:
            return False
        
        try:
            url = f"{self.server_url}/api/3.0/sites/{self.site_id}/datasources/{datasource_id}/data"
            headers = {'X-Tableau-Auth': self.access_token}
            response = requests.put(url, headers=headers, json={'data': data})
            return response.status_code == 200
        except:
            pass
        return False

# Global Tableau instance
tableau = TableauIntegration()
