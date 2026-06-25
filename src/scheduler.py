"""
SkyJames - Task Scheduler
"""

import schedule
import time
import threading
from datetime import datetime
import subprocess

class TaskScheduler:
    def __init__(self):
        self.tasks = []
        self.running = False
        self.thread = None
    
    def add_task(self, func, interval, unit='minutes'):
        """Add a scheduled task"""
        if unit == 'minutes':
            schedule.every(interval).minutes.do(func)
        elif unit == 'hours':
            schedule.every(interval).hours.do(func)
        elif unit == 'days':
            schedule.every(interval).days.do(func)
        elif unit == 'weeks':
            schedule.every(interval).weeks.do(func)
        else:
            schedule.every().day.at(interval).do(func)
        
        self.tasks.append({'func': func, 'interval': interval, 'unit': unit})
        print(f"✅ Task added: {func.__name__} every {interval} {unit}")
    
    def start(self):
        """Start the scheduler"""
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print("🚀 Task scheduler started")
    
    def _run(self):
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("🛑 Task scheduler stopped")
    
    def list_tasks(self):
        print("\n📋 Scheduled Tasks:")
        for i, task in enumerate(self.tasks):
            print(f"  {i+1}. {task['func'].__name__} every {task['interval']} {task['unit']}")

# Example tasks
def process_videos_task():
    print(f"[{datetime.now()}] Processing new videos...")
    subprocess.run(["python", "skyjames.py", "--mode", "video", "--video", "data/input/latest.mp4"])

def generate_report_task():
    print(f"[{datetime.now()}] Generating daily report...")
    subprocess.run(["python", "-c", "from src.email_reports import EmailReports; EmailReports().send_daily_report({})"])

def retrain_model_task():
    print(f"[{datetime.now()}] Retraining model...")
    subprocess.run(["python", "scripts/train_cpu.py"])

if __name__ == "__main__":
    scheduler = TaskScheduler()
    
    # Add tasks
    scheduler.add_task(process_videos_task, 30, 'minutes')
    scheduler.add_task(generate_report_task, 1, 'hours')
    scheduler.add_task(retrain_model_task, 7, 'days')
    
    scheduler.list_tasks()
    scheduler.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()
