"""
SkyJames - Production Monitoring & Alerting
"""

import psutil
import json
import time
import threading
from datetime import datetime
import requests
import os

class ProductionMonitor:
    def __init__(self, config_path="config/monitor_config.json"):
        self.config = self.load_config(config_path)
        self.metrics = {
            'cpu': [],
            'memory': [],
            'disk': [],
            'response_time': [],
            'error_rate': []
        }
        self.alerts = []
        self.running = False
        self.thread = None
    
    def load_config(self, path):
        """Load monitoring configuration"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return {
                'alert_thresholds': {
                    'cpu_high': 80,
                    'memory_high': 85,
                    'disk_high': 90,
                    'response_time_high': 1000,
                    'error_rate_high': 5
                },
                'check_interval': 10,  # seconds
                'alert_webhook': None
            }
    
    def start_monitoring(self):
        """Start monitoring in background"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print("✅ Production monitoring started")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Collect metrics
                cpu = psutil.cpu_percent()
                memory = psutil.virtual_memory().percent
                disk = psutil.disk_usage('/').percent
                
                self.metrics['cpu'].append(cpu)
                self.metrics['memory'].append(memory)
                self.metrics['disk'].append(disk)
                
                # Keep only last 1000 metrics
                for key in self.metrics:
                    if len(self.metrics[key]) > 1000:
                        self.metrics[key] = self.metrics[key][-1000:]
                
                # Check thresholds
                self._check_thresholds(cpu, memory, disk)
                
                # Send metrics to monitoring service
                self._send_metrics(cpu, memory, disk)
                
                time.sleep(self.config['check_interval'])
            except Exception as e:
                print(f"⚠️ Monitoring error: {e}")
    
    def _check_thresholds(self, cpu, memory, disk):
        """Check against thresholds and trigger alerts"""
        alerts = []
        
        if cpu > self.config['alert_thresholds']['cpu_high']:
            alerts.append(f"⚠️ High CPU usage: {cpu}%")
        
        if memory > self.config['alert_thresholds']['memory_high']:
            alerts.append(f"⚠️ High memory usage: {memory}%")
        
        if disk > self.config['alert_thresholds']['disk_high']:
            alerts.append(f"⚠️ High disk usage: {disk}%")
        
        for alert in alerts:
            self.alerts.append({
                'message': alert,
                'timestamp': datetime.now().isoformat(),
                'resolved': False
            })
            self._send_alert(alert)
    
    def _send_metrics(self, cpu, memory, disk):
        """Send metrics to monitoring service"""
        # Send to Prometheus
        try:
            # Implement Prometheus push gateway
            pass
        except:
            pass
        
        # Send to custom endpoint
        if self.config.get('metrics_endpoint'):
            try:
                requests.post(self.config['metrics_endpoint'], json={
                    'cpu': cpu,
                    'memory': memory,
                    'disk': disk,
                    'timestamp': datetime.now().isoformat()
                })
            except:
                pass
    
    def _send_alert(self, message):
        """Send alert via configured channels"""
        print(f"🚨 ALERT: {message}")
        
        # Email alert
        if self.config.get('email_alerts'):
            try:
                from src.email_reports import EmailReports
                email = EmailReports()
                email.send_report("Production Alert", message)
            except:
                pass
        
        # Webhook alert
        if self.config.get('alert_webhook'):
            try:
                requests.post(self.config['alert_webhook'], json={
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                })
            except:
                pass
    
    def get_status(self):
        """Get current status"""
        return {
            'metrics': {
                'cpu': self.metrics['cpu'][-1] if self.metrics['cpu'] else 0,
                'memory': self.metrics['memory'][-1] if self.metrics['memory'] else 0,
                'disk': self.metrics['disk'][-1] if self.metrics['disk'] else 0
            },
            'alerts': self.alerts[-10:],
            'total_alerts': len(self.alerts),
            'status': 'healthy' if len(self.alerts) == 0 else 'warning'
        }

# Initialize monitor
monitor = ProductionMonitor()
monitor.start_monitoring()
print("✅ Production monitor active")

# Create Grafana dashboard config
cat > grafana_dashboard.json << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "SkyJames Production Monitoring",
    "panels": [
      {
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {"expr": "skyjames_cpu_usage"}
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {"expr": "skyjames_memory_usage"}
        ]
      },
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {"expr": "skyjames_response_time"}
        ]
      },
      {
        "title": "Error Rate",
        "type": "stat",
        "targets": [
          {"expr": "skyjames_error_rate"}
        ]
      }
    ]
  }
}
