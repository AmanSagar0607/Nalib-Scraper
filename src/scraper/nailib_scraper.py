import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import re
from typing import Dict, Any, List, Optional, Set
import time
import random
from urllib.parse import urljoin, urlparse
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class NailibScraper:
    def __init__(self, max_retries: int = 3, backoff_factor: float = 0.3):
        """Initialize the scraper with robust retry mechanism."""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.base_url = "https://nailib.com"
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Cache for visited URLs
        self.visited_urls: Set[str] = set()

    def _make_request(self, url: str) -> Optional[str]:
        """Make HTTP request with error handling and caching."""
        try:
            if url in self.visited_urls:
                logger.info(f"URL already processed: {url}")
                return None
                
            # Random delay between requests (1-3 seconds)
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            self.visited_urls.add(url)
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        # Remove extra whitespace and normalize newlines
        return ' '.join(text.split())

    def _extract_checklist_items(self, content: str) -> List[str]:
        """Extract bullet points from content."""
        items = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('•') or line.startswith('-'):
                cleaned_item = self._clean_text(line[1:])
                if cleaned_item:
                    items.append(cleaned_item)
        return items

    def _extract_word_count_and_time(self, soup: BeautifulSoup) -> tuple:
        """Extract word count and read time using multiple strategies."""
        stats_selectors = [
            'div.article-stats', 'div.sample-stats', 'div.meta-info',
            'div.stats', 'div.metrics'
        ]
        
        for selector in stats_selectors:
            try:
                stats_div = soup.select_one(selector)
                if stats_div:
                    text = stats_div.get_text()
                    
                    word_count = None
                    read_time = None
                    
                    # Try different word count patterns
                    word_patterns = [
                        r'(\d+)\s*words?',
                        r'words?:\s*(\d+)',
                        r'length:\s*(\d+)'
                    ]
                    for pattern in word_patterns:
                        match = re.search(pattern, text, re.I)
                        if match:
                            word_count = int(match.group(1))
                            break
                    
                    # Try different read time patterns
                    time_patterns = [
                        r'(\d+\s*mins?\s*read)',
                        r'read\s*time:\s*(\d+\s*mins?)',
                        r'reading\s*time:\s*(\d+\s*mins?)'
                    ]
                    for pattern in time_patterns:
                        match = re.search(pattern, text, re.I)
                        if match:
                            read_time = match.group(1)
                            break
                    
                    if word_count or read_time:
                        return (word_count, read_time)
                        
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {str(e)}")
                continue
        
        return (None, None)

    def _extract_section_content(self, soup: BeautifulSoup, section_title: str) -> Dict[str, Any]:
        """Extract section content with advanced heading detection."""
        title_variations = [
            section_title,
            section_title.lower(),
            section_title.replace(' ', '-').lower(),
            section_title.replace(' ', '_').lower()
        ]
        
        for title in title_variations:
            try:
                # Try different heading patterns
                heading = soup.find(lambda tag: (
                    tag.name in ['h1', 'h2', 'h3', 'h4'] and
                    re.search(title, tag.get_text(), re.I)
                ))
                
                if heading:
                    content = []
                    checklist_items = []
                    current = heading.find_next_sibling()
                    
                    while current and current.name not in ['h1', 'h2', 'h3', 'h4']:
                        text = self._clean_text(current.get_text())
                        if text:
                            content.append(text)
                            if '•' in text or text.strip().startswith('-'):
                                checklist_items.extend(self._extract_checklist_items(text))
                        current = current.find_next_sibling()
                    
                    return {
                        "content": ' '.join(content),
                        "checklist_items": checklist_items
                    }
                    
            except Exception as e:
                logger.debug(f"Error extracting section {title}: {str(e)}")
                continue
        
        return {"content": "", "checklist_items": []}

    def _find_similar_samples(self, soup: BeautifulSoup) -> List[str]:
        """Find similar sample URLs using multiple strategies."""
        similar_urls = set()
        
        # Link selectors in order of relevance
        selectors = [
            'div.related-samples a',
            'div.similar-content a',
            'div.recommendations a',
            'aside a',
            'nav a',
            'main a'
        ]
        
        for selector in selectors:
            try:
                for link in soup.select(selector):
                    href = link.get('href', '')
                    if href and '/ia-sample/ib-math-ai-sl/' in href:
                        full_url = urljoin(self.base_url, href)
                        if not full_url.endswith('#'):
                            similar_urls.add(full_url)
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {str(e)}")
                continue
        
        return list(similar_urls)

    def discover_samples(self, start_url: str, max_samples: int = 10) -> List[str]:
        """Discover sample URLs using depth-first search."""
        discovered_urls = set()
        to_visit = {start_url}
        
        try:
            while to_visit and len(discovered_urls) < max_samples:
                current_url = to_visit.pop()
                if current_url in discovered_urls:
                    continue
                
                html_content = self._make_request(current_url)
                if not html_content:
                    continue
                
                soup = BeautifulSoup(html_content, 'lxml')
                similar_urls = self._find_similar_samples(soup)
                
                discovered_urls.add(current_url)
                
                # Add new URLs to visit
                for url in similar_urls:
                    if url not in discovered_urls and len(discovered_urls) < max_samples:
                        to_visit.add(url)
                
                # Log progress
                logger.info(f"Discovered {len(discovered_urls)}/{max_samples} samples")
                
            return list(discovered_urls)
            
        except Exception as e:
            logger.error(f"Error discovering samples: {str(e)}")
            return list(discovered_urls)

    def scrape_sample(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape sample data with comprehensive extraction."""
        try:
            html_content = self._make_request(url)
            if not html_content:
                return None

            soup = BeautifulSoup(html_content, 'lxml')
            
            # Extract title with fallbacks
            title = None
            title_selectors = ['h1.title', 'h1.sample-title', 'h1']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = self._clean_text(title_elem.get_text())
                    break
            
            # Extract description
            description = ""
            desc_selectors = ['div.description', 'div.summary', 'div.overview']
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    description = self._clean_text(desc_elem.get_text())
                    break
            
            # Extract core data
            word_count, read_time = self._extract_word_count_and_time(soup)
            
            # Extract sections
            sections = {
                "introduction": self._extract_section_content(soup, "Introduction"),
                "mathematical_information": self._extract_section_content(soup, "Mathematical Information"),
                "mathematical_processes": self._extract_section_content(soup, "Mathematical Processes"),
                "interpretation": self._extract_section_content(soup, "Interpretation of Findings"),
                "validity_limitations": self._extract_section_content(soup, "Validity and Limitations"),
                "academic_honesty": self._extract_section_content(soup, "Academic Honesty")
            }
            
            # Extract file links
            file_links = self._extract_file_links(soup)
            
            # Extract publication date
            publication_date = None
            date_selectors = ['time', 'span.date', 'div.meta-date']
            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    date_str = date_elem.get('datetime') or date_elem.get_text()
                    try:
                        publication_date = datetime.fromisoformat(date_str).isoformat()
                        break
                    except (ValueError, TypeError):
                        continue
            
            # Construct sample data
            sample_data = {
                "url": url,
                "title": title,
                "subject": "Math AI SL",
                "description": description,
                "sections": sections,
                "word_count": word_count,
                "read_time": read_time,
                "file_links": file_links,
                "publication_date": publication_date,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            return sample_data
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None

    def validate_sample_data(self, sample_data: Dict[str, Any]) -> bool:
        """Validate sample data with comprehensive checks."""
        try:
            # Required fields
            required_fields = ['url', 'title', 'subject']
            for field in required_fields:
                if not sample_data.get(field):
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Section validation
            sections = sample_data.get('sections', {})
            required_sections = [
                'introduction',
                'mathematical_information',
                'mathematical_processes',
                'interpretation',
                'validity_limitations',
                'academic_honesty'
            ]
            
            for section in required_sections:
                if section not in sections:
                    logger.error(f"Missing required section: {section}")
                    return False
                
                section_data = sections[section]
                if not isinstance(section_data, dict) or 'content' not in section_data:
                    logger.error(f"Invalid section format: {section}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating sample data: {str(e)}")
            return False