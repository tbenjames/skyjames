"""
SkyJames - Advanced Notification System
"""

import json
import os
from datetime import datetime

# Try to import optional dependencies
try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

class NotificationSystem:
    def __init__(self, config_path="config/notifications.json"):
        self.config = self._load_config(config_path)
        self.alerts = []
    
    def _load_config(self, path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return {
                'email': {
                    'enabled': False,
                    'smtp_server': 'smtp.gmail.com',
                    'smtp_port': 587,
                    'username': 'your_email@gmail.com',
                    'password': 'your_password',
                    'recipients': ['admin@example.com']
                },
                'slack': {
                    'enabled': False,
                    'webhook_url': ''
                },
                'telegram': {
                    'enabled': False,
                    'bot_token': '',
                    'chat_id': ''
                }
            }
    
    def send_alert(self, title, message, severity='info'):
        """Send alert through all enabled channels"""
        alert = {
            'title': title,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        }
        self.alerts.append(alert)
        
        # Send through enabled channels
        if self.config['email']['enabled'] and EMAIL_AVAILABLE:
            self._send_email(alert)
        if self.config['slack']['enabled'] and REQUESTS_AVAILABLE:
            self._send_slack(alert)
        if self.config['telegram']['enabled'] and REQUESTS_AVAILABLE:
            self._send_telegram(alert)
        
        # Always print to console
        print(f"🔔 ALERT [{severity}]: {title} - {message}")
    
    def _send_email(self, alert):
        """Send email notification"""
        try:
            if not EMAIL_AVAILABLE:
                print("⚠️ Email module not available")
                return False
            
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['username']
            msg['To'] = ', '.join(self.config['email']['recipients'])
            msg['Subject'] = f"[SkyJames] {alert['title']}"
            
            body = f"""
            Alert: {alert['title']}
            Severity: {alert['severity']}
            Message: {alert['message']}
            Time: {alert['timestamp']}
            """
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.config['email']['smtp_server'], self.config['email']['smtp_port'])
            server.starttls()
            server.login(self.config['email']['username'], self.config['email']['password'])
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Email failed: {e}")
            return False
    
    def _send_slack(self, alert):
        """Send Slack notification"""
        try:
            if not REQUESTS_AVAILABLE:
                print("⚠️ Requests module not available for Slack")
                return False
            
            message = {
                'text': f"*🚀 SkyJames Alert*\n*{alert['title']}*\n{alert['message']}\nSeverity: {alert['severity']}"
            }
            response = requests.post(self.config['slack']['webhook_url'], json=message)
            return response.status_code == 200
        except:
            return False
    
    def _send_telegram(self, alert):
        """Send Telegram notification"""
        try:
            if not REQUESTS_AVAILABLE:
                print("⚠️ Requests module not available for Telegram")
                return False
            
            url = f"https://api.telegram.org/bot{self.config['telegram']['bot_token']}/sendMessage"
            message = f"🚀 *SkyJames Alert*\n*{alert['title']}*\n{alert['message']}\nSeverity: {alert['severity']}"
            payload = {
                'chat_id': self.config['telegram']['chat_id'],
                'text': message,
                'parse_mode': 'Markdown'
            }
            response = requests.post(url, json=payload)
            return response.status_code == 200
        except:
            return False
