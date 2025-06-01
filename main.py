import streamlit as st
from scrape import (
    scrape_website,
    extract_body_content,
    clean_body_content,
    split_dom_content
)
from parse import parse_with_ollama
import logging
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Parse command-line arguments
parser = argparse.ArgumentParser(description='AI Web Scraper')
parser.add_argument('--url', type=str, help='The URL of the website to scrape')
parser.add_argument('--output', type=str, help='The name of the output file to save the scraped content')
parser.add_argument('--wait', type=int, default=5, help='The number of seconds to wait for the page to load')
parser.add_argument('--model', type=str, default='llama3', help='The name of the Ollama model to use for parsing')
args = parser.parse_args()

# Streamlit UI
st.title("AI Web Scraper")
url = st.text_input("Enter Website URL", value=args.url if args.url else "")

# Step 1: Scrape the Website
if st.button("Scrape Website"):
    if url:
        with st.status("Scraping the website...", expanded=True) as status:
            try:
                # Scrape the website
                dom_content = scrape_website(url, wait=args.wait)
                status.update(label="Extracting body content...", state="running")
                body_content = extract_body_content(dom_content)
                status.update(label="Cleaning body content...", state="running")
                cleaned_content = clean_body_content(body_content)

                # Store the DOM content in Streamlit session state
                st.session_state.dom_content = cleaned_content

                # Display the DOM content in an expandable text box
                with st.expander("View DOM Content"):
                    st.text_area("DOM Content", cleaned_content, height=300)

                # Save the scraped content to a file if an output file is specified
                if args.output:
                    status.update(label="Saving scraped content to file...", state="running")
                    with open(args.output, 'w', encoding='utf-8') as f:
                        f.write(cleaned_content)
                    st.write(f"Scraped content saved to {args.output}")

                status.update(label="Scraping completed!", state="complete")
            except Exception as e:
                st.error(f"An error occurred while scraping the website: {e}")
                logging.error(f"An error occurred while scraping the website: {e}")
                status.update(label="Scraping failed!", state="error")


# Step 2: Ask Questions About the DOM Content
if "dom_content" in st.session_state:
    parse_description = st.text_area("Describe what you want to parse")

    if st.button("Parse Content"):
        if parse_description:
            with st.status("Parsing the content...", expanded=True) as status:
                try:
                    # Parse the content with Ollama
                    dom_chunks = split_dom_content(st.session_state.dom_content)
                    parsed_result = parse_with_ollama(dom_chunks, parse_description, model=args.model)
                    st.write(parsed_result)
                    status.update(label="Parsing completed!", state="complete")
                except Exception as e:
                    st.error(f"An error occurred while parsing the content: {e}")
                    logging.error(f"An error occurred while parsing the content: {e}")
                    status.update(label="Parsing failed!", state="error")
