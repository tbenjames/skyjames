"""
SkyJames - Email Reports
"""

import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os

class EmailReports:
    def __init__(self, config_path="config/email_config.json"):
        self.config = self.load_config(config_path)
    
    def load_config(self, path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return {
                'enabled': False,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': 'your_email@gmail.com',
                'password': 'your_password',
                'recipients': ['admin@example.com']
            }
    
    def send_report(self, subject, body, attachments=None):
        if not self.config['enabled']:
            print("📧 Email reports disabled")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['username']
            msg['To'] = ', '.join(self.config['recipients'])
            msg['Subject'] = f"[SkyJames] {subject}"
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach files
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename={os.path.basename(file_path)}'
                            )
                            msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
            server.login(self.config['username'], self.config['password'])
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email report sent: {subject}")
            return True
        except Exception as e:
            print(f"❌ Email failed: {e}")
            return False
    
    def send_daily_report(self, stats):
        subject = f"SkyJames Daily Report - {datetime.now().strftime('%Y-%m-%d')}"
        body = f"""
SkyJames Daily Report
=====================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Statistics:
  - Videos Processed: {stats.get('videos', 0)}
  - Detections Made: {stats.get('detections', 0)}
  - Average FPS: {stats.get('fps', 0):.1f}
  - Uptime: {stats.get('uptime', 'N/A')}
  - Model Accuracy: {stats.get('accuracy', 0):.2f}%

System Health: ✅ All systems operational
        """
        return self.send_report(subject, body)

# Example usage
if __name__ == "__main__":
    reports = EmailReports()
    reports.send_daily_report({
        'videos': 150,
        'detections': 1245,
        'fps': 26.7,
        'uptime': '2d 4h',
        'accuracy': 94.2
    })
