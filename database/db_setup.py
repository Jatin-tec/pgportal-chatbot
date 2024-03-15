import chromadb.utils.embedding_functions as embedding_functions
import chromadb
from utils.embedding import huggingface_ef

chroma_client = chromadb.HttpClient(host='localhost', port=8000)

class_name = "FAQ"  
emb_fn = huggingface_ef

try:
    # Create a new collection
    collection = chroma_client.create_collection(name=class_name, embedding_function=emb_fn)
    collection = chroma_client.get_collection(name=class_name)
    print(f"Collection {class_name} created successfully.")
    print(f"Collection: {collection}")
except Exception as e:
    print(f"Failed to create collection {class_name}: {e}")

