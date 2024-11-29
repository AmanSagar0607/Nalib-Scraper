
# Nailib Math AI SL Sample Scraper

A robust web scraper for extracting and archiving IB Math AI SL Internal Assessment (IA) samples from Nailib.

## 🚀 Features

### 🔍 Data Extraction
- Extracts essential data points:
  - Title, subject, and description
  - Section content and checklist items
  - Word count, read time, and publication date
  - File links and downloadable resources

### 🤖 Smart Scraping
- Intelligent discovery of related samples
- Handles pagination and depth-first exploration
- Configurable scraping limits

### 💾 Robust Architecture
- MongoDB integration with upsert support to prevent duplicates
- Comprehensive error handling and rate limiting
- Detailed logging for monitoring progress

---

## 🛠 Technical Stack

- **Python 3.8+**
- **Libraries:**
  - `beautifulsoup4` - HTML parsing
  - `requests` - HTTP client
  - `pymongo` - MongoDB integration
  - `python-dotenv` - Environment management
  - `lxml` - Advanced HTML/XML processing

---

## 🔧 Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/AmanSagar0607/Nalib-Scraper.git
   cd Nalib-Scraper
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Unix/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   Create a `.env` file with the following variables:
   ```env
   MONGODB_URI=your_mongodb_uri
   DB_NAME=nailib_samples
   COLLECTION_NAME=samples
   LOG_LEVEL=INFO
   ```

---

## 🚀 Usage

1. **Run the Scraper**
   ```bash
   python src/main.py
   ```

2. **Monitor Progress**
   - Check the console for real-time updates.
   - View the MongoDB collection to access scraped data.

---

## 📊 Data Structure

```json
{
  "url": "https://nailib.com/ia-sample/...",
  "title": "Sample Title",
  "subject": "Math AI SL",
  "description": "Sample description",
  "sections": {
    "introduction": {
      "content": "Introduction content...",
      "checklist_items": ["Item 1", "Item 2"]
    },
    "mathematical_information": {
      "content": "Mathematical content...",
      "checklist_items": ["Item 1", "Item 2"]
    }
  },
  "word_count": 2000,
  "read_time": "11 mins",
  "file_links": [
    {
      "url": "https://...",
      "title": "Resource Title"
    }
  ],
  "publication_date": "2024-01-01T00:00:00Z",
  "last_updated": "2024-01-01T12:00:00Z"
}
```

---

## ⚙️ Configuration Options

| Variable          | Description                | Default           |
|--------------------|----------------------------|-------------------|
| `MONGODB_URI`      | MongoDB connection string  | Required          |
| `DB_NAME`          | Database name             | `nailib_samples`  |
| `COLLECTION_NAME`  | Collection name           | `samples`         |
| `LOG_LEVEL`        | Logging verbosity         | `INFO`            |

---

## 🛡️ Key Features

- **Intelligent Sample Discovery**:
  - Starts from seed URLs and discovers related samples.
  - Handles pagination and respects rate limits.

- **Robust Data Extraction**:
  - Adapts to dynamic content structures.
  - Cleans and validates text fields.

- **Efficient Storage**:
  - MongoDB integration with duplicate prevention.
  - Connection pooling for optimal performance.

---

## 📝 Logging and Error Handling

- Logs real-time progress, errors, and statistics.
- Graceful handling of:
  - Network errors
  - Data inconsistencies
  - MongoDB connection issues

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**GitHub Repository:** [Nalib Scraper](https://github.com/AmanSagar0607/Nalib-Scraper)
