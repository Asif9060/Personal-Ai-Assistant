"""
Voice-Controlled Browser System for JARVIS

This module provides complete voice control over web browsers including:
- Opening browser
- Searching on Google
- Navigation (back, forward, refresh)
- Bookmarking websites
- Tab management
- Page interaction
"""

import time
import re
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
import os


class VoiceBrowser:
    """Voice-controlled browser interface for JARVIS"""

    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.is_active = False
        self.current_url = ""
        self.search_engine = "https://www.google.com"

    def open_browser(self) -> bool:
        """Open the default browser with voice control capabilities"""
        try:
            if self.driver and self.is_active:
                print("[BROWSER] Browser is already open")
                return True

            print("[BROWSER] Opening browser...")

            # Chrome options for better automation
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(
                "--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option(
                "excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option(
                'useAutomationExtension', False)

            # Use webdriver manager for automatic driver management
            service = Service(ChromeDriverManager().install())

            self.driver = webdriver.Chrome(
                service=service, options=chrome_options)
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # Open Google as default page
            self.driver.get(self.search_engine)
            self.current_url = self.search_engine
            self.is_active = True

            print("[BROWSER] Browser opened successfully")
            return True

        except Exception as e:
            print(f"[BROWSER] Failed to open browser: {e}")
            return False

    def close_browser(self) -> bool:
        """Close the browser"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.is_active = False
                print("[BROWSER] Browser closed")
                return True
            return False
        except Exception as e:
            print(f"[BROWSER] Error closing browser: {e}")
            return False

    def search(self, query: str) -> bool:
        """Search for something on Google"""
        try:
            if not self._ensure_browser_active():
                return False

            print(f"[BROWSER] Searching for: {query}")

            # If not on Google, navigate to Google first
            if "google.com" not in self.driver.current_url:
                self.driver.get(self.search_engine)
                time.sleep(2)

            # Find search box and enter query
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )

            # Clear previous search and enter new query
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)

            time.sleep(2)
            self.current_url = self.driver.current_url
            print(f"[BROWSER] Search completed for: {query}")
            return True

        except Exception as e:
            print(f"[BROWSER] Search failed: {e}")
            return False

    def navigate_to(self, url: str) -> bool:
        """Navigate to a specific URL"""
        try:
            if not self._ensure_browser_active():
                return False

            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            print(f"[BROWSER] Navigating to: {url}")
            self.driver.get(url)
            time.sleep(2)
            self.current_url = self.driver.current_url
            print(f"[BROWSER] Navigation completed")
            return True

        except Exception as e:
            print(f"[BROWSER] Navigation failed: {e}")
            return False

    def go_back(self) -> bool:
        """Go back to previous page"""
        try:
            if not self._ensure_browser_active():
                return False

            self.driver.back()
            time.sleep(1)
            self.current_url = self.driver.current_url
            print("[BROWSER] Navigated back")
            return True

        except Exception as e:
            print(f"[BROWSER] Go back failed: {e}")
            return False

    def go_forward(self) -> bool:
        """Go forward to next page"""
        try:
            if not self._ensure_browser_active():
                return False

            self.driver.forward()
            time.sleep(1)
            self.current_url = self.driver.current_url
            print("[BROWSER] Navigated forward")
            return True

        except Exception as e:
            print(f"[BROWSER] Go forward failed: {e}")
            return False

    def refresh_page(self) -> bool:
        """Refresh the current page"""
        try:
            if not self._ensure_browser_active():
                return False

            self.driver.refresh()
            time.sleep(2)
            print("[BROWSER] Page refreshed")
            return True

        except Exception as e:
            print(f"[BROWSER] Refresh failed: {e}")
            return False

    def bookmark_page(self) -> bool:
        """Add current page to bookmarks using Ctrl+D"""
        try:
            if not self._ensure_browser_active():
                return False

            # Use Ctrl+D to bookmark
            webdriver.ActionChains(self.driver).key_down(
                Keys.CONTROL).send_keys('d').key_up(Keys.CONTROL).perform()
            time.sleep(1)

            # Try to press Enter to confirm bookmark (works in most browsers)
            try:
                webdriver.ActionChains(self.driver).send_keys(
                    Keys.RETURN).perform()
            except:
                pass

            print(f"[BROWSER] Bookmarked: {self.current_url}")
            return True

        except Exception as e:
            print(f"[BROWSER] Bookmark failed: {e}")
            return False

    def open_new_tab(self) -> bool:
        """Open a new tab"""
        try:
            if not self._ensure_browser_active():
                return False

            # Use Ctrl+T to open new tab
            webdriver.ActionChains(self.driver).key_down(
                Keys.CONTROL).send_keys('t').key_up(Keys.CONTROL).perform()
            time.sleep(1)

            print("[BROWSER] New tab opened")
            return True

        except Exception as e:
            print(f"[BROWSER] Open new tab failed: {e}")
            return False

    def close_tab(self) -> bool:
        """Close current tab"""
        try:
            if not self._ensure_browser_active():
                return False

            # Use Ctrl+W to close tab
            webdriver.ActionChains(self.driver).key_down(
                Keys.CONTROL).send_keys('w').key_up(Keys.CONTROL).perform()
            time.sleep(1)

            print("[BROWSER] Tab closed")
            return True

        except Exception as e:
            print(f"[BROWSER] Close tab failed: {e}")
            return False

    def switch_tab(self, direction: str = "next") -> bool:
        """Switch to next or previous tab"""
        try:
            if not self._ensure_browser_active():
                return False

            if direction.lower() == "next":
                # Ctrl+Tab for next tab
                webdriver.ActionChains(self.driver).key_down(
                    Keys.CONTROL).send_keys(Keys.TAB).key_up(Keys.CONTROL).perform()
            else:
                # Ctrl+Shift+Tab for previous tab
                webdriver.ActionChains(self.driver).key_down(Keys.CONTROL).key_down(
                    Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).key_up(Keys.CONTROL).perform()

            time.sleep(1)
            self.current_url = self.driver.current_url
            print(f"[BROWSER] Switched to {direction} tab")
            return True

        except Exception as e:
            print(f"[BROWSER] Switch tab failed: {e}")
            return False

    def scroll_page(self, direction: str = "down", amount: int = 3) -> bool:
        """Scroll the page up or down"""
        try:
            if not self._ensure_browser_active():
                return False

            if direction.lower() == "down":
                for _ in range(amount):
                    self.driver.execute_script("window.scrollBy(0, 300);")
                    time.sleep(0.2)
            else:
                for _ in range(amount):
                    self.driver.execute_script("window.scrollBy(0, -300);")
                    time.sleep(0.2)

            print(f"[BROWSER] Scrolled {direction}")
            return True

        except Exception as e:
            print(f"[BROWSER] Scroll failed: {e}")
            return False

    def click_link(self, link_text: str) -> bool:
        """Click on a link containing the specified text with enhanced search"""
        try:
            if not self._ensure_browser_active():
                return False

            print(f"[BROWSER] Looking for link containing: '{link_text}'")

            # Multiple strategies to find the link
            strategies = [
                # Strategy 1: Direct partial link text
                lambda: self.driver.find_element(
                    By.PARTIAL_LINK_TEXT, link_text),

                # Strategy 2: XPath with text contains
                lambda: self.driver.find_element(
                    By.XPATH, f"//a[contains(text(), '{link_text}')]"),

                # Strategy 3: XPath with case-insensitive text
                lambda: self.driver.find_element(
                    By.XPATH, f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{link_text.lower()}')]"),

                # Strategy 4: Find by title or aria-label
                lambda: self.driver.find_element(
                    By.XPATH, f"//a[@title='{link_text}' or @aria-label='{link_text}']"),

                # Strategy 5: Search in all links
                lambda: next((link for link in self.driver.find_elements(By.TAG_NAME, "a")
                              if link_text.lower() in link.text.lower() and link.is_displayed()), None)
            ]

            for strategy in strategies:
                try:
                    element = strategy()
                    if element and element.is_displayed():
                        # Scroll to element if needed
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView(true);", element)
                        time.sleep(0.5)

                        # Try clicking
                        element.click()
                        time.sleep(2)
                        self.current_url = self.driver.current_url
                        print(
                            f"[BROWSER] Successfully clicked link: {link_text}")
                        return True
                except Exception:
                    continue

            print(f"[BROWSER] Link not found: {link_text}")
            return False

        except Exception as e:
            print(f"[BROWSER] Click link failed: {e}")
            return False

    def click_search_result(self, position: int = 1) -> bool:
        """Click on a search result by position (1-based index)"""
        try:
            if not self._ensure_browser_active():
                return False

            print(f"[BROWSER] Clicking search result #{position}")

            # Wait for search results to load
            time.sleep(2)

            # Try different selectors for Google search results
            selectors = [
                # Google h3 titles
                f"(//h3[contains(@class, 'LC20lb')])[{position}]",
                # Alternative Google h3
                f"(//div[@class='g']//h3)[{position}]",
                # Google result links
                f"(//div[@class='g']//a[h3])[{position}]",
                # Generic Google links
                f"(//div[contains(@class, 'g')]//a[@href])[{position}]",
            ]

            for selector in selectors:
                try:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    element.click()
                    time.sleep(3)  # Wait for page to load
                    self.current_url = self.driver.current_url
                    print(
                        f"[BROWSER] Successfully clicked search result #{position}")
                    return True
                except TimeoutException:
                    continue

            # Fallback: try to find any clickable search results
            try:
                results = self.driver.find_elements(
                    By.CSS_SELECTOR, "div.g h3")
                if results and len(results) >= position:
                    parent_link = results[position -
                                          1].find_element(By.XPATH, "./ancestor::a")
                    parent_link.click()
                    time.sleep(3)
                    self.current_url = self.driver.current_url
                    print(
                        f"[BROWSER] Successfully clicked search result #{position} (fallback)")
                    return True
            except Exception:
                pass

            print(f"[BROWSER] Could not find search result #{position}")
            return False

        except Exception as e:
            print(f"[BROWSER] Click search result failed: {e}")
            return False

    def get_search_results(self) -> list:
        """Get list of search result titles and URLs"""
        try:
            if not self._ensure_browser_active():
                return []

            results = []

            # Wait for search results
            time.sleep(2)

            # Get search result elements
            try:
                result_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, "div.g")

                # Top 10 results
                for i, element in enumerate(result_elements[:10], 1):
                    try:
                        title_elem = element.find_element(
                            By.CSS_SELECTOR, "h3")
                        link_elem = element.find_element(By.CSS_SELECTOR, "a")

                        title = title_elem.text.strip()
                        url = link_elem.get_attribute("href")

                        if title and url:
                            results.append({
                                "position": i,
                                "title": title,
                                "url": url
                            })
                    except Exception:
                        continue

            except Exception as e:
                print(f"[BROWSER] Could not get search results: {e}")

            print(f"[BROWSER] Found {len(results)} search results")
            return results

        except Exception as e:
            print(f"[BROWSER] Get search results failed: {e}")
            return []

    def click_link_by_number(self, link_number: int) -> bool:
        """Click on any link on the page by its position number"""
        try:
            if not self._ensure_browser_active():
                return False

            print(f"[BROWSER] Clicking link #{link_number} on page")

            # Get all clickable links
            links = self.driver.find_elements(By.TAG_NAME, "a")
            visible_links = [
                link for link in links if link.is_displayed() and link.get_attribute("href")]

            if len(visible_links) >= link_number:
                target_link = visible_links[link_number - 1]
                target_link.click()
                time.sleep(2)
                self.current_url = self.driver.current_url
                print(f"[BROWSER] Successfully clicked link #{link_number}")
                return True
            else:
                print(
                    f"[BROWSER] Only {len(visible_links)} links found on page")
                return False

        except Exception as e:
            print(f"[BROWSER] Click link by number failed: {e}")
            return False

    def list_links(self, max_links: int = 10) -> list:
        """List all visible links on the current page"""
        try:
            if not self._ensure_browser_active():
                return []

            links = []
            link_elements = self.driver.find_elements(By.TAG_NAME, "a")

            for i, element in enumerate(link_elements, 1):
                try:
                    if element.is_displayed() and element.get_attribute("href"):
                        text = element.text.strip()
                        href = element.get_attribute("href")

                        if text:  # Only include links with visible text
                            links.append({
                                "position": i,
                                "text": text[:100],  # Truncate long text
                                "url": href
                            })

                        if len(links) >= max_links:
                            break

                except Exception:
                    continue

            print(f"[BROWSER] Found {len(links)} visible links")
            return links

        except Exception as e:
            print(f"[BROWSER] List links failed: {e}")
            return []

    def get_page_title(self) -> str:
        """Get the title of the current page"""
        try:
            if not self._ensure_browser_active():
                return ""

            title = self.driver.title
            print(f"[BROWSER] Page title: {title}")
            return title

        except Exception as e:
            print(f"[BROWSER] Get title failed: {e}")
            return ""

    def get_current_url(self) -> str:
        """Get the current URL"""
        try:
            if not self._ensure_browser_active():
                return ""

            url = self.driver.current_url
            return url

        except Exception as e:
            print(f"[BROWSER] Get URL failed: {e}")
            return ""

    def _ensure_browser_active(self) -> bool:
        """Ensure browser is open and active"""
        if not self.driver or not self.is_active:
            print("[BROWSER] Browser not active, opening...")
            return self.open_browser()
        return True

    def get_status(self) -> Dict[str, Any]:
        """Get current browser status"""
        return {
            "is_active": self.is_active,
            "current_url": self.current_url,
            "title": self.get_page_title() if self.is_active else "",
            "driver_available": self.driver is not None
        }


# Voice command parser for browser operations
class BrowserCommandParser:
    """Parse voice commands for browser operations"""

    def __init__(self, browser: VoiceBrowser):
        self.browser = browser

        # Command patterns (order matters - more specific patterns first!)
        self.patterns = {
            'open_browser': [
                r'open browser',
                r'launch browser',
                r'start browser',
                r'open web browser'
            ],
            'close_browser': [
                r'close browser',
                r'quit browser',
                r'exit browser'
            ],
            'click_search_result': [
                r'(?:open|click) (?:the )?first (?:result|link)',
                r'(?:open|click) (?:the )?second (?:result|link)',
                r'(?:open|click) (?:the )?third (?:result|link)',
                r'(?:open|click) (?:the )?fourth (?:result|link)',
                r'(?:open|click) (?:the )?fifth (?:result|link)',
                r'(?:open|click) (?:the )?(\d+)(?:st|nd|rd|th) (?:result|link)',
                r'(?:open|click) result (\d+)',
                r'(?:open|click) link (\d+)',
                r'(?:open|click) number (\d+)'
            ],
            'click_link_number': [
                r'click link number (\d+)',
                r'click the (\d+)(?:st|nd|rd|th) link'
            ],
            'list_search_results': [
                r'(?:show|list) (?:search )?results',
                r'what are the results',
                r'show me the links'
            ],
            'list_links': [
                r'(?:show|list) (?:all )?links',
                r'what links are available',
                r'show me all links'
            ],
            'search': [
                r'search (?:for )?(.+)',
                r'google (.+)',
                r'look up (.+)',
                r'find (.+)'
            ],
            'navigate': [
                r'go to (.+)',
                r'navigate to (.+)',
                r'visit (.+)',
                r'open (?:website |site )?(.+\.(?:com|org|net|edu|gov|co\.uk|io|ly|me|info|biz))',
                r'open https?://(.+)'
            ],
            'back': [
                r'go back',
                r'navigate back',
                r'back page'
            ],
            'forward': [
                r'go forward',
                r'navigate forward',
                r'forward page'
            ],
            'refresh': [
                r'refresh page',
                r'reload page',
                r'refresh'
            ],
            'bookmark': [
                r'bookmark (?:this )?page',
                r'add bookmark',
                r'save bookmark'
            ],
            'new_tab': [
                r'new tab',
                r'open new tab',
                r'create tab'
            ],
            'close_tab': [
                r'close tab',
                r'close this tab'
            ],
            'switch_tab': [
                r'switch tab',
                r'next tab',
                r'previous tab'
            ],
            'scroll_down': [
                r'scroll down',
                r'page down'
            ],
            'scroll_up': [
                r'scroll up',
                r'page up'
            ],
            'click_link': [
                r'click (?:on )?(.+)',
                r'click link (.+)'
            ],
            'page_title': [
                r'what is the title',
                r'page title',
                r'get title'
            ],
            'current_url': [
                r'what is the url',
                r'current url',
                r'where am i'
            ]
        }

    def parse_command(self, command: str) -> tuple[str, str, dict]:
        """
        Parse voice command and return action, response, and parameters
        Returns: (action, response_message, parameters)
        """
        command = command.lower().strip()

        # Check each pattern category
        for action, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, command)
                if match:
                    return self._execute_action(action, match, command)

        return "unknown", "I didn't understand that browser command, Boss.", {}

    def _execute_action(self, action: str, match, original_command: str) -> tuple[str, str, dict]:
        """Execute the parsed browser action"""
        try:
            if action == 'open_browser':
                success = self.browser.open_browser()
                return ("open_browser",
                        "Browser opened successfully, Boss." if success else "Failed to open browser, Boss.",
                        {"success": success})

            elif action == 'close_browser':
                success = self.browser.close_browser()
                return ("close_browser",
                        "Browser closed, Boss." if success else "Failed to close browser, Boss.",
                        {"success": success})

            elif action == 'search':
                query = match.group(1).strip()
                success = self.browser.search(query)
                return ("search",
                        f"Searching for '{query}', Boss." if success else f"Search failed for '{query}', Boss.",
                        {"success": success, "query": query})

            elif action == 'navigate':
                url = match.group(1).strip()
                success = self.browser.navigate_to(url)
                return ("navigate",
                        f"Navigating to {url}, Boss." if success else f"Failed to navigate to {url}, Boss.",
                        {"success": success, "url": url})

            elif action == 'back':
                success = self.browser.go_back()
                return ("back",
                        "Going back, Boss." if success else "Cannot go back, Boss.",
                        {"success": success})

            elif action == 'forward':
                success = self.browser.go_forward()
                return ("forward",
                        "Going forward, Boss." if success else "Cannot go forward, Boss.",
                        {"success": success})

            elif action == 'refresh':
                success = self.browser.refresh_page()
                return ("refresh",
                        "Page refreshed, Boss." if success else "Refresh failed, Boss.",
                        {"success": success})

            elif action == 'bookmark':
                success = self.browser.bookmark_page()
                return ("bookmark",
                        "Page bookmarked, Boss." if success else "Bookmark failed, Boss.",
                        {"success": success})

            elif action == 'new_tab':
                success = self.browser.open_new_tab()
                return ("new_tab",
                        "New tab opened, Boss." if success else "Failed to open new tab, Boss.",
                        {"success": success})

            elif action == 'close_tab':
                success = self.browser.close_tab()
                return ("close_tab",
                        "Tab closed, Boss." if success else "Failed to close tab, Boss.",
                        {"success": success})

            elif action == 'switch_tab':
                direction = "next" if "next" in original_command else "previous"
                success = self.browser.switch_tab(direction)
                return ("switch_tab",
                        f"Switched to {direction} tab, Boss." if success else "Failed to switch tab, Boss.",
                        {"success": success, "direction": direction})

            elif action == 'scroll_down':
                success = self.browser.scroll_page("down")
                return ("scroll_down",
                        "Scrolling down, Boss." if success else "Scroll failed, Boss.",
                        {"success": success})

            elif action == 'scroll_up':
                success = self.browser.scroll_page("up")
                return ("scroll_up",
                        "Scrolling up, Boss." if success else "Scroll failed, Boss.",
                        {"success": success})

            elif action == 'click_link':
                link_text = match.group(1).strip()
                success = self.browser.click_link(link_text)
                return ("click_link",
                        f"Clicking on '{link_text}', Boss." if success else f"Could not find link '{link_text}', Boss.",
                        {"success": success, "link_text": link_text})

            elif action == 'page_title':
                title = self.browser.get_page_title()
                return ("page_title",
                        f"The page title is: {title}, Boss." if title else "Could not get page title, Boss.",
                        {"title": title})

            elif action == 'current_url':
                url = self.browser.get_current_url()
                return ("current_url",
                        f"Current URL is: {url}, Boss." if url else "Could not get current URL, Boss.",
                        {"url": url})

            elif action == 'click_search_result':
                # Extract position number from command
                position = 1  # Default to first result

                # Check for number words
                if "first" in original_command:
                    position = 1
                elif "second" in original_command:
                    position = 2
                elif "third" in original_command:
                    position = 3
                elif "fourth" in original_command:
                    position = 4
                elif "fifth" in original_command:
                    position = 5
                else:
                    # Try to extract number from regex match
                    try:
                        if match.group(1):
                            position = int(match.group(1))
                    except (IndexError, ValueError):
                        position = 1

                success = self.browser.click_search_result(position)
                return ("click_search_result",
                        f"Opening search result #{position}, Boss." if success else f"Could not open search result #{position}, Boss.",
                        {"success": success, "position": position})

            elif action == 'list_search_results':
                results = self.browser.get_search_results()
                if results:
                    result_text = "Search results, Boss:\n"
                    for result in results[:5]:  # Show top 5
                        result_text += f"{result['position']}. {result['title']}\n"
                    return ("list_search_results", result_text.strip(), {"results": results})
                else:
                    return ("list_search_results", "No search results found, Boss.", {"results": []})

            elif action == 'list_links':
                links = self.browser.list_links()
                if links:
                    link_text = "Available links, Boss:\n"
                    for link in links[:5]:  # Show top 5
                        link_text += f"{link['position']}. {link['text']}\n"
                    return ("list_links", link_text.strip(), {"links": links})
                else:
                    return ("list_links", "No links found on this page, Boss.", {"links": []})

            elif action == 'click_link_number':
                try:
                    link_number = int(match.group(1))
                    success = self.browser.click_link_by_number(link_number)
                    return ("click_link_number",
                            f"Clicking link #{link_number}, Boss." if success else f"Could not click link #{link_number}, Boss.",
                            {"success": success, "link_number": link_number})
                except (IndexError, ValueError):
                    return ("click_link_number", "Invalid link number, Boss.", {"success": False})

            else:
                return ("unknown", "Unknown browser command, Boss.", {})

        except Exception as e:
            print(f"[BROWSER] Action execution failed: {e}")
            return ("error", f"Browser command failed: {str(e)}, Boss.", {"error": str(e)})
