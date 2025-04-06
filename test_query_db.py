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

collection = client.collections.get("Hoch_Menu_Test")
# testing the vector database 
# agg = questions.aggregate.over_all()
# print(agg)
# response = questions.query.fetch_objects(
#     include_vector=True,
#     limit=1
# )
# print(response.objects[0].properties)
# print(response.objects[0].vector["default"])

#this works: output is a json object
# response = collection.query.near_text(
#     query="a meal with fruits",  # The model provider integration will automatically vectorize the query
#     limit=1
# )

# for obj in response.objects:
#     print(f"Suggestion: {obj}")

#this works: output is a the name of the meal 
# response = collection.query.hybrid(
#     query="A vegetarian protein meal with low calories",  # The model provider integration will automatically vectorize the query
#     limit=2
# )

# for obj in response.objects:
#     print(obj.properties["name"], obj.properties["dining_hall"], obj.properties["cal"])

# response = collection.generate.near_text(
#     query="A protein meal",  # The model provider integration will automatically vectorize the query
#     grouped_task="Describe this meal option.",
#     limit=2
# )

# print(f"Generated output: {response}")  # Note that the generated output is per query
# for obj in response.objects:
#     print(obj.properties["name"])
response = collection.generate.near_text(
    query="I am in the mood for asian food today",
    grouped_task="You are a helpful assistant that suggests meals based on the user's preferences. Based on these menu items. Include the dining hall, nutritional information, and why it's a good choice, encourage the user to try plant based options.",
    limit=1
)
print(response.generative.text)
client.close()