from scraper.nailib_scraper import NailibScraper
from database.mongo_client import MongoDBClient
import time
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initial sample URLs to start discovery from
SEED_URLS = [
    "https://nailib.com/ia-sample/ib-math-ai-sl/63909fa87396d2b674677e94",
    "https://nailib.com/ia-sample/ib-math-ai-sl/673eabc22cf72f15b89207d1",
    "https://nailib.com/ia-sample/ib-math-ai-sl/66850c7329992f12f20084f4",
    "https://nailib.com/ia-sample/ib-math-ai-sl/64b79eeb579bc83f7df3dd6b"
]

def discover_and_scrape():
    """Discover similar samples and scrape their content."""
    try:
        # Initialize scraper and database client
        scraper = NailibScraper()
        db_client = MongoDBClient(
            uri=os.getenv('MONGODB_URI'),
            db_name=os.getenv('DB_NAME', 'nailib_samples')
        )
        
        collection_name = os.getenv('COLLECTION_NAME', 'samples')
        successful_scrapes = 0
        all_urls = set()
        
        # Discover samples from each seed URL
        for seed_url in SEED_URLS:
            logger.info(f"Discovering samples from seed URL: {seed_url}")
            discovered_urls = scraper.discover_samples(seed_url, max_samples=5)
            all_urls.update(discovered_urls)
        
        logger.info(f"Discovered {len(all_urls)} unique sample URLs")
        
        # Process each discovered URL
        for url in all_urls:
            try:
                # Scrape the sample
                logger.info(f"Scraping sample from: {url}")
                sample_data = scraper.scrape_sample(url)
                
                if sample_data and scraper.validate_sample_data(sample_data):
                    # Store in MongoDB
                    success = db_client.upsert_sample(collection_name, sample_data)
                    
                    if success:
                        successful_scrapes += 1
                        logger.info(f"Successfully stored sample data from {url}")
                    else:
                        logger.error(f"Failed to store sample data from {url}")
                else:
                    logger.error(f"Invalid or missing sample data from {url}")
                
                # Add a small delay between URLs
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error processing URL {url}: {str(e)}")
                continue
        
        # Log final statistics
        stats = db_client.get_stats(collection_name)
        logger.info(f"Scraping round completed. Successfully processed {successful_scrapes}/{len(all_urls)} samples")
        logger.info(f"Collection stats: {stats}")
            
    except Exception as e:
        logger.error(f"Error in discover_and_scrape: {str(e)}")
    finally:
        if 'db_client' in locals():
            db_client.close()

def main():
    """Main function to run the scraper continuously."""
    logger.info("Starting Nailib Sample Scraper")
    
    while True:
        try:
            # Run discovery and scraping task
            discover_and_scrape()
            
            # Small delay between rounds
            time.sleep(5)  # 5 second delay between rounds
            
        except KeyboardInterrupt:
            logger.info("Scraper stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            # Brief delay before retrying on error
            time.sleep(1)

if __name__ == "__main__":
    main()