"""
SkyJames - PowerBI Integration
"""

import json
import pandas as pd
from datetime import datetime
import requests

class PowerBIIntegration:
    def __init__(self, workspace_id=None, dataset_id=None):
        self.workspace_id = workspace_id
        self.dataset_id = dataset_id
        self.access_token = None
    
    def authenticate(self, client_id, client_secret, tenant_id):
        """Authenticate with PowerBI API"""
        try:
            url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
            data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'scope': 'https://analysis.windows.net/powerbi/api/.default',
                'grant_type': 'client_credentials'
            }
            response = requests.post(url, data=data)
            if response.status_code == 200:
                self.access_token = response.json()['access_token']
                return True
        except:
            pass
        return False
    
    def push_data(self, dataset_name, table_name, data):
        """Push data to PowerBI dataset"""
        if not self.access_token:
            return False
        
        try:
            url = f"https://api.powerbi.com/v1.0/myorg/datasets/{self.dataset_id}/tables/{table_name}/rows"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            response = requests.post(url, headers=headers, json={'rows': data})
            return response.status_code == 200
        except:
            return False
    
    def export_report(self, report_id, format='pdf'):
        """Export PowerBI report"""
        if not self.access_token:
            return None
        
        try:
            url = f"https://api.powerbi.com/v1.0/myorg/reports/{report_id}/export"
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.content
        except:
            pass
        return None

# Global PowerBI instance
powerbi = PowerBIIntegration()
