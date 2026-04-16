import time
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
import os
import requests
from bs4 import BeautifulSoup
from langchain_community.tools import DuckDuckGoSearchRun
from typing import Optional, Dict, List, Any

class BrowserSkills:
    # Consolidated Browser skills: Playwright automation, Web extraction, and Web Search.
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._is_initialized = False
    
    def _ensure_browser(self):
        if not self._is_initialized:
            self.playwright = sync_playwright().start()
            
            # User provided specific Edge path
            edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
            user_data_dir = os.path.join(os.getcwd(), "data", "browser_profile")
            os.makedirs(user_data_dir, exist_ok=True)

            launch_kwargs = {
                "headless": False,
                "channel": "msedge",
                # "viewport": {'width': 1280, 'height': 720},
                "args": [
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox"
                    # "--disable-infobars",
                    # "--disable-dev-shm-usage"
                ]
            }

            # Use persistent context to store session/cookies and avoid verification prompts
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                **launch_kwargs
            )
            
            # Inject script to hide webdriver flag
            self.context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
            self._is_initialized = True

    def browser_open(self, url: str):
        """Navigate the browser to a specific URL."""
        self._ensure_browser()
        self.page.goto(url, wait_until='domcontentloaded')
        return f"Opened {url}"

    def browser_click(self, selector: str):
        """Click a specific element on the webpage."""
        self._ensure_browser()
        self.page.locator(selector).click(timeout=5000)
        return "Clicked."

    def browser_type(self, selector: str, text: str):
        """Type text into a specific element."""
        self._ensure_browser()
        self.page.locator(selector).fill(text, timeout=5000)
        return f"Typed {text}"

    def browser_get_text(self, selector: str):
        """Get the text content of a specific element."""
        self._ensure_browser()
        return self.page.locator(selector).inner_text(timeout=5000)

    def browser_get_url(self):
        """Get the current browser URL."""
        self._ensure_browser()
        return self.page.url

    def browser_get_all_text(self):
        """Get the text content of the entire webpage (truncated)."""
        self._ensure_browser()
        return self.page.inner_text('body')[:2000]

    def browser_nav(self, action: str, url: str = None, **kwargs):
        """Deprecated: Use specific browser methods."""
        action = action.lower().strip()
        self._ensure_browser()
        if action == 'open' and url: return self.browser_open(url)
        if action == 'back': self.page.go_back(); return "Back."
        if action == 'reload': self.page.reload(); return "Reloaded."
        if action == 'close': self.close_browser(); return "Closed."
        if action == 'screenshot':
            path = kwargs.get('path', f"screenshots/browser_{int(time.time())}.png")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.page.screenshot(path=path)
            return f"Browser screenshot saved to {path}"
        return "Invalid action."

    def browser_interact(self, action: str, selector: str, text: str = None, **kwargs):
        """Deprecated: Use browser_click or browser_type."""
        action = action.lower().strip()
        if action == 'click': return self.browser_click(selector)
        if action == 'type': return self.browser_type(selector, text)
        return "Invalid action."

    def browser_inspect(self, action: str, selector: str = None):
        """Deprecated: Use specific browser inspection methods."""
        action = action.lower().strip()
        if action == 'url': return self.browser_get_url()
        if action == 'all_text': return self.browser_get_all_text()
        if action == 'text': return self.browser_get_text(selector)
        return "Invalid action."

    def web_search(self, query: str):
        """Search the web for information using DuckDuckGo."""
        search = DuckDuckGoSearchRun()
        return search.run(query)

    def google_search_nav(self, query: str):
        """Search Google and open results in the browser."""
        self._ensure_browser()
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        self.page.goto(url)
        return f"Navigated to search for {query}"

    def web_ops(self, query: str, mode: str = "search"):
        """Deprecated: Use web_search or google_search_nav."""
        if mode == "search": return self.web_search(query)
        if mode == "nav": return self.google_search_nav(query)
        return "Invalid mode."

    def close_browser(self):
        try:
            if self.page: self.page.close()
            if self.context: self.context.close()
            if self.browser: self.browser.close()
            if self.playwright: self.playwright.stop()
            self._is_initialized = False
            return "Closed."
        except Exception as e: return str(e)

    @staticmethod
    def read_url(url: str):
        """Simplified textual extraction via requests/bs4 (fast/lightweight)."""
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
                tag.decompose()
            text = '\n'.join([p.strip() for p in soup.get_text().splitlines() if p.strip()]) 
            return text[:4000]
        except Exception as e: return str(e)
