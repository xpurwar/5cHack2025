import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.config import Configure
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

weaviate_url = os.environ["WEAVIATE_URL"]
weaviate_api_key = os.environ["WEAVIATE_API_KEY"]
openai_key = os.getenv("OPENAI_APIKEY")
print("weaviate_url ",weaviate_url)
print(weaviate_api_key)

# Configure the client with the OpenAI integration
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
    headers={
        "X-OpenAI-Api-Key": openai_key
    }
)

collection = client.collections.get("Mock_Menu")
# testing the vector database 
# agg = questions.aggregate.over_all()
# print(agg)
# response = questions.query.fetch_objects(
#     include_vector=True,
#     limit=1
# )
# print(response.objects[0].properties)
# print(response.objects[0].vector["default"])

response = collection.generate.near_text(
    query="vegetarian protein meal",
    single_prompt="Suggest the {items[0].name} from {dining_hall} as a meal option. Include its nutritional benefits, especially protein content of {items[0].nutrition.protein}g, and why it's a good vegetarian choice.",
    limit=1
)

for obj in response.objects:
    print(f"Suggestion: {obj}")
client.close()