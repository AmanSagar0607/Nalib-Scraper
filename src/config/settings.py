import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB settings
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'nailib_samples')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'samples')

# Scraper settings
BASE_URL = "https://nailib.com"
DEFAULT_SAMPLE_URL = "https://nailib.com/ia-sample/ib-math-ai-sl/63909fa87396d2b674677e94"

# API settings
API_HOST = "0.0.0.0"
API_PORT = 8000

# Logging settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')