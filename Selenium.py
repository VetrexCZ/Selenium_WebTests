from selenium.webdriver.support import expected_conditions as ec # Terms for explicit wait
from webdriver_manager.chrome import ChromeDriverManager # Automatic installation of ChromeDriver
from selenium.webdriver.support.ui import WebDriverWait # Explicit wait
from selenium.webdriver.chrome.service import Service # Service for ChromeDriver
from selenium.webdriver.common.keys import Keys # Simulation of keyboard keys
from selenium.webdriver.common.by import By # Locators for elements
from selenium import webdriver  # Main Selenium WebDriver
import logging # Logging messages
import os # Operating system functions

# URL of the website to be tested
URL = "https://www.autodily-pema.cz"

# Logging configuration
logging.basicConfig(
    level=logging.INFO, # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format='%(asctime)s - %(levelname)s: %(message)s',  # Define log format %(asctime)s- time %(levelname)s:- level of log %(message)s- message
    datefmt='%Y-%m-%d %H:%M:%S' # Define date format %H:%M:%S- hours, minutes, seconds
)
logger = logging.getLogger(__name__)

def open_webpage(driver, url):
    """Open the webpage"""
    driver.get(url)
    logger.info(f"Opened webpage: {url}")

def initialize_driver():
    """Initializing Chrome WebDriver with robust configuration"""
    try:

        driver_cache_path = "chromedriver_path.txt"
        if os.path.exists(driver_cache_path):
            with open(driver_cache_path, "r") as file:
                driver_path = file.read().strip()
        else:
            driver_path = ChromeDriverManager().install()
            with open(driver_cache_path, "w") as file:
                file.write(driver_path)
                
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service)
        driver.maximize_window()
        logger.info("WebDriver successfully initialized")
        return driver
    except Exception as e:
        logger.error(f"Error initializing WebDriver: {e}")
        raise

def handle_cookies(driver):
    """Handle cookie consent popup"""
    try:
        # Wait for the cookies consent button to be clickable
        cookies_button = WebDriverWait(driver, 5).until(
            ec.element_to_be_clickable((By.NAME, "grantAllButton"))
        )
        cookies_button.click()
        logger.info("Cookies consent button clicked successfully")
    except Exception as e:
        logger.warning(f"Error handling cookies popup: {e}")

def verify_page_title(driver, expected_title):
    """Verify the page title matches the expected title"""
    try:
        actual_title = driver.title
        assert expected_title in actual_title, f"Page title verification failed: Expected title to contain '{expected_title}', but found '{actual_title}'"
        logger.info(f"Page title verified: {actual_title}")
    except AssertionError as e:
        logger.error(f"Page title not found: {e}")
        raise

def verify_search_functionality(driver, search_query, expected_result):
    """Test the search functionality on the website"""
    try:
        # Wait for search input with explicit wait
        search_box = WebDriverWait(driver, 5).until(
            ec.presence_of_element_located((By.NAME, "search"))
        )

        search_box.clear()
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)

        # Wait for search results and verify
        product_heading = WebDriverWait(driver, 5).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "h2.heading.productInline__heading"))
        )

        # Verify element is displayed
        assert product_heading.is_displayed(), "Search results not displayed"
        assert expected_result in product_heading.text, f"Search query '{search_query}' failed: Expected '{expected_result}' not found in '{product_heading.text}'"
        logger.info("Search functionality works correctly")
    
    except Exception as e:
        logger.error(f"Error testing search: {e}")
        raise

def verify_login_form(driver):
    """Verify login form functionality"""
    try:
        # Click "Můj účet" button
        account_button = WebDriverWait(driver, 5).until(
            ec.element_to_be_clickable((By.XPATH,"//span[@class='layoutHeaderMainBar__button__label'][contains(text(),'Můj účet')]"))
        )
        account_button.click()

        login_button = WebDriverWait(driver, 5).until(
            ec.element_to_be_clickable((By.XPATH, "//span[@class='dropdownMenu__icon']"))
        )

        login_button.click()
        
        driver.find_element(By.ID, "frm-login-loginForm-email").send_keys("test")

        driver.find_element(By.ID, "frm-login-loginForm-password").send_keys("test")
        
        green_button = WebDriverWait(driver, 5).until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'][value='Přihlásit se']"))
        )

        green_button.click()

        logger.info("Login form verification successful")
    except Exception as e:
        error_message = f"Error verifying login form: {str(e.__class__.__name__)}: {str(e)}"
        logger.error(error_message)
        raise type(e)(error_message) from e

def run_tests():
    """Main Test execution Function"""
    driver = None
    try:
        # Opening webpage
        driver = initialize_driver()
        open_webpage(driver, URL)

        # Tests
        handle_cookies(driver)
        verify_page_title(driver, "Autodíly, motodíly, cyklo vybavení, nářadí, oleje, chovatelské potřeby, zahrada - levně")
        verify_search_functionality(driver, "Brzdové destičky", "Brzdové destičky")
        verify_login_form(driver)
        logger.info("All tests were successful")

    except Exception as e:
        logger.error(f"Error: program cannot be complete: {e}")

    finally:
        # Page close
        if driver:
            driver.quit()
            logger.info("Webdriver closed")

if __name__ == "__main__":
    run_tests()
