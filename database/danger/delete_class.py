import chromadb

client = chromadb.HttpClient(host='localhost', port=8000)

class_name = "Departments"  # The name of the class you want to delete

try:
    client.delete_collection(name=class_name)
    print(f"Class '{class_name}' deleted successfully.")
except Exception as e:
    print(f"Failed to delete class '{class_name}': {e}")