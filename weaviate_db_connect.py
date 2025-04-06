import weaviate
from weaviate.classes.init import Auth
import os
from weaviate.classes.config import Configure
from dotenv import load_dotenv

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


client.close()  # Free up resources