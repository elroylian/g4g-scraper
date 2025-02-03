# GeeksForGeeks Algorithm Content Scraper

A Python web scraper designed to extract algorithm tutorials and content from GeeksForGeeks, converting them into well-formatted markdown files for offline reading and study.

## Prerequisites

```bash
python 3.6+
```

## Required Libraries

```bash
requests
beautifulsoup4
```

You can install the required libraries using pip:

```bash
pip install requests beautifulsoup4
```

## Usage

1. Clone the repository or download the script.

2. Run the script:
```bash
python g4g_scraper.py
```

The script will:
- Create a `scraped_content` directory if it doesn't exist
- Download content from predefined algorithm topics
- Save each topic as a separate markdown file

## Output Structure

The scraper creates markdown files with the following structure:

```markdown
# Main Topic Title

## Section 1
### Article 1
Content...
Code examples...

### Article 2
Content...
Code examples...

## Section 2
...
```

## Customization

You can modify the URLs list in the `main()` function to scrape different topics:

```python
urls = [
    "https://www.geeksforgeeks.org/your-topic-here/",
    # Add more URLs...
]
```

## Configuration

Adjust the scraping behavior by modifying these parameters:

- `delay_range`: Tuple of (min, max) seconds to wait between requests
- `timeout`: Request timeout in seconds
- Various BeautifulSoup selectors for different page elements

## License

This project is licensed under the MIT License - feel free to use, modify, and distribute as needed.

## Disclaimer

This scraper is intended for personal educational use only. Please respect GeeksForGeeks' robots.txt and terms of service. Consider supporting GeeksForGeeks by:
- Using their official website for regular access
- Subscribing to their premium content
- Contributing to their community

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## Author Notes

- This scraper was created for educational purposes
- It implements polite scraping practices with delays between requests
- Content is saved in markdown format for easy reading and conversion
- The code includes extensive comments for maintainability

## Acknowledgements

* [Beautiful Soup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
* [Requests: HTTP for Humans](https://requests.readthedocs.io/en/latest/)
* [GeeksForGeeks](https://www.geeksforgeeks.org/) for their comprehensive tutorials

## TODO

Potential improvements that could be made:
- Add support for images and diagrams
- Add command-line arguments for configuration
- Improve error recovery and logging
- Add support for other GeeksForGeeks content types