import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.config import Configure
import os
from dotenv import load_dotenv

load_dotenv()

weaviate_url = os.environ["WEAVIATE_URL"]
weaviate_api_key = os.environ["WEAVIATE_API_KEY"]
openai_key = os.getenv("OPENAI_APIKEY")

# Connect to your Weaviate instance
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
    headers={
        "X-OpenAI-Api-Key": openai_key
    }
)

# Get the existing collection
collection = client.collections.get("Hoch_Menu_Test")

# Update the collection to add generative capabilities
try:
    collection.config.update(
        generative_config=Configure.Generative.openai(
            model="gpt-4o-mini"
        )
    )
    print("Successfully added generative capabilities to the collection")
except Exception as e:
    print(f"Error updating collection: {e}")

# Close the client
client.close()