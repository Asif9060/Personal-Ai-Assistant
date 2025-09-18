from __future__ import annotations

import webbrowser
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class WebSkill:
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None

    def ensure_driver(self) -> webdriver.Chrome:
        if self.driver is None:
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        return self.driver

    def search(self, query: str) -> str:
        if not query:
            return "What should I search for?"
        try:
            driver = self.ensure_driver()
            driver.get("https://www.google.com")
            box = driver.find_element(By.NAME, "q")
            box.clear()
            box.send_keys(query)
            box.submit()
            return f"Searching the web for {query}."
        except Exception:
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return f"Opened browser for {query}."

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
