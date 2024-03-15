import os
from pymongo import MongoClient
from dotenv import load_dotenv
from utils.embedding import huggingface_ef
import chromadb

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
documents = collection.find({
    "parent_id": 2565
})

# Print the question-answer pairs
collection_object = {
    "documents": [],
    "embeddings": [],
    "metadatas": [],
    "ids": []
}
for document in documents:
    collection_object["documents"].append(document["description"])
    collection_object["metadatas"].append({
        "orgCode": document["orgCode"],
        "stage": document["stage"],
        "parent_id": document["parent_id"],
        "hinDescription": document["descriptionHindi"]
    })
    collection_object["ids"].append(str(document["_id"]))
    print(f"Department {document['_id']}: {document['_id']}")

client = chromadb.HttpClient(host="localhost", port=8000)
collection = client.get_collection(name="Departments", embedding_function=huggingface_ef)

collection.add(
    documents=collection_object["documents"],
    metadatas=collection_object["metadatas"],
    ids=collection_object["ids"]
)