import weaviate
from weaviate.classes.init import Auth, AdditionalConfig, Timeout
from weaviate.classes.config import Configure
import os

# Best practice: store your credentials in environment variables
wcd_url = os.environ["WEAVIATE_URL"]
wcd_api_key = os.environ["WEAVIATE_API_KEY"]
cohere_api_key = os.environ["COHERE_APIKEY"]

client = weaviate.connect_to_weaviate_cloud(
   cluster_url=wcd_url,
   auth_credentials=Auth.api_key(wcd_api_key),
   headers={"X-Cohere-Api-Key": cohere_api_key},
   additional_config=AdditionalConfig(
       timeout=Timeout(init=30, query=60, insert=120)  # Increased timeout values in seconds
   )
)

questions = client.collections.get("Hoch_Menu_Test")
# testing the vector database 
# agg = questions.aggregate.over_all()
# print(agg)
# response = questions.query.fetch_objects(
#     include_vector=True,
#     limit=1
# )
# print(response.objects[0].properties)
# print(response.objects[0].vector["default"])

response = questions.generate.near_text(
    query="A protein meal with low calories",
    limit=1,
    grouped_task="You are a helpful assistant that suggests meals based on the user's preferences."
)

print(response)  # Inspect the generated text

client.close()