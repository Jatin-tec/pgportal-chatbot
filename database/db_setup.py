import argparse
import chromadb.utils.embedding_functions as embedding_functions
import chromadb
from utils.embedding import huggingface_ef

# Initialize parser
parser = argparse.ArgumentParser(description='Create collections in Chroma DB.')
# Add arguments for class names. We use nargs='+' to accept multiple class names
parser.add_argument('classnames', type=str, nargs='+', help='Names of the classes (collections) to create')

# Parse the command line arguments
args = parser.parse_args()

chroma_client = chromadb.HttpClient(host='localhost', port=8000)
emb_fn = huggingface_ef

# Loop through each class name provided and create the collection
for class_name in args.classnames:
    try:
        # Create a new collection
        collection = chroma_client.create_collection(name=class_name, embedding_function=emb_fn)
        collection = chroma_client.get_collection(name=class_name)
        print(f"Collection {class_name} created successfully.")
        print(f"Collection: {collection}")
    except Exception as e:
        print(f"Failed to create collection {class_name}: {e}")
