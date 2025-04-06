import weaviate
from weaviate.classes.init import Auth
import os
from weaviate.classes.config import Configure
from dotenv import load_dotenv
import json

load_dotenv()  # Load environment variables from .env file

weaviate_url = os.environ["WEAVIATE_URL"]
weaviate_api_key = os.environ["WEAVIATE_API_KEY"]
openai_key = os.getenv("OPENAI_APIKEY")
print("weaviate_url ",weaviate_url)
print(weaviate_api_key)

headers = {
    "X-OpenAI-Api-Key": openai_key,
}

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
    headers=headers
    
)

# Check if collection exists before creating it
if "Mock_Menu" not in client.collections.list_all():
    client.collections.create(
        "Mock_Menu",
        vectorizer_config=[
            Configure.NamedVectors.text2vec_openai(
                name="menu_item_vector",
                source_properties=["menu_item"],
                # If using `text-embedding-3` model family
                model="text-embedding-3-small",
                dimensions=512 
            )
        ],
    )

# reading in the json file and adding it to the weaviate db
with open('mock_menu_data.json', 'r') as f:
    menu_data = json.load(f)

collection = client.collections.get("Mock_Menu")

with collection.batch.dynamic() as batch:
    for src_obj in menu_data:
        # Create a list of labels extracted from each item
        labels = []
        for item in src_obj["items"]:
            # Here, we're taking 'category' and 'meal_station' as labels.
            labels.append({
                "name": item["name"],
                "category": item["category"],
                "meal_station": item["meal_station"],
                "nutrition": item["nutrition"]
            })
        
        # Add the object with the original items and the extracted labels.
        batch.add_object(
            properties={
                "date": src_obj["date"],
                "dining_hall": src_obj["dining_hall"],
                "meal": src_obj["meal"],
                "items": src_obj["items"],
                "labels": labels  # New field with extracted labels
            }
        )
        
        if batch.number_errors > 10:
            print("Batch import stopped due to excessive errors.")
            break

failed_objects = collection.batch.failed_objects
if failed_objects:
    print(f"Number of failed imports: {len(failed_objects)}")
    print(f"First failed object: {failed_objects[0]}")

client.close()  # Free up resources
