import os
import multiprocessing
from pymongo import MongoClient
from dotenv import load_dotenv
import weaviate
from itertools import islice
import time

load_dotenv()

# MongoDB connection details
mongo_connection_string = 'mongodb://rootuser:rootpass@localhost:27017/?authSource=admin'
database_name = 'gov'

# Connect to MongoDB
client = MongoClient(mongo_connection_string)
db = client[database_name]

# Select the departments collection
collection = db['departments']

# Fetch all documents from the collection
documents = list(collection.find({}))

API_KEYS = os.getenv("HUGGINGFACE_APIKEYS").split(" ")  # Assuming your API keys are space-separated

# Function to read the progress log for a worker or create it if it doesn't exist
def read_progress(worker_id):
    log_file_path = f"database/logs/worker_{worker_id}_progress.log"
    try:
        with open(log_file_path, "r") as file:
            uploaded_ids = file.read().splitlines()
        return set(uploaded_ids)
    except FileNotFoundError:
        # If the file doesn't exist, create it and then return an empty set
        with open(log_file_path, "w") as file:
            pass  # Create an empty file
        return set()

# Function to log a successfully uploaded document ID for a worker
def log_progress(worker_id, document_id):
    with open(f"database/logs/worker_{worker_id}_progress.log", "a") as file:
        file.write(f"{document_id}\n")

# Worker function to upload documents
def upload_documents(doc_chunk, api_key_index):
    uploaded_ids = read_progress(api_key_index)
    API_TOKEN = API_KEYS[api_key_index]

    client = weaviate.Client(
        url="http://localhost:8080",
        additional_headers={
            "X-HuggingFace-Api-Key": API_TOKEN
        }
    )

    client.batch.configure(batch_size=10)
    for document in doc_chunk:
        document_id = str(document["_id"])
        if document_id in uploaded_ids:
            print(f"Document {document_id} already uploaded. Skipping.")
            continue  # Skip this document
        
        # Prepare the document for upload
        weaviate_obj = {
            "__id": document_id, 
            "orgCode": str(document.get("orgCode", "")),
            "stage": str(document.get("stage", "")),
            "parent_id": str(document.get("parent_id", "-1")),
            "description": str(document.get("description", "")),
            "hinDescription": str(document.get("descriptionHindi", ""))
        }
        
        # Upload document with error handling
        try:
            with client.batch as batch:
                batch.add_data_object(weaviate_obj, "Organisations")
                log_progress(api_key_index, document_id)  # Log successful upload
            print(f"Successfully uploaded document {weaviate_obj['__id']}")
            time.sleep(1)
        except Exception as e:
            print(f"Error uploading document {weaviate_obj['__id']}: {e}")
            # Optionally, implement retry logic here

    print(f"Process {api_key_index} uploaded {len(doc_chunk)} documents")

# Split documents into chunks for multiprocessing
def chunks(data, n):
    """Yield successive n-sized chunks from data."""
    for i in range(0, len(data), n):
        yield data[i:i + n]

# Divide documents into equally sized chunks based on the number of CPU cores
num_chunks = multiprocessing.cpu_count()
documents_per_chunk = len(documents) // num_chunks
doc_chunks = list(chunks(documents, documents_per_chunk))

# Use context manager for the pool to ensure proper closure
with multiprocessing.Pool(processes=num_chunks) as pool:
    # Assign each chunk of documents to a worker process
    for i, chunk in enumerate(doc_chunks):
        pool.apply_async(upload_documents, args=(chunk, i % len(API_KEYS)))

    pool.close()
    pool.join()

# Close the MongoDB connection
client.close()
