async def analyze_mongo_schema(db, sample_percent=10, max_docs=10) -> dict:
    """
    Analyze the schema of MongoDB collections.
    
    Args:
        db: pymongo database connection
        sample_percent: percentage of documents to sample (default 10%)
        max_docs: maximum number of documents to analyze per collection (default 100)
        
    Returns:
        dict: Collection names as keys, schema analysis as values with lists of types
    """
    result = {}
    
    # Get all collection names
    collection_names = db.list_collection_names()
    
    for collection_name in collection_names:
        collection = db[collection_name]
        
        # Get the total count and calculate sample size
        total_count = collection.count_documents({})
        sample_size = min(max_docs, int(total_count * sample_percent / 100))
        
        # Skip empty collections
        if sample_size == 0:
            continue
        
        # Aggregate fields and their types
        field_types = {}
        
        # Get a random sample of documents
        documents = list(collection.aggregate([{"$sample": {"size": sample_size}}]))
        
        # Analyze each document
        for doc in documents:
            await _analyze_document(doc, field_types, "")
        
        result[collection_name] = field_types
    
    return result

async def _analyze_document(doc, field_types, prefix):
    """
    Recursively analyze a document and update field_types.
    
    Args:
        doc: MongoDB document
        field_types: dict to update with field types
        prefix: prefix for nested fields
    """
    for key, value in doc.items():
        field_name = f"{prefix}{key}" if prefix else key
        
        # Get the type name
        type_name = type(value).__name__
        
        # Handle nested documents (dict)
        if isinstance(value, dict):
            if field_name not in field_types:
                field_types[field_name] = {}
            
            _analyze_document(value, field_types, f"{field_name}.")
        
        # Handle arrays
        elif isinstance(value, list):
            if field_name not in field_types:
                field_types[field_name] = {"array": []}
            elif "array" not in field_types[field_name]:
                field_types[field_name] = {"array": []}
            
            # Track types of elements in the array
            if value:
                for item in value:
                    item_type = type(item).__name__
                    
                    if item_type not in field_types[field_name]["array"]:
                        field_types[field_name]["array"].append(item_type)
                    
                    # For nested objects in arrays
                    if isinstance(item, dict):
                        array_item_field = f"{field_name}[]"
                        if array_item_field not in field_types:
                            field_types[array_item_field] = {}
                        
                        _analyze_document(item, field_types, f"{array_item_field}.")
        
        # Handle scalar values
        else:
            if field_name not in field_types:
                field_types[field_name] = type_name
            elif isinstance(field_types[field_name], str):
                if field_types[field_name] != type_name:
                    # Convert to list if we find a different type
                    field_types[field_name] = [field_types[field_name], type_name]
            elif isinstance(field_types[field_name], list):
                if type_name not in field_types[field_name]:
                    field_types[field_name].append(type_name)