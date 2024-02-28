import os
from pymongo import MongoClient
from dotenv import load_dotenv
import weaviate

load_dotenv()

# MongoDB connection details
mongo_connection_string = 'mongodb://rootuser:rootpass@localhost:27017/?authSource=admin'  # Update with your connection string
database_name = 'gov'

# Connect to MongoDB
client = MongoClient(mongo_connection_string)
db = client[database_name]

# Select the departments collection
collection = db['departments']

# Fetch all documents from the collection
documents = collection.find({})
# print(documents)

weaviate_objs = []
# Print each document
for document in documents:
    try:
        weaviate_obj = {
            # Map your MongoDB document fields to your Weaviate class properties here
            "__id": str(document["_id"]), 
            "orgCode": str(document["orgCode"]),
            "stage": str(document["stage"]),
            "parent_id": str(document["parent_id"]),
            "description": str(document["description"]),
            "hinDescription": str(document["descriptionHindi"])
        }
    except:
        weaviate_obj = {
            # Map your MongoDB document fields to your Weaviate class properties here
            "__id": str(document["_id"]), 
            "orgCode": str(document["orgCode"]),
            "stage": str(document["stage"]),
            "parent_id": "-1",
            "description": str(document["description"]),
            "hinDescription": str(document["descriptionHindi"])
        }
    weaviate_objs.append(weaviate_obj)

# Close the MongoDB connection
client.close()

API_TOKEN = os.getenv("HUGGINGFACE_APIKEY")

client = weaviate.Client(
    url="http://localhost:8080",
    additional_headers={
        "X-HuggingFace-Api-Key": API_TOKEN
    }
)

client.batch.configure(batch_size=10) 
with client.batch as batch:
    for data_obj in weaviate_objs:
        batch.add_data_object(
            data_obj,
            "Organisations",
        )
