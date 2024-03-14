import os
import weaviate
import json
from dotenv import load_dotenv

load_dotenv()
huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")

client = weaviate.Client(
    url="http://localhost:8080",
    additional_headers={
        # Replace with your inference API key
        "X-HuggingFace-Api-Key": huggingface_api_key
    }
)

# Create Organisations class
# class_obj = {
#     "class": "Organisations",
#     "vectorizer": "text2vec-huggingface",
#     "description": "Organisation description",

#     "moduleConfig": {
#         "text2vec-huggingface": {
#             "model": "google/muril-large-cased",
#             "options": {
#                 "waitForModel": True
#             }
#         }
#     },
#     "properties": [
#         {
#             "dataType": ["text"],
#             "description": "__id",
#             "name": "__id",
#         },
#         {
#             "dataType": ["text"],
#             "description": "Organisation Code",
#             "name": "orgCode",
#         },
#         {
#             "dataType": ["text"],
#             "description": "Stage",
#             "name": "stage",
#         },
#         {
#             "dataType": ["text"],
#             "description": "Parent id",
#             "name": "parent_id",
#         },
#         {
#             "dataType": ["text"],
#             "description": "English Description",
#             "moduleConfig": {
#                 "text2vec-huggingface": {
#                     "vectorizePropertyName": True
#                 }
#             },
#             "name": "description",
#         },
#         {
#             "dataType": ["text"],
#             "description": "Hindi Description",
#             "moduleConfig": {
#                 "text2vec-huggingface": {
#                     "vectorizePropertyName": True
#                 }
#             },
#             "name": "hinDescription",
#         },
#     ],
#     "vectorIndexType": "hnsw",
# }

faq_obj = {
    "class": "FAQ",
    "vectorizer": "text2vec-huggingface",
    "description": "FAQ's",

    "moduleConfig": {
        "text2vec-huggingface": {
            "model": "ai4bharat/IndicBART",
            "options": {
                "waitForModel": True
            }
        }
    },
    "properties": [
        {
            "dataType": ["text"],
            "description": "Question Answer",
            "moduleConfig": {
                "text2vec-huggingface": {
                    "vectorizePropertyName": True
                }
            },
            "name": "qna",
        },
    ],
    "vectorIndexType": "hnsw",
}

client.schema.create_class(faq_obj)
# client.schema.create_class(faq_obj)

# data = (client.query.get("Organisations", ["description", "hinDescription"])
#         .with_near_text({"concepts": ["Jatin Kshatriya"]})
#         .with_limit(1)
#         ).do()

# print(data)
