import chromadb
from utils.embedding import huggingface_ef

chroma_client = chromadb.HttpClient(host='localhost', port=8000)
collection = chroma_client.get_collection(name="FAQ", embedding_function=huggingface_ef)

# query = input("Enter the question: ")

# results = collection.query(
#     query_texts=query,
#     n_results=2
# )
# print(results)

print(collection.peek())