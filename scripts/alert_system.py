"""
SkyJames - Alert System
"""

import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime

class SkyJamesAlert:
    def __init__(self, config_path="config/skyjames_alerts.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.alert_history = []
        self.system_name = "SkyJames"
    
    def _load_config(self):
        """Load alert configuration"""
        default_config = {
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
            'thresholds': {
                'safety_violation': 5,
                'detection_failure': 10,
                'fps_below': 15
            }
        }
        
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"📝 SkyJames alert config created: {self.config_path}")
            return default_config
    
    def check_alerts(self, metrics):
        """Check for alerts based on metrics"""
        alerts = []
        
        if metrics.get('safety_violations', 0) > self.config['thresholds']['safety_violation']:
            alerts.append({
                'type': 'safety',
                'message': f"🚨 SkyJames Safety Alert: {metrics['safety_violations']} violations",
                'severity': 'critical'
            })
        
        if metrics.get('detection_failures', 0) > self.config['thresholds']['detection_failure']:
            alerts.append({
                'type': 'detection',
                'message': f"⚠️ SkyJames Detection Alert: {metrics['detection_failures']} failures",
                'severity': 'warning'
            })
        
        if metrics.get('fps', 30) < self.config['thresholds']['fps_below']:
            alerts.append({
                'type': 'performance',
                'message': f"⚠️ SkyJames Performance Alert: Low FPS ({metrics['fps']:.1f})",
                'severity': 'warning'
            })
        
        for alert in alerts:
            self.send_alert(alert)
        
        return alerts
    
    def send_alert(self, alert):
        """Send an alert via configured channels"""
        print(f"🔔 SkyJames ALERT: {alert['message']}")
        
        alert['timestamp'] = datetime.now().isoformat()
        alert['system'] = self.system_name
        self.alert_history.append(alert)
        
        if self.config['email']['enabled']:
            self._send_email_alert(alert)
        
        if self.config['slack']['enabled']:
            self._send_slack_alert(alert)
    
    def _send_email_alert(self, alert):
        """Send email alert"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['username']
            msg['To'] = ', '.join(self.config['email']['recipients'])
            msg['Subject'] = f"[SkyJames] {alert['type'].upper()} Alert"
            
            body = f"""
            SkyJames Alert System
            ====================
            
            Alert Type: {alert['type']}
            Severity: {alert['severity']}
            Message: {alert['message']}
            Time: {alert['timestamp']}
            
            This is an automated alert from SkyJames.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.config['email']['smtp_server'], 
                                 self.config['email']['smtp_port'])
            server.starttls()
            server.login(self.config['email']['username'], 
                        self.config['email']['password'])
            server.send_message(msg)
            server.quit()
            
            print("📧 SkyJames email alert sent")
        except Exception as e:
            print(f"❌ SkyJames email alert failed: {e}")
    
    def _send_slack_alert(self, alert):
        """Send Slack alert"""
        try:
            import requests
            
            message = {
                'text': f"🚨 *SkyJames {alert['type'].upper()} Alert*\n{alert['message']}",
                'attachments': [{
                    'color': 'danger' if alert['severity'] == 'critical' else 'warning',
                    'fields': [
                        {'title': 'Type', 'value': alert['type'], 'short': True},
                        {'title': 'Severity', 'value': alert['severity'], 'short': True},
                        {'title': 'Time', 'value': alert['timestamp'], 'short': False}
                    ]
                }]
            }
            
            response = requests.post(self.config['slack']['webhook_url'], json=message)
            if response.status_code == 200:
                print("💬 SkyJames Slack alert sent")
            else:
                print(f"❌ SkyJames Slack alert failed: {response.status_code}")
        except Exception as e:
            print(f"❌ SkyJames Slack alert failed: {e}")
    
    def get_history(self, limit=10):
        """Get recent alert history"""
        return self.alert_history[-limit:]

if __name__ == "__main__":
    alert_system = SkyJamesAlert()
    metrics = {'safety_violations': 7, 'detection_failures': 12, 'fps': 12.5}
    alerts = alert_system.check_alerts(metrics)
    print(f"SkyJames alerts triggered: {len(alerts)}")
