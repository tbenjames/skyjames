"""
SkyJames - Professional Logging System
"""

import logging
import logging.handlers
import os
from datetime import datetime
import json

class ProfessionalLogger:
    def __init__(self, name="skyjames"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory
        os.makedirs("logs", exist_ok=True)
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            f"logs/{name}.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        
        # JSON formatter for structured logging
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "level": record.levelname,
                    "module": record.module,
                    "message": record.getMessage()
                }
                return json.dumps(log_entry)
        
        json_formatter = JSONFormatter()
        file_handler.setFormatter(json_formatter)
        console_handler.setFormatter(json_formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message, **kwargs):
        self.logger.info(message, extra=kwargs)
    
    def error(self, message, **kwargs):
        self.logger.error(message, extra=kwargs)
    
    def warning(self, message, **kwargs):
        self.logger.warning(message, extra=kwargs)
    
    def debug(self, message, **kwargs):
        self.logger.debug(message, extra=kwargs)

logger = ProfessionalLogger()

def log_api_call(endpoint, user, duration, status):
    logger.info(
        f"API Call: {endpoint}",
        extra={
            "user": user,
            "duration_ms": duration,
            "status": status
        }
    )
