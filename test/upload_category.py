import pandas as pd
from pymongo import MongoClient

# MongoDB connection details
mongo_connection_string = 'mongodb://rootuser:rootpass@localhost:27017/?authSource=admin'  # Update with your connection string
database_name = 'gov'
collection_name = 'departments'

# Path to the Excel file
excel_file_path = '/home/jatin/Documents/problem_statement_1_and_2/CategoryCode_Mapping_v2.xlsx'

# Read the Excel file
df = pd.read_excel(excel_file_path, sheet_name="Sheet2")

# Rename columns and select specific fields
df.rename(columns={'Code': '_id', 'Parent': 'parent_id', 'Description': 'description', 'Stage': 'stage', 'DescriptionHindi': 'descriptionHindi', 'OrgCode': 'orgCode'}, inplace=True)
df = df[['_id', 'description', 'orgCode', 'parent_id', 'stage', 'descriptionHindi']]

# Connect to MongoDB
client = MongoClient(mongo_connection_string)
db = client[database_name]
collection = db[collection_name]

# Convert the DataFrame to a list of dictionaries (suitable for MongoDB)
data = df.to_dict('records')
# print(data)

# Insert the data into the MongoDB collection
collection.insert_many(data)

print(f"Successfully inserted {len(data)} records into MongoDB.")

# Close the MongoDB connection
client.close()
