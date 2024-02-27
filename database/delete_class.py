import weaviate

# Replace with your Weaviate instance URL
client = weaviate.Client("http://localhost:8080")

class_name = "Organisations"  # The name of the class you want to delete

try:
    client.schema.delete_class(class_name)
    print(f"Class '{class_name}' deleted successfully.")
except Exception as e:
    print(f"Failed to delete class '{class_name}': {e}")