import weaviate
import os
from dotenv import load_dotenv

load_dotenv()
huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")

client = weaviate.Client(
    url="http://localhost:8080",
    additional_headers={
        "X-HuggingFace-Api-Key": huggingface_api_key
    }
)

batch_size = 10000
class_name = "FAQ"
# class_properties = ['__id', 'orgCode', 'description']
cursor = None

query = (
    client.query.get(class_name)
    .with_additional(["id vector"])
    .with_limit(batch_size)
)
print(len(query.do()["data"]["Get"][class_name]))
