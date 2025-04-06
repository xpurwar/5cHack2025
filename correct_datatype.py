import weaviate
from weaviate.classes.init import Auth
import os
from weaviate.classes.config import Configure
from dotenv import load_dotenv
from weaviate.classes.config import Property, DataType
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

collection_name = "Hoch_Menu_Test"

client.collections.delete(collection_name)  # Optional: if re-creating from scratch

collection = client.collections.create(
    name=collection_name,
    description="Dining hall meals with nutrition info",
    properties=[
        Property(name="dining_hall", data_type=DataType.TEXT),
        Property(name="date", data_type=DataType.TEXT),
        Property(name="day", data_type=DataType.TEXT),
        Property(name="meal", data_type=DataType.TEXT),
        Property(name="station", data_type=DataType.TEXT),
        Property(name="name", data_type=DataType.TEXT),
        Property(name="cal", data_type=DataType.TEXT),
        Property(name="allergens", data_type=DataType.TEXT_ARRAY),
        Property(name="diets", data_type=DataType.TEXT_ARRAY),
    ],
    vectorizer_config=Configure.Vectorizer.text2vec_openai(),  # You’re using `generate`, so vectorizer is needed
    generative_config=Configure.Generative.openai()
)

# reading in the json file and adding it to the weaviate db
with open('hoch_food_items.json', 'r') as f:
    menu_data = json.load(f)

collection = client.collections.get("Hoch_Menu_Test")

with collection.batch.dynamic() as batch:
    for src_obj in menu_data:
        # Add the object with the original items and the extracted labels.
        batch.add_object(
            properties={
                "dining_hall": src_obj["dining_hall"],
                "date": src_obj["date"],
                "day": src_obj["day"],
                "meal": src_obj["meal"],
                "station": src_obj["station"],
                "name": src_obj["name"],    
                "cal": src_obj["cal"],
                # "allergens": src_obj["allergens"],
                # "diets": src_obj["diets"]   
            }
        )

        if batch.number_errors > 10:
            print("Batch import stopped due to excessive errors.")
            break

failed_objects = collection.batch.failed_objects
if failed_objects:
    print(f"Number of failed imports: {len(failed_objects)}")
    print(f"First failed object: {failed_objects[0]}")

print("Collection created successfully")

client.close()  # Free up resources
