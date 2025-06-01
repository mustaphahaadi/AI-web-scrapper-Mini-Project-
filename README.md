# AI Web Scraper

A web scraper that uses AI to extract information from websites.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/yourusername/ai-web-scraper.git
    cd ai-web-scraper
    ```

2.  Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  Copy the `sample.env` file to `.env`:
    ```bash
    cp sample.env .env
    ```

2.  Edit the `.env` file to set the following environment variables:
    *   `OLLAMA_API_URL`: The URL of the Ollama API (default: `http://localhost:11434`).
    *   `OLLAMA_MODEL`: The name of the Ollama model to use (default: `llama3`).

## Usage

1.  Start the Streamlit app:
    ```bash
    streamlit run main.py
    ```

2.  Open your web browser and navigate to `http://localhost:8501`.

3.  Enter the URL of the website you want to scrape and click the "Scrape Website" button.

4.  Once the website is scraped, you can ask questions about the content in the "Describe what you want to parse" text area and click the "Parse Content" button.

## Error Handling

*   **Ollama Server Not Running:** If the Ollama server is not running, the scraper will use a fallback parser. The fallback parser is less accurate than the Ollama parser, but it can still extract some information from the website.
*   **Scraping Errors:** If an error occurs while scraping the website, the scraper will display an error message. You can try scraping the website again or check the website's robots.txt file to see if scraping is allowed.
*   **Parsing Errors:** If an error occurs while parsing the content, the scraper will display an error message. You can try parsing the content again or check the parse description to make sure it is clear and concise.

## Contributing

1.  Fork the repository.
2.  Create a new branch for your feature.
3.  Make your changes and commit them.
4.  Push your branch to your fork.
5.  Create a pull request.
