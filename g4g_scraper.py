"""
GeeksForGeeks Web Scraper

This script scrapes tutorial content from GeeksForGeeks, focusing on algorithm-related articles.
It converts the content into well-formatted markdown files while preserving the structure and code examples.

Features:
- Handles nested topic structures
- Preserves code blocks with language detection
- Implements polite scraping with random delays
- Robust error handling and content extraction
"""

import requests
from bs4 import BeautifulSoup
import time
import os
import random
from urllib.parse import urljoin

class GeeksForGeeksScraper:
    """
    A web scraper class specifically designed for GeeksForGeeks algorithm tutorials.
    
    Attributes:
        session (requests.Session): Maintains cookies and connection pooling
        delay_range (tuple): Min and max seconds to wait between requests
        base_url (str): The base URL for GeeksForGeeks
    """
    
    def __init__(self, delay_range=(1, 3)):
        """
        Initialize the scraper with custom headers and delay settings.
        
        Args:
            delay_range (tuple): Range of seconds (min, max) to delay between requests
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.delay_range = delay_range
        self.base_url = "https://www.geeksforgeeks.org"

    def _delay(self):
        """Implement a random delay between requests to avoid overwhelming the server."""
        time.sleep(random.uniform(*self.delay_range))

    def fetch_page(self, url):
        """
        Fetch a webpage with error handling and timeout.
        
        Args:
            url (str): The URL to fetch
            
        Returns:
            str or None: The page HTML content, or None if the request failed
        """
        try:
            self._delay()
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {str(e)}")
            return None

    def find_topic_section(self, soup):
        """
        Locate the main content section containing organized topic links.
        
        Uses multiple pattern matching strategies to find the most likely
        content container based on common GeeksForGeeks page structures.
        
        Args:
            soup (BeautifulSoup): Parsed HTML content
            
        Returns:
            bs4.element.Tag or None: The main content section if found
        """
        patterns = [
            # Headers followed by lists pattern
            {'headers': ['h2', 'h3'], 'min_links': 3},
            # Multiple lists pattern
            {'lists': 'ul', 'min_links': 5},
            # Known container classes pattern
            {'container': ['post-content', 'entry-content', 'article-content']}
        ]
        
        for pattern in patterns:
            if 'headers' in pattern:
                # Try finding sections with headers that have substantial link lists
                for header_tag in pattern['headers']:
                    headers = soup.find_all(header_tag)
                    for header in headers:
                        next_ul = header.find_next('ul')
                        if next_ul and len(next_ul.find_all('a')) >= pattern['min_links']:
                            return header.parent
            
            elif 'lists' in pattern:
                # Look for significant list clusters
                lists = soup.find_all('ul')
                for ul in lists:
                    if len(ul.find_all('a')) >= pattern['min_links']:
                        return ul.parent
            
            elif 'container' in pattern:
                # Check known content container classes
                for class_name in pattern['container']:
                    container = soup.find('div', class_=class_name)
                    if container and container.find_all('a'):
                        return container
        
        return None

    def scrape_from_url(self, url):
        """
        Main scraping method that processes a GeeksForGeeks topic page.
        
        Extracts the topic structure and recursively scrapes linked articles,
        organizing everything into a markdown-formatted hierarchy.
        
        Args:
            url (str): The topic page URL to scrape
            
        Returns:
            list or None: List of markdown content strings, or None if scraping failed
        """
        print(f"Fetching main page: {url}")
        html_content = self.fetch_page(url)
        if not html_content:
            return None
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract page title
        page_title = soup.find('h1')
        main_title = page_title.get_text(strip=True) if page_title else "GeeksForGeeks Guide"
        
        # Locate the main content section
        topic_section = self.find_topic_section(soup)
        if not topic_section:
            print("Could not find topic section in the page")
            return None
        
        # Build markdown content
        markdown_content = [f"# {main_title}\n"]
        
        # Process each section and its articles
        for header in topic_section.find_all(['h2', 'h3']):
            section_title = header.get_text(strip=True)
            if not section_title or len(section_title) < 2:
                continue
                
            print(f"\nProcessing section: {section_title}")
            markdown_content.append(f"\n## {section_title}\n")
            
            # Process articles in the section
            ul = header.find_next('ul')
            if ul:
                for li in ul.find_all('li'):
                    link = li.find('a')
                    if link and link.get('href'):
                        article_url = urljoin(self.base_url, link.get('href'))
                        text = link.get_text(strip=True)
                        print(f"Scraping: {text} - {article_url}")
                        
                        markdown_content.append(f"\n### {text}\n")
                        
                        # Get article content
                        page_html = self.fetch_page(article_url)
                        if page_html:
                            article_content = self.extract_article_content(page_html)
                            if article_content:
                                markdown_content.append(article_content['content'])
                        
                        markdown_content.append("\n---\n")
        
        return markdown_content
    
    def extract_article_content(self, html):
        """
        Extract and format article content, preserving structure and code blocks.
        
        Handles various content elements including:
        - Headers of different levels
        - Paragraphs and text content
        - Code blocks with language detection
        - Ordered and unordered lists
        
        Args:
            html (str): The HTML content of the article
            
        Returns:
            dict or None: Dictionary with 'title' and 'content' keys, or None if extraction failed
        """
        if not html:
            return None
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Get article title
        title = ""
        h1 = soup.find('h1')
        if h1:
            title = h1.get_text(strip=True)
        
        markdown_content = []
        
        # Find main article container
        main_content = soup.find('article') or soup.find('div', {'class': ['post-content', 'entry-content', 'article-content']})
        
        if main_content:
            # Track code block state
            in_code_block = False
            current_code_block = []
            current_language = None
            
            # Process content elements
            elements = main_content.find_all(['p', 'h2', 'h3', 'h4', 'pre', 'code', 'ul', 'ol', 'div'])
            
            for element in elements:
                # Process headers
                if element.name in ['h2', 'h3', 'h4']:
                    # Close any open code block before adding header
                    if in_code_block and current_code_block:
                        markdown_content.append(f"\n```{current_language or ''}\n{''.join(current_code_block)}\n```\n")
                        current_code_block = []
                        in_code_block = False
                    
                    level = int(element.name[1]) + 1
                    markdown_content.append(f"\n{'#' * level} {element.get_text(strip=True)}\n")
                
                # Process paragraphs
                elif element.name == 'p':
                    if in_code_block and current_code_block:
                        markdown_content.append(f"\n```{current_language or ''}\n{''.join(current_code_block)}\n```\n")
                        current_code_block = []
                        in_code_block = False
                    
                    text = element.get_text(strip=True)
                    if text:
                        markdown_content.append(f"\n{text}\n")
                
                # Process code blocks
                elif element.name in ['pre', 'code'] or (element.name == 'div' and 'code' in element.get('class', [])):
                    code_text = element.get_text()
                    
                    # Detect programming language from class
                    language = None
                    if 'class' in element.attrs:
                        classes = element.get('class', [])
                        language_classes = [c for c in classes if 'language-' in c]
                        if language_classes:
                            language = language_classes[0].replace('language-', '')
                    
                    # Handle code block state
                    if not in_code_block:
                        in_code_block = True
                        current_language = language
                    
                    if code_text.strip():
                        current_code_block.append(code_text)
                
                # Process lists
                elif element.name in ['ul', 'ol']:
                    if in_code_block and current_code_block:
                        markdown_content.append(f"\n```{current_language or ''}\n{''.join(current_code_block)}\n```\n")
                        current_code_block = []
                        in_code_block = False
                    
                    markdown_content.append("\n")
                    for li in element.find_all('li'):
                        markdown_content.append(f"- {li.get_text(strip=True)}\n")
            
            # Close any remaining code block
            if in_code_block and current_code_block:
                markdown_content.append(f"\n```{current_language or ''}\n{''.join(current_code_block)}\n```\n")
        
        return {
            'title': title,
            'content': "\n".join(markdown_content)
        }

    def save_content(self, content, filename):
        """
        Save the scraped content to a markdown file.
        
        Args:
            content (list): List of markdown-formatted strings
            filename (str): Name of the output file
        """
        os.makedirs('scraped_content', exist_ok=True)
        filepath = os.path.join('scraped_content', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        print(f"\nContent saved to {filepath}")

def main():
    """
    Main execution function that initializes the scraper and processes multiple URLs.
    
    Covers major algorithm topics from GeeksForGeeks including:
    - Greedy Algorithms
    - Dynamic Programming
    - Graph Algorithms
    - Pattern Searching
    - Branch and Bound
    - Geometric Algorithms
    - Randomized Algorithms
    """
    # Initialize scraper
    scraper = GeeksForGeeksScraper()
    
    # List of algorithm topic URLs to scrape
    urls = [
        "https://www.geeksforgeeks.org/greedy-algorithms/",
        "https://www.geeksforgeeks.org/dynamic-programming/",
        "https://www.geeksforgeeks.org/graph-data-structure-and-algorithms/",
        "https://www.geeksforgeeks.org/pattern-searching/",
        "https://www.geeksforgeeks.org/branch-and-bound-algorithm/",
        "https://www.geeksforgeeks.org/geometric-algorithms/",
        "https://www.geeksforgeeks.org/randomized-algorithms/"
    ]
    
    for url in urls:
        # Generate filename from the last part of the URL
        filename = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
        filename = f"{filename}.md"
        
        # Scrape and save content
        content = scraper.scrape_from_url(url)
        
        if content:
            scraper.save_content(content, filename)
        else:
            print("Failed to scrape content from the URL")

if __name__ == "__main__":
    main()