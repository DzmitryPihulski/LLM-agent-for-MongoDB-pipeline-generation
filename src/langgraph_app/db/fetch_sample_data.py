import json
import urllib.request
from typing import Dict, List, Literal, Union

from db.db import mongo_db



async def fetch_sample_data() -> Literal[True]:
    """
    Fetches documents from multiple source URLs and adds to the database.
    
    Returns:
        Literal[True]: True if operation succeeded
    """
    # List of URLs to download data from
    urls = [
        "https://raw.githubusercontent.com/neelabalan/mongodb-sample-dataset/refs/heads/main/sample_analytics/customers.json",
        "https://raw.githubusercontent.com/neelabalan/mongodb-sample-dataset/refs/heads/main/sample_analytics/transactions.json",
    ]

    collection_names = ["customers", "transactions"]
    
    # MongoDB connection details
    
    await mongo_db.upload_from_urls(urls, collection_names)
    return True

