from typing import Any, Dict, Literal, List

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import urllib.request
from typing import List, Literal
from pymongo import MongoClient
from bson import json_util

from config import (
    MONGO_COLLECTION_NAME,
    MONGO_DB_NAME,
    MONGO_HOST,
    MONGO_LOGIN,
    MONGO_PASSWORD,
    MONGO_PORT,
)
from models.db_models import MongoConfig


class MongoDatabase:
    def __init__(self, config: MongoConfig):
        self.config: MongoConfig = config

    async def connect(self) -> Literal[True]:
        """Connect to the db.

        Returns:
            Literal[True]: whether the connection succeeded.
        """
        self._mongo_client: MongoClient[Dict[str, Any]] = MongoClient(
            # f"mongodb://{self.config.MONGO_LOGIN}:{self.config.MONGO_PASSWORD}@{self.config.MONGO_HOST}:{self.config.MONGO_PORT}"
            f"mongodb://{self.config.MONGO_LOGIN}:{self.config.MONGO_PASSWORD}@mongodb:{self.config.MONGO_PORT}"
        )
        # self._db = self._mongo_client[self.config.MONGO_DB_NAME]
        # self.collection = Collection(self._db, self.config.MONGO_COLLECTION_NAME)
        return True
    

    # async def get_the_number_of_docs(self) -> int:
    #     """Get the current number of documents in the working collection.

    #     Returns:
    #         int: the number of documents.
    #     """
    #     return len(self.collection.find({}).to_list())
    
    # async def download_and_parse_json(self, url: str) -> List:
    #     """
    #     Download JSON data from URL and parse it using json_util.
        
    #     Args:
    #         url (str): URL to download JSON data from
            
    #     Returns:
    #         List: List of parsed documents
    #     """
    #     try:
    #         # Download data from URL
    #         response = urllib.request.urlopen(url)
    #         data = response.read().decode("utf-8")
            
    #         # Check if the data is in JSON Lines format (one JSON object per line)
    #         if data.strip().startswith("{") and "\n{" in data:
    #             json_objects = data.strip().split("\n")
    #             parsed_data = [json_util.loads(obj) for obj in json_objects]
    #         else:
    #             # Assume it's a single JSON object or an array
    #             parsed_data = json_util.loads(data)
    #             if not isinstance(parsed_data, list):
    #                 parsed_data = [parsed_data]
            
    #         return parsed_data
    #     except Exception as e:
    #         print(f"Error downloading or parsing data from {url}: {e}")
    #         return []
    
    # async def upload_from_urls(self, urls: List[str], collection_names: List[str]) -> Literal[True]:
    #     """
    #     Download, parse and upload JSON data from multiple URLs.
        
    #     Args:
    #         urls (List[str]): List of URLs to download JSON data from
            
    #     Returns:
    #         Literal[True]: True if operation succeeded
    #     """
    #     total_documents = 0
    #     assert len(urls) == len(collection_names)

        
    #     for i in range(len(urls)):
    #         print(f"Processing data from: {urls[i]}")
    #         input_collection = Collection(self._db, collection_names[i])
    #         parsed_data = await self.download_and_parse_json(urls[i])
            
    #         if parsed_data:
    #             # Insert data into MongoDB
    #             result = input_collection.insert_many(parsed_data)
    #             num_inserted = len(result.inserted_ids)
    #             total_documents += num_inserted
    #             print(f"Inserted {num_inserted} documents from {urls[i]}")
    #         else:
    #             print(f"No data was inserted from {urls[i]}")
        
    #     print(f"Total documents inserted: {total_documents}")
    #     return True

    async def disconnect(self) -> Literal[True]:
        """Disconnect from the db.

        Returns:
            Literal[True]: whether the disconnection succeeded.
        """
        self.__mongo_client.close()
        return True


mongo_config = MongoConfig(
    MONGO_PORT=MONGO_PORT,
    MONGO_HOST=MONGO_HOST,
    MONGO_DB_NAME=MONGO_DB_NAME,
    MONGO_COLLECTION_NAME=MONGO_COLLECTION_NAME,
    MONGO_LOGIN=MONGO_LOGIN,
    MONGO_PASSWORD=MONGO_PASSWORD,
)

mongo_db = MongoDatabase(mongo_config)
