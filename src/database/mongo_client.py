from pymongo import MongoClient
from pymongo.errors import PyMongoError, ConnectionFailure, ServerSelectionTimeoutError
from bson import ObjectId
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class MongoJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for MongoDB objects."""
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

class MongoDBClient:
    def __init__(self, uri: str, db_name: str, collection_name: str):
        """Initialize MongoDB client with connection URI and database name."""
        try:
            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            self.db = self.client[db_name]
            self.collection_name = collection_name
            
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB database: {db_name}")
            
            # Ensure text index exists
            self.ensure_indexes()
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
        except ServerSelectionTimeoutError as e:
            logger.error(f"Could not connect to MongoDB server: {str(e)}")
            raise
        except PyMongoError as e:
            logger.error(f"MongoDB error: {str(e)}")
            raise

    def ensure_indexes(self):
        """Ensure required indexes exist."""
        try:
            # Create text index for search
            self.db[self.collection_name].create_index([
                ("title", "text"),
                ("description", "text"),
                ("sections.introduction.content", "text")
            ])
            logger.info("Ensured text search indexes exist")
        except PyMongoError as e:
            logger.error(f"Error creating indexes: {str(e)}")

    def _serialize_doc(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize MongoDB document to JSON-compatible format."""
        if doc is None:
            return None
        return json.loads(MongoJSONEncoder().encode(doc))

    def _validate_sample(self, sample_data: Dict[str, Any]) -> bool:
        """Validate sample data against expected schema."""
        required_fields = ['url', 'title', 'subject']
        for field in required_fields:
            if field not in sample_data:
                logger.error(f"Missing required field: {field}")
                return False
        return True

    def upsert_sample(self, sample_data: Dict[str, Any]) -> bool:
        """
        Upsert a sample document into MongoDB.
        Uses URL as the unique identifier.
        """
        try:
            if not self._validate_sample(sample_data):
                return False

            collection = self.db[self.collection_name]
            
            # Create query for upsert (using URL as unique identifier)
            query = {"url": sample_data["url"]}
            
            # Add metadata
            sample_data["last_updated"] = datetime.utcnow()
            
            # Perform upsert
            result = collection.update_one(
                query,
                {"$set": sample_data},
                upsert=True
            )
            
            logger.info(
                f"Upserted document: matched={result.matched_count}, "
                f"modified={result.modified_count}, "
                f"upserted_id={result.upserted_id}"
            )
            return True
            
        except PyMongoError as e:
            logger.error(f"MongoDB upsert error: {str(e)}")
            return False

    def get_samples(self, query: Dict = None, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Retrieve samples from MongoDB with pagination.
        Returns list of samples.
        """
        try:
            collection = self.db[self.collection_name]
            cursor = collection.find(query or {}, {'_id': 0}).skip(skip).limit(limit)
            samples = list(cursor)
            return [self._serialize_doc(sample) for sample in samples]
        except PyMongoError as e:
            logger.error(f"MongoDB query error: {str(e)}")
            return []

    def get_sample_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific sample by URL.
        Returns the sample document or None if not found.
        """
        try:
            collection = self.db[self.collection_name]
            doc = collection.find_one({"url": url}, {'_id': 0})
            return self._serialize_doc(doc)
        except PyMongoError as e:
            logger.error(f"MongoDB query error: {str(e)}")
            return None

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the samples collection."""
        try:
            collection = self.db[self.collection_name]
            stats = {
                "total_samples": collection.count_documents({}),
                "subjects": collection.distinct("subject"),
                "latest_update": collection.find_one(
                    sort=[("last_updated", -1)]
                )["last_updated"].isoformat() if collection.find_one() else None
            }
            return stats
        except PyMongoError as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {}

    def get_samples_by_subject(self, subject: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get samples for a specific subject."""
        return self.get_samples({"subject": subject}, limit=limit)

    def close(self):
        """Close MongoDB connection."""
        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except PyMongoError as e:
            logger.error(f"Error closing MongoDB connection: {str(e)}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()