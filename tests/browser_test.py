"""
Automated browser tests for SkyJames Dashboard
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SkyJamesBrowserTest:
    def __init__(self):
        self.driver = webdriver.Chrome()  # or Firefox()
        self.base_url = "http://localhost:8501"
    
    def test_dashboard_load(self):
        self.driver.get(self.base_url)
        time.sleep(2)
        assert "SkyJames" in self.driver.title
    
    def test_navigation(self):
        # Test navigation buttons
        buttons = ["Home", "Lane", "Sports", "Gallery", "Perf", "Settings"]
        for btn in buttons:
            try:
                element = self.driver.find_element(By.LINK_TEXT, btn)
                element.click()
                time.sleep(1)
                print(f"✅ {btn} navigation works")
            except:
                print(f"❌ {btn} navigation failed")
    
    def cleanup(self):
        self.driver.quit()

if __name__ == "__main__":
    test = SkyJamesBrowserTest()
    test.test_dashboard_load()
    test.test_navigation()
    test.cleanup()
