#!/usr/bin/env python3
"""
Simplified headless test - Single category, single product type
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_driver():
    """Setup Firefox driver with headless configuration"""
    options = Options()

    # Headless configuration
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--window-size=1920,1080")

    # Anti-detection measures
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)
    options.set_preference("general.useragent.override",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # WebRTC blocking
    options.set_preference("media.peerconnection.enabled", False)

    try:
        service = Service(executable_path=r"d:\dev\caminando-onlinev9\geckodriver_temp\geckodriver.exe")
        driver = webdriver.Firefox(service=service, options=options)

        # Execute script to remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        logging.info("Headless Firefox driver initialized successfully")
        return driver
    except Exception as e:
        logging.error(f"Failed to initialize driver: {e}")
        raise

def handle_modals_and_overlays(driver):
    """Handle modals, cookies banners, and overlays that block interactions"""
    try:
        # Common modal selectors
        modal_selectors = [
            "div.dy-modal-wrapper",
            ".cookie-banner",
            ".gdpr-banner",
            "[data-testid*='modal']",
            ".modal",
            ".popup",
            ".overlay",
            "div[role='dialog']",
            ".vtex-modal"
        ]

        for selector in modal_selectors:
            try:
                modal_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in modal_elements:
                    if element.is_displayed():
                        # Try to click close button
                        try:
                            close_buttons = element.find_elements(By.CSS_SELECTOR, "button[aria-label*='close'], .close, [data-testid*='close']")
                            for close_btn in close_buttons:
                                if close_btn.is_displayed():
                                    driver.execute_script("arguments[0].click();", close_btn)
                                    time.sleep(1)
                                    logging.info(f"✓ Closed modal with selector: {selector}")
                                    return True
                        except:
                            pass

                        # Try to click accept/cookies buttons
                        try:
                            accept_buttons = element.find_elements(By.CSS_SELECTOR, "button:contains('Aceptar'), button:contains('Accept'), button[data-testid*='accept']")
                            for accept_btn in accept_buttons:
                                if accept_btn.is_displayed():
                                    driver.execute_script("arguments[0].click();", accept_btn)
                                    time.sleep(1)
                                    logging.info(f"✓ Accepted modal with selector: {selector}")
                                    return True
                        except:
                            pass

                        # Last resort: hide the modal
                        try:
                            driver.execute_script("arguments[0].style.display = 'none';", element)
                            logging.info(f"✓ Hidden modal with selector: {selector}")
                            return True
                        except:
                            pass

            except Exception as e:
                continue

        return False

    except Exception as e:
        logging.warning(f"Error handling modals: {e}")
        return False

def test_single_category_simple():
    """Test processing a single category with minimal operations"""
    driver = None
    try:
        driver = setup_driver()
        logging.info("Testing single category processing...")

        # Navigate to Carrefour
        driver.get("https://www.carrefour.com.ar")
        logging.info("✓ Navigated to Carrefour")

        # Wait for page to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        logging.info("✓ Page loaded")

        # Handle modals and overlays BEFORE any interactions
        handle_modals_and_overlays(driver)
        time.sleep(2)  # Extra time for modal handling

        # Try to find and click on a category (simplified)
        try:
            # Look for any category link
            category_links = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='electro'], a[href*='categoria']"))
            )

            if category_links:
                first_category = category_links[0]
                driver.execute_script("arguments[0].scrollIntoView();", first_category)
                time.sleep(1)
                first_category.click()
                logging.info("✓ Clicked on category link")

                # Wait for category page to load
                time.sleep(3)
                logging.info("✓ Category page loaded")

                # Try to extract just one product name
                try:
                    product_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid*='product'], .product-container, .vtex-product-summary")
                    if product_elements:
                        first_product = product_elements[0]
                        product_name = first_product.text[:50] if first_product.text else "Product found"
                        logging.info(f"✓ Found product: {product_name}...")
                        return True
                    else:
                        logging.warning("No products found on category page")
                        return False
                except Exception as e:
                    logging.error(f"Error extracting product: {e}")
                    return False
            else:
                logging.warning("No category links found")
                return False

        except Exception as e:
            logging.error(f"Error during category navigation: {e}")
            return False

    except Exception as e:
        logging.error(f"Error in test: {e}")
        return False
    finally:
        if driver:
            driver.quit()
            logging.info("✓ Driver closed")

if __name__ == "__main__":
    success = test_single_category_simple()
    if success:
        print("\n🎉 Single category test PASSED!")
        print("✅ Headless mode works for basic category navigation and product extraction")
    else:
        print("\n❌ Single category test FAILED!")
        print("❌ Need to debug headless category navigation")