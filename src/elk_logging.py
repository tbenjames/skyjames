"""
SkyJames - ELK Stack Logging Integration
"""

import logging
import json
import sys
from datetime import datetime
from pythonjsonlogger import jsonlogger

class SkyJamesLogger:
    def __init__(self, service_name="skyjames"):
        self.service_name = service_name
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Setup JSON logger for ELK"""
        logger = logging.getLogger(self.service_name)
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # JSON formatter
        formatter = jsonlogger.JsonFormatter(
            fmt='%(asctime)s %(levelname)s %(service)s %(message)s'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_event(self, event_type, data, level='info'):
        """Log an event"""
        log_data = {
            'service': self.service_name,
            'event_type': event_type,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        if level == 'info':
            self.logger.info(json.dumps(log_data))
        elif level == 'warning':
            self.logger.warning(json.dumps(log_data))
        elif level == 'error':
            self.logger.error(json.dumps(log_data))
    
    def log_video_processed(self, video_path, metrics):
        """Log video processing event"""
        self.log_event('video_processed', {
            'video': video_path,
            'metrics': metrics
        })
    
    def log_detection_made(self, detections, fps):
        """Log detection event"""
        self.log_event('detection_made', {
            'count': len(detections),
            'fps': fps
        })
    
    def log_error(self, error, context=None):
        """Log error"""
        self.log_event('error', {
            'error': str(error),
            'context': context
        }, level='error')

# Example usage
logger = SkyJamesLogger()
logger.log_video_processed("test.mp4", {"fps": 26.7, "frames": 150})
