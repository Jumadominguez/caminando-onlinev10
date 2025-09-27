#!/usr/bin/env python3
"""
Test script for headless mode - Direct implementation
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
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
    options.add_argument("--disable-images")  # Speed up loading
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

def get_all_categories():
    """Get all categories from MongoDB"""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['carrefour']
        collection = db['categories']

        categories = list(collection.find({}, {'_id': 0}))
        logging.info(f"Found {len(categories)} categories in database")
        return categories

    except Exception as e:
        logging.error(f"Error getting categories: {e}")
        return []

def test_headless_setup():
    """Test that headless driver setup works"""
    print("Testing headless driver setup...")

    try:
        driver = setup_driver()
        print("✓ Driver created successfully")

        # Test basic navigation
        driver.get("https://www.carrefour.com.ar")
        print("✓ Navigation to Carrefour works")

        # Test getting categories
        categories = get_all_categories()
        if categories:
            print(f"✓ Found {len(categories)} categories")
            # Test with first category only
            test_category = categories[0]
            print(f"Testing with category: {test_category.get('name', 'Unknown')}")
        else:
            print("✗ No categories found")

        driver.quit()
        print("✓ Driver closed successfully")
        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_headless_setup()
    if success:
        print("\n🎉 Headless mode test PASSED!")
    else:
        print("\n❌ Headless mode test FAILED!")
        import sys
        sys.exit(1)