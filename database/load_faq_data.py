import os
from dotenv import load_dotenv
import weaviate
import re

load_dotenv()

client = weaviate.Client(
    url="http://localhost:8080",
    additional_headers={
        # Replace with your inference API key
        "X-HuggingFace-Api-Key": os.getenv("HUGGINGFACE_API_KEY")
    }
)

data = ""
# read data from file
with open('database/web_data.txt', 'r', encoding='utf-8') as file:
    data = file.read()

pairs = data.strip().split("\n\n")

# Print the question-answer pairs
weaviate_objs = []
for qa_pair in pairs:
    weaviate_obj = {
        "qna": qa_pair
    }
    weaviate_objs.append(weaviate_obj)

client.batch.configure(batch_size=10) 
with client.batch as batch:
    for data_obj in weaviate_objs:
        batch.add_data_object(
            data_obj,
            "FAQ",
        )
