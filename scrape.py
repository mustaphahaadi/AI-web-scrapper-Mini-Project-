from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_website(website):
    logging.info("Setting up ChromeDriver with WebDriver Manager...")
    try:
        # Use WebDriver Manager to automatically download and use the correct ChromeDriver version
        service = Service(ChromeDriverManager().install())
        chrome_options = Options()
        
        # Launch the local ChromeDriver using a context manager
        with webdriver.Chrome(service=service, options=chrome_options) as driver:
            logging.info("Navigating to website...")
            driver.get(website)
            
            # Use standard approach with implicit wait
            driver.implicitly_wait(10)  # Wait up to 10 seconds for elements to be available
            
            # Give the page some time to fully load (including any potential captchas)
            import time
            time.sleep(5)  # Wait 5 seconds for page to load completely
            
            logging.info("Waiting for page to load completely...")
            # Wait for the page to be fully loaded
            wait_complete = driver.execute_script("return document.readyState") == "complete"
            
            # Additional wait for any potential captchas to appear
            logging.info("Page loaded, checking for any captchas...")
            # Just wait a bit more to allow any captchas to appear and be manually solved
            time.sleep(3)
            
            logging.info("Navigated! Scraping page content...")
            html = driver.page_source
            return html
    except Exception as e:
        logging.error(f"An error occurred while scraping the website: {e}")
        raise

def extract_body_content(html):
    logging.info("Extracting body content...")
    try:
        soup = BeautifulSoup(html, 'html.parser')
        body_content = soup.find('body').get_text()
        return body_content
    except Exception as e:
        logging.error(f"An error occurred while extracting body content: {e}")
        raise

def clean_body_content(body_content):
    logging.info("Cleaning body content...")
    try:
        # Remove extra whitespace and newlines
        cleaned_content = ' '.join(body_content.split())
        return cleaned_content
    except Exception as e:
        logging.error(f"An error occurred while cleaning body content: {e}")
        raise

def split_dom_content(content, max_length=4000):
    """
    Split the content into chunks of specified maximum length while trying to maintain
    complete sentences or logical breaks.
    """
    # If content is shorter than max_length, return it as a single chunk
    if len(content) <= max_length:
        return [content]
    
    chunks = []
    current_chunk = ""
    
    # Split content into sentences (roughly, by looking for periods followed by spaces)
    sentences = content.split('. ')
    
    for sentence in sentences:
        # Add period back to sentence (except for the last one if it didn't have one)
        if sentence != sentences[-1]:
            sentence += '. '
            
        # If adding this sentence would exceed max_length, store current chunk and start new one
        if len(current_chunk) + len(sentence) > max_length:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += sentence
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks