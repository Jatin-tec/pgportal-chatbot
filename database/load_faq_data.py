import chromadb
from utils.embedding import huggingface_ef

chroma_client = chromadb.HttpClient(host='localhost', port=8000)
collection = chroma_client.get_collection(name="FAQ", embedding_function=huggingface_ef)

data = ""
# read data from file
with open('database/web_data.txt', 'r', encoding='utf-8') as file:
    data = file.read()

pairs = data.strip().split("\n\n")

# Print the question-answer pairs
collection_object = {
    "documents": [],
    "embeddings": [],
    "ids": []
}

for index, pair in enumerate(pairs):
    collection_object["documents"].append(pair)
    collection_object["ids"].append(str(index))
    print(f"Pair {index + 1}: {pair}")

collection.add(
    documents=collection_object["documents"],
    ids=collection_object["ids"]
)
