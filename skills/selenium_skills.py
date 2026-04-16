import time
import os
import requests
from bs4 import BeautifulSoup
from langchain_community.tools import DuckDuckGoSearchRun
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

class SeleniumSkills:
    def __init__(self):
        self.driver: Optional[webdriver.Edge] = None
        self._is_initialized = False

    def _ensure_browser(self):
        if not self._is_initialized:
            options = webdriver.EdgeOptions()
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Use persistent context to store session/cookies
            user_data_dir = os.path.join(os.getcwd(), "data", "browser_profile_selenium")
            os.makedirs(user_data_dir, exist_ok=True)
            options.add_argument(f"user-data-dir={user_data_dir}")
            
            # Hide webdriver flag
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            try:
                self.driver = webdriver.Edge(options=options)
                self.driver.set_window_size(1280, 720)
                
                # Execute CDP command to block webdriver detection
                self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                  "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                      get: () => undefined
                    })
                  """
                })
                self._is_initialized = True
            except Exception as e:
                raise RuntimeError(f"Failed to initialize Selenium Edge driver: {e}")

    def browser_open(self, url: str):
        """Navigate the browser to a specific URL."""
        self._ensure_browser()
        if not url.startswith('http'):
            url = 'https://' + url
        try:
            self.driver.get(url)
            return f"Opened {url}"
        except WebDriverException as e:
            return f"Failed to open {url}: {e}"

    def browser_click(self, selector: str):
        """Click a specific element on the webpage."""
        self._ensure_browser()
        try:
            # Assume CSS Selector
            element = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            element.click()
            return "Clicked."
        except TimeoutException:
            return f"Timeout: Element '{selector}' not clickable."
        except Exception as e:
            return f"Click Error: {e}"

    def browser_type(self, selector: str, text: str):
        """Type text into a specific element."""
        self._ensure_browser()
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            element.clear()
            element.send_keys(text)
            return f"Typed {text} into '{selector}'"
        except TimeoutException:
            return f"Timeout: Element '{selector}' not found."
        except Exception as e:
            return f"Type Error: {e}"

    def browser_get_text(self, selector: str):
        """Get the text content of a specific element."""
        self._ensure_browser()
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element.text
        except TimeoutException:
            return f"Timeout: Element '{selector}' not found."
        except Exception as e:
            return f"Get Text Error: {e}"

    def browser_get_url(self):
        """Get the current browser URL."""
        self._ensure_browser()
        return self.driver.current_url

    def browser_get_all_text(self):
        """Get the text content of the entire webpage (truncated)."""
        self._ensure_browser()
        try:
            body = self.driver.find_element(By.TAG_NAME, 'body')
            return body.text[:2000]
        except Exception as e:
            return f"Error grabbing text: {e}"

    def web_search(self, query: str):
        """Search the web for information using DuckDuckGo."""
        search = DuckDuckGoSearchRun()
        return search.run(query)

    def google_search_nav(self, query: str):
        """Search Google and open results in the browser."""
        self._ensure_browser()
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        self.driver.get(url)
        return f"Navigated to search for {query}"

    def close_browser(self):
        try:
            if self.driver:
                self.driver.quit()
            self._is_initialized = False
            return "Closed."
        except Exception as e:
            return str(e)
