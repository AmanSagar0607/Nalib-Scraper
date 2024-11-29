from src.scraper.nailib_scraper import NailibScraper
import json
import logging
import requests
from bs4 import BeautifulSoup

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_specific_url():
    """Test scraping from a specific URL."""
    print("\nTesting specific URL extraction...")
    
    try:
        # Initialize the scraper
        scraper = NailibScraper()
        
        # The specific URL to test
        test_url = "https://nailib.com/ia-sample/ib-math-ai-sl/63909fa87396d2b674677e94"
        
        print(f"\nFetching data from: {test_url}")
        
        # First, test if the URL is accessible
        try:
            response = requests.get(test_url)
            response.raise_for_status()
            print(f"\nURL is accessible (Status code: {response.status_code})")
            
            # Print some response details
            print(f"Content type: {response.headers.get('content-type', 'unknown')}")
            print(f"Content length: {len(response.text)} characters")
            
            # Try parsing the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            print(f"Page title: {soup.title.string if soup.title else 'No title found'}")
            
        except requests.RequestException as e:
            print(f"\nError accessing URL: {str(e)}")
            if hasattr(e, 'response'):
                print(f"Status code: {e.response.status_code}")
                print(f"Response headers: {dict(e.response.headers)}")
            return
        
        # Extract data from the URL
        data = scraper.extract_ia_data(test_url)
        
        if data:
            print("\nSuccessfully extracted data:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Print summary of extracted fields
            print("\nExtracted fields summary:")
            for key, value in data.items():
                if isinstance(value, (str, int)):
                    print(f"{key}: {value}")
                elif isinstance(value, dict):
                    print(f"{key}: {len(value)} sections")
                    # Print section names
                    print("  Sections found:", list(value.keys()))
                elif isinstance(value, list):
                    print(f"{key}: {len(value)} items")
                    if value:  # Print first item as example
                        print(f"  Example: {value[0]}")
        else:
            print("\nFailed to extract data from the URL")
            
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        logger.exception("Detailed error information:")

if __name__ == "__main__":
    test_specific_url()