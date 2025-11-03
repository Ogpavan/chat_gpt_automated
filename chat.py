from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, WebDriverException
import time
import sys
import os
import random

def wait_for_stable_div(driver, div_selector, timeout=15, stable_checks=2, interval=0.5):
    """Wait until the last div's text stops changing (response is complete)."""
    last_text = ""
    stable_count = 0
    start_time = time.time()
    
    while stable_count < stable_checks and (time.time() - start_time) < timeout:
        try:
            # Re-find elements each time to avoid stale references
            divs = driver.find_elements(By.CSS_SELECTOR, div_selector)
            if not divs:
                time.sleep(interval)
                continue
                
            current_text = divs[-1].text  # Get text from the last div
            
            if current_text == last_text and current_text.strip() != "":
                stable_count += 1
            else:
                stable_count = 0
                last_text = current_text
                
        except StaleElementReferenceException:
            # If stale, just continue and re-find
            stable_count = 0
            
        time.sleep(interval)
    
    return last_text.strip()

def handle_login_modal(driver):
    """Handle the login modal by clicking 'Stay logged out'."""
    try:
        # Look for the "Stay logged out" link
        stay_logged_out_selectors = [
            "a[href='#']:contains('Stay logged out')",
            "//a[contains(text(), 'Stay logged out')]",
            "a.cursor-pointer:contains('Stay logged out')",
            ".text-token-text-secondary.cursor-pointer"
        ]
        
        for selector in stay_logged_out_selectors:
            try:
                if selector.startswith("//"):
                    # XPath selector
                    element = driver.find_element(By.XPATH, selector)
                else:
                    # CSS selector
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                
                if element and "stay logged out" in element.text.lower():
                    element.click()
                    print("✅ Clicked 'Stay logged out'")
                    time.sleep(2)  # Wait for modal to close
                    return True
            except:
                continue
        
        # Fallback: look for any link with "Stay logged out" text
        links = driver.find_elements(By.TAG_NAME, "a")
        for link in links:
            if "stay logged out" in link.text.lower():
                link.click()
                print("✅ Clicked 'Stay logged out' (fallback)")
                time.sleep(2)
                return True
                
    except Exception as e:
        print(f"⚠️ Could not handle login modal: {e}")
    
    return False

def check_for_rate_limit(driver):
    """Check if ChatGPT shows rate limit messages."""
    rate_limit_indicators = [
        "You've reached the current usage cap",
        "rate limit",
        "try again later",
        "Too many requests",
        "upgrade your plan",
        "usage limit"
    ]
    
    try:
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        for indicator in rate_limit_indicators:
            if indicator.lower() in page_text:
                return True
    except:
        pass
    
    return False

def create_driver():
    """Create a new Chrome driver instance with optimized settings."""
    # Suppress ChromeDriver and Chrome stderr output for clean CLI
    sys.stderr = open(os.devnull, "w")

    options = webdriver.ChromeOptions()
    
    # Add headless mode
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # Fix WebGL errors in headless mode
    options.add_argument("--enable-unsafe-swiftshader")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-webgl")
    options.add_argument("--disable-software-rasterizer")
    
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Randomize user agent slightly to avoid detection
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ]
    options.add_argument(f"--user-agent={random.choice(user_agents)}")
    
    # Performance optimizations
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-images")
    options.add_argument("--disable-javascript-harmony-shipping")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-features=TranslateUI")
    options.add_argument("--disable-ipc-flooding-protection")
    
    # Suppress Chrome logging
    options.add_argument("--log-level=3")
    options.add_argument("--disable-logging")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--silent")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # Create service with logging suppressed
    service = Service(ChromeDriverManager().install())
    service.log_path = os.devnull
    
    try:
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        print(f"❌ Failed to create driver: {e}")
        return None

def initialize_chatgpt(driver, max_retries=3):
    """Initialize ChatGPT and wait for it to be ready."""
    wait = WebDriverWait(driver, 15)
    
    for attempt in range(max_retries):
        try:
            print(f"🚀 Opening ChatGPT (attempt {attempt + 1})...")
            driver.get("https://chatgpt.com")
            
            # Wait a moment for page to load
            time.sleep(3)
            
            # Check for and handle login modal
            try:
                # Look for modal indicators
                modal_indicators = [
                    "Thanks for trying ChatGPT",
                    "Log in or sign up",
                    "Stay logged out"
                ]
                
                page_text = driver.find_element(By.TAG_NAME, "body").text
                if any(indicator in page_text for indicator in modal_indicators):
                    print("🔍 Login modal detected, handling...")
                    handle_login_modal(driver)
                    time.sleep(2)
            except:
                pass
            
            # Wait for the input to be ready
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true']#prompt-textarea")))
            
            # Check for rate limits
            if check_for_rate_limit(driver):
                print("⚠️ Rate limit detected on initialization")
                return False
                
            print("✅ ChatGPT is ready!")
            return True
            
        except TimeoutException:
            print(f"⏰ Timeout on attempt {attempt + 1}")
            if attempt < max_retries - 1:
                time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
    
    return False

def send_message(driver, wait, message):
    """Send a message and get response, with rate limit detection."""
    try:
        # Check for and handle login modal before sending
        try:
            page_text = driver.find_element(By.TAG_NAME, "body").text
            if "Stay logged out" in page_text:
                print("🔍 Login modal appeared, handling...")
                handle_login_modal(driver)
                time.sleep(2)
        except:
            pass
        
        # Check for rate limits before sending
        if check_for_rate_limit(driver):
            print("⚠️ Rate limit detected before sending message")
            return "RATE_LIMITED"
        
        # Wait for the input box and interact immediately
        input_div = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[contenteditable='true']#prompt-textarea")))
        input_div.click()
        input_div.clear()
        input_div.send_keys(message)
        
        # Click send immediately without delay
        send_btn = wait.until(EC.element_to_be_clickable((By.ID, "composer-submit-button")))
        send_btn.click()
        
        # Wait for response to appear
        div_selector = "div[data-message-author-role='assistant']"
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, div_selector)))
        time.sleep(0.5)  # Minimal delay for response to start
        
        # Check for rate limits after sending
        if check_for_rate_limit(driver):
            print("⚠️ Rate limit detected after sending message")
            return "RATE_LIMITED"
        
        # Wait for the response to stabilize and get the final text
        final_response = wait_for_stable_div(driver, div_selector)
        return final_response
        
    except TimeoutException:
        print("⏰ Timeout waiting for response")
        return "TIMEOUT"
    except Exception as e:
        print(f"❌ Error in send_message: {e}")
        return "ERROR"

def main():
    driver = None
    wait = None
    message_count = 0
    max_messages_per_session = 50  # Restart after 50 messages to avoid limits
    
    try:
        while True:
            # Create new driver if needed
            if driver is None:
                driver = create_driver()
                if not driver:
                    print("❌ Failed to create driver. Exiting...")
                    break
                
                wait = WebDriverWait(driver, 15)
                
                # Initialize ChatGPT
                if not initialize_chatgpt(driver):
                    print("❌ Failed to initialize ChatGPT. Trying new instance...")
                    if driver:
                        driver.quit()
                        driver = None
                    time.sleep(5)
                    continue
                
                message_count = 0
                print("Type your message (type 'exit' or 'quit' to stop):\n")
            
            # Get user input
            user_input = input("You: ")
            if user_input.strip().lower() in ("exit", "quit"):
                print("👋 Exiting. Goodbye!")
                break
            
            print("🚀 Thinking...")
            response = send_message(driver, wait, user_input)
            
            # Handle different response types
            if response == "RATE_LIMITED":
                print("🔄 Rate limit hit. Starting new ChatGPT instance...")
                if driver:
                    driver.quit()
                    driver = None
                time.sleep(random.uniform(3, 7))  # Random delay before restart
                continue
                
            elif response == "TIMEOUT" or response == "ERROR":
                print("🔄 Error occurred. Restarting ChatGPT instance...")
                if driver:
                    driver.quit()
                    driver = None
                time.sleep(2)
                continue
                
            elif response and response.strip():
                print(f"\nChatGPT:\n{response}\n")
                message_count += 1
                
                # Restart session after max messages to prevent rate limits
                if message_count >= max_messages_per_session:
                    print("🔄 Session limit reached. Starting fresh instance...")
                    if driver:
                        driver.quit()
                        driver = None
                    time.sleep(2)
                
            else:
                print("⚠️ No response received.\n")

    except KeyboardInterrupt:
        print("\n👋 Interrupted. Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        if driver:
            driver.quit()
        sys.stderr = sys.__stderr__  # Restore stderr

if __name__ == "__main__":
    main()
