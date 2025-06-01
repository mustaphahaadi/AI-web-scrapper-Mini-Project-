from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import requests
import sys
import time
import re
import subprocess
import platform
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)

# Function to check if Ollama server is running
def is_ollama_running(base_url="http://localhost:11434", max_retries=3, retry_delay=2):
    """Check if Ollama server is running by making a request to its API endpoint"""
    print("Checking if Ollama server is running...")
    for attempt in range(max_retries):
        try:
            # Add a longer timeout for slower systems
            response = requests.get(f"{base_url}/api/version", timeout=10)
            if response.status_code == 200:
                print("✅ Ollama server is running and accessible.")
                return True
            print(f"❌ Ollama server responded with status code: {response.status_code}")
            # Don't immediately return False on non-200 status, try again
            if attempt < max_retries - 1:
                print(f"⚠️ Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                return False
        except requests.exceptions.ConnectionError as e:
            if attempt < max_retries - 1:
                print(f"⚠️ Connection to Ollama server failed (attempt {attempt+1}/{max_retries}). Retrying in {retry_delay} seconds...")
                print(f"  Error details: Connection refused. Is Ollama running?")
                time.sleep(retry_delay)
            else:
                print("❌ Ollama server is not running or not accessible.")
                return False
        except requests.exceptions.Timeout as e:
            if attempt < max_retries - 1:
                print(f"⚠️ Connection to Ollama server timed out (attempt {attempt+1}/{max_retries}). Retrying in {retry_delay} seconds...")
                print(f"  Error details: Request timed out. Server might be busy or starting up.")
                time.sleep(retry_delay)
            else:
                print("❌ Ollama server connection timed out repeatedly.")
                return False
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(f"⚠️ Ollama server not responding (attempt {attempt+1}/{max_retries}). Retrying in {retry_delay} seconds...")
                print(f"  Error details: {str(e)}")
                time.sleep(retry_delay)
            else:
                print("❌ Ollama server is not running or not accessible.")
                return False
    return False

# Function to check if Ollama is installed
def is_ollama_installed():
    """Check if Ollama is installed on the system"""
    system = platform.system()
    try:
        if system == "Windows":
            # Check Windows Start Menu for Ollama
            try:
                start_menu = os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs")
                if os.path.exists(start_menu):
                    for root, dirs, files in os.walk(start_menu):
                        for file in files:
                            if file.lower() == "ollama.lnk":
                                return True
            except Exception as e:
                print(f"Error checking Start Menu: {e}")
                
            # Try to find Ollama in Program Files
            try:
                program_files = [os.environ.get("ProgramFiles", ""), os.environ.get("ProgramFiles(x86)", "")]
                for pf in program_files:
                    if pf and os.path.exists(os.path.join(pf, "Ollama")):
                        return True
            except Exception as e:
                print(f"Error checking Program Files: {e}")
                
            # Check if ollama.exe exists in PATH
            try:
                result = subprocess.run(["where", "ollama"], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    return True
            except Exception as e:
                print(f"Error checking PATH for Ollama: {e}")
                
        elif system == "Darwin":  # macOS
            return os.path.exists("/Applications/Ollama.app") or subprocess.run(["which", "ollama"], capture_output=True).returncode == 0
        else:  # Linux and others
            return subprocess.run(["which", "ollama"], capture_output=True).returncode == 0
    except Exception as e:
        print(f"Error checking if Ollama is installed: {e}")
    return False

# Function to get Ollama start instructions based on OS
def get_ollama_start_instructions():
    """Get OS-specific instructions for starting Ollama"""
    system = platform.system()
    if system == "Windows":
        return (
            "1. Search for 'Ollama' in your Start menu and click to launch it\n"
            "2. Or open Command Prompt and run: start /b ""Ollama"" ""C:\Program Files\Ollama\ollama.exe"" serve"
        )
    elif system == "Darwin":  # macOS
        return (
            "1. Open Finder, go to Applications, and double-click on Ollama\n"
            "2. Or open Terminal and run: open -a Ollama"
        )
    else:  # Linux and others
        return (
            "1. Open a terminal and run: ollama serve\n"
            "2. If using systemd: systemctl --user start ollama"
        )

# Configure OllamaLLM with explicit connection parameters
def initialize_ollama_model():
    """Initialize the Ollama model with proper error handling"""
    try:
        # Only initialize the model if Ollama is running
        if is_ollama_running():
            try:
                print("Initializing Ollama model...")
                model = OllamaLLM(
                    model="llama3",
                    base_url="http://localhost:11434",  # Default Ollama API endpoint
                    temperature=0.7,
                    request_timeout=120.0  # Increase timeout for larger content processing
                )
                # Test the model with a simple query to ensure it's working
                try:
                    print("Testing Ollama model connection...")
                    test_prompt = ChatPromptTemplate.from_template("Say hello")
                    test_chain = test_prompt | model
                    test_chain.invoke({})
                    print("✅ Ollama model initialized and tested successfully.")
                    return model
                except Exception as test_error:
                    print(f"❌ Ollama model test failed: {test_error}")
                    return None
            except Exception as init_error:
                print(f"❌ Error initializing Ollama model: {init_error}")
                return None
        else:
            print("❌ Ollama server is not running, model initialization skipped.")
            return None
    except Exception as e:
        print(f"❌ Unexpected error during model initialization: {e}")
        return None

# Initialize the model
model = initialize_ollama_model()


# Simple fallback parser when Ollama is not available
def simple_fallback_parser(dom_chunks, parse_description):
    logging.info("Using fallback parser...")
    try:
        if not dom_chunks or not parse_description:
            logging.warning("No content or search description provided.")
            return "No content or search description provided."
            
        results = []
        # Convert parse description to lowercase for case-insensitive matching
        parse_desc_lower = parse_description.lower()
        
        # Create a list of stopwords to filter out
        stopwords = ['the', 'and', 'that', 'with', 'from', 'this', 'these', 'for', 'are', 'was', 
                    'were', 'will', 'have', 'has', 'had', 'not', 'what', 'when', 'where', 'who', 
                    'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'some', 
                    'such', 'than', 'too', 'very', 'can', 'cannot', 'could', 'may', 'might', 
                    'must', 'need', 'ought', 'shall', 'should', 'would']
        
        # Extract key terms from the parse description
        # This is a very basic approach and won't work for complex queries
        key_terms = [term.strip() for term in re.split(r'[,\s\-_]+', parse_desc_lower) 
                    if len(term.strip()) > 2 and term.strip() not in stopwords]
        
        # If no key terms were found, use the whole description
        if not key_terms and len(parse_desc_lower) > 2:
            key_terms = [parse_desc_lower]
        
        logging.info(f"Fallback parser using key terms: {key_terms}")
        
        for i, chunk in enumerate(dom_chunks, start=1):
            try:
                chunk_lower = chunk.lower()
                matches = []
                
                # Look for sentences containing the key terms
                sentences = re.split(r'(?<=[.!?])\s+', chunk)
                for sentence in sentences:
                    # Skip very short sentences
                    if len(sentence.strip()) < 10:
                        continue
                        
                    # Check if any key term is in the sentence
                    if any(term in sentence.lower() for term in key_terms):
                        matches.append(sentence.strip())
                
                if matches:
                    results.append("\n".join(matches))
            except Exception as chunk_error:
                logging.error(f"An error occurred while processing chunk {i} in fallback parser: {chunk_error}")
                continue
            
        if not results:
            # Try a more lenient approach if no results were found
            for i, chunk in enumerate(dom_chunks, start=1):
                try:
                    # Look for paragraphs containing at least one key term
                    paragraphs = chunk.split('\n\n')
                    for paragraph in paragraphs:
                        if any(term in paragraph.lower() for term in key_terms):
                            results.append(paragraph.strip())
                except Exception:
                    continue
        
        if not results:
            logging.warning("No matching information found. Try refining your search terms.")
            return "No matching information found. Try refining your search terms."
        
        # Limit the total length of results to avoid overwhelming the user
        combined_results = "\n\n".join(results)
        if len(combined_results) > 5000:
            combined_results = combined_results[:5000] + "\n\n[Output truncated due to length...]\n"
            
        return combined_results
    except Exception as e:
        error_msg = f"Error in fallback parser: {str(e)}"
        logging.error(error_msg)
        return error_msg

def parse_with_ollama(dom_chunks, parse_description):
    logging.info("Parsing content with Ollama...")
    # Check if Ollama is running
    if model is None:
        # Check if Ollama is installed
        is_installed = is_ollama_installed()
        
        error_message = (
            "⚠️ Ollama server is not running or not accessible. \n\n"
        )
        logging.error(error_message)
        return error_message

    try:
        # Parse the content with Ollama
        results = []
        for i, chunk in enumerate(dom_chunks, start=1):
            logging.info(f"Parsing chunk {i}...")
            try:
                prompt = ChatPromptTemplate.from_template(template)
                chain = prompt | model
                result = chain.invoke({"dom_content": chunk, "parse_description": parse_description})
                results.append(result)
            except Exception as chunk_error:
                logging.error(f"An error occurred while parsing chunk {i}: {chunk_error}")
                continue

        if not results:
            logging.warning("No results were found.")
            return "No results were found."

        # Combine the results
        combined_results = "\n\n".join(results)
        return combined_results
    except Exception as e:
        logging.error(f"An error occurred while parsing with Ollama: {e}")
        return f"An error occurred while parsing with Ollama: {e}"
