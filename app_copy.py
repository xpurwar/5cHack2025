import streamlit as st
from datetime import datetime, timedelta 
from calendar import monthrange
import json
import os
import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.config import Configure
import os
from dotenv import load_dotenv
from html import escape

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


with open("hoch_menus.json", "r") as f:
    data = json.load(f)
    
st.markdown(
    """
    <style>
    body {
        background-color: #F8F4EF !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f'<style>{open(os.path.join(".streamlit", "styles.css")).read()}</style>',
    unsafe_allow_html=True
)

# st.title(":red[5C Dining Healthy Menu Search] :knife_fork_plate: :wine_glass:")
st.markdown(
    '<h1 style="color:#b68958;">5C Dining Healthy Menu Search 🍴 🍷</h1>',
    unsafe_allow_html=True
)

# Sidebar
st.sidebar.header("5C Campus Dining")
dining_halls = [
    "Frank (Pomona College)",
    "Frary (Pomona College)",
    # "Oldenborg (Pomona College)",
    "Collins (Claremont McKenna College)",
    "McConell (Pitzer College)",
    "Mallot (Scripps College)",
    "Hoch (Harvey Mudd College)"
]

# Create buttons in a row using columns
cols = st.columns(len(dining_halls))
for i, hall in enumerate(dining_halls):
    if cols[i].button(hall):
        st.session_state.hall_select = hall
# Set a default
if "hall_select" not in st.session_state:
    st.session_state.hall_select = dining_halls[-1]  # default to Hoch
hall_select = st.session_state.hall_select

meal_stations = {"frank": ["Expo Station", "Desserts", "Mainline", "Pizza", "Grill Station", "Salad Bar", "Soup Station"],
                "frary": ["Expo Station", "Desserts", "Grill Station ", "Mainline", "Pizza", "Salad Bar", "Soup Station"],
                "oldenborg": ["Panini Station", "Mainline", "Pizza", "Salad Bar", "Soup Station"],
                "collins": ["@home", "Options", "Grill Station", "Stock Pot", "Ovens", "Expo Station", "PLant Forward"],
                "mcconell_breakfast": ["Global", "Hot Cereal"],
                "mcconell": ["Comfort", "Herbivore", "Stocks"],
                "mallot_breakfast": ["Herbivore", "Global", "Salad", "Soup", "Sweets"],
                "mallot": ["Grill", "Herbivore", "Global", "Oasis", "Salad", "Ovens", "Soup", "Sweets"],
                "hoch_breakfast": ["Bakery", "Exhibition", "Grill", "HMC Special Salad", "Salad Bar Yogurt"],
                "hoch": ["bakery", "exhibit", "grill", "hmc special salad", "grown plant", "oven", "salad bar yogurt", "simple servings", "soup bar", "chef corner"]
                }
  




# --- SIDEBAR CHATBOT ---
with st.sidebar.expander("💬 Chat with DiningBot", expanded=True):
    # Inject custom styles
    st.markdown("""
        <style>
        .user-msg {
            color: #F8F4EF;
            font-weight: 500;
            margin-bottom: 0.5rem;
        }
        .bot-msg {
            color: #e4d3c0;
            font-weight: 500;
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Input field (always stays at the bottom)
    prompt = st.chat_input("Ask about meals, nutrition, or dining...")
    
    # Process new user input
    if prompt:
        # Store user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Process with Weaviate
        response = collection.generate.near_text(
            query = prompt,
            grouped_task = "You are a helpful assistant that suggests meals based on the user's preferences. Based on these menu items. Include the dining hall, nutritional information, and why it's a good choice, encourage the user to try plant based options.",
            limit = 1
        )
        
        # Extract and store assistant response
        bot_reply = response.generative.text
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
        # Force refresh to show new messages immediately
        st.rerun()
    
    # Display all messages (after potentially updating them)
    for message in st.session_state.messages:
        css_class = "user-msg" if message["role"] == "user" else "bot-msg"
        st.markdown(f"<div class='{css_class}'>{message['content']}</div>", unsafe_allow_html=True)



                   
def meal_station_caption(s):
   for i in range(len(meal_stations[s])):
       st.markdown(
            f'<div style="color:#b68958; font-size:1.25rem; font-weight:bold; font-family:serif;">{meal_stations[s][i]}</div>',
            unsafe_allow_html=True
        )
   st.divider()

def render_food_item(item):
    name = escape(item["name"])
    cal = escape(item["cal"])
    
    diets = item["diets"]
    allergens = item["allergens"]
    
    diet_html = f'<div>🥗 <span style="color: #b68958">{", ".join(diets)}</span></div>' if diets else ""
    allergen_html = f'<div>⚠️ <span style="color: #b68958">{", ".join(allergens)}</span></div>' if allergens else ""
    
    return f"""
    <div style="border: 1px solid #eee; border-radius: 10px; padding: 8px; margin-bottom: 8px;">
      <div style="display: flex; justify-content: space-between; align-items: baseline;">
        <div style="color: #b68958;"><strong>{name}</strong></div>
        <div style="font-size: 0.9em; color: gray;">{cal}</div>
      </div>
      {diet_html}
      {allergen_html}
    </div>
    """

def display_menu_items_for_station(hall, station, meal, selected_date):
    # Filter data for selected dining hall, date, and meal
    for entry in data:
        if (entry["dining_hall"].lower() == hall.lower() and
            entry["meal"].lower() == meal.lower() and
            entry["date"] == selected_date):

            # Get items for this station
            items = entry["stations"].get(station.lower(), [])
            if not items:
                st.write("No items listed for this station.")
            else:
                for item in items:
                    st.markdown(render_food_item(item), unsafe_allow_html=True)

            return  # done, exit early
    st.write("No menu data found for this station.")

# Meals Tabs
tabs = st.tabs(["🍳 Breakfast (7:30 AM - 9:30 AM)", "🥗 Lunch (11:15 AM - 1:00 PM)", "🍝 Dinner (5:00 PM - 7:00 PM)"])
meal_names = ["breakfast", "lunch", "dinner"]

# Dates Buttons
available_dates = ("2025-04-05", "2025-04-06", "2025-04-07", "2025-04-08", "2025-04-09", "2025-04-10", "2025-04-11", )

date_cols = st.columns(len(available_dates))
for i, date_str in enumerate(available_dates):
    if date_cols[i].button(date_str):
        st.session_state.selected_date = date_str

if "selected_date" not in st.session_state:
    st.session_state.selected_date = available_dates[-1]  # default to the most recent
selected_date = st.session_state.selected_date

# Display of Menus

if hall_select == "Hoch (Harvey Mudd College)":
    selected_date = "2025-04-11" 
    for i, meal in enumerate(meal_names):
        with tabs[i]:
            station_list = meal_stations["hoch"]
            for station in station_list:
                st.markdown(f"<h4 class='station-header'>{station}</h4>", unsafe_allow_html=True)
                display_menu_items_for_station("Hoch", station, meal, selected_date)
                st.divider()

if hall_select == "Frank (Pomona College)":
    selected_date = "2025-04-09" 
    for i, meal in enumerate(meal_names):
        with tabs[i]:
            station_list = meal_stations["hoch"]
            for station in station_list:
                st.markdown(f"<h4 class='station-header'>{station}</h4>", unsafe_allow_html=True)
                display_menu_items_for_station("Hoch", station, meal, selected_date)
                st.divider()


if hall_select == "Frary (Pomona College)":
    selected_date = "2025-04-07" 
    for i, meal in enumerate(meal_names):
        with tabs[i]:
            station_list = meal_stations["hoch"]
            for station in station_list:
                st.markdown(f"<h4 class='station-header'>{station}</h4>", unsafe_allow_html=True)
                display_menu_items_for_station("Hoch", station, meal, selected_date)
                st.divider()

if hall_select == "Collins (Claremont McKenna College)":
    selected_date = "2025-04-08" 
    for i, meal in enumerate(meal_names):
        with tabs[i]:
            station_list = meal_stations["hoch"]
            for station in station_list:
                st.markdown(f"<h4 class='station-header'>{station}</h4>", unsafe_allow_html=True)
                display_menu_items_for_station("Hoch", station, meal, selected_date)
                st.divider()

if hall_select == "McConell (Pitzer College)":
    selected_date = "2025-04-09" 
    for i, meal in enumerate(meal_names):
        with tabs[i]:
            station_list = meal_stations["hoch"]
            for station in station_list:
                st.markdown(f"<h4 class='station-header'>{station}</h4>", unsafe_allow_html=True)
                display_menu_items_for_station("Hoch", station, meal, selected_date)
                st.divider()
    
if hall_select == "Mallot (Scripps College)":
    selected_date = "2025-04-10" 
    for i, meal in enumerate(meal_names):
        with tabs[i]:
            station_list = meal_stations["hoch"]
            for station in station_list:
                st.markdown(f"<h4 class='station-header'>{station}</h4>", unsafe_allow_html=True)
                display_menu_items_for_station("Hoch", station, meal, selected_date)
                st.divider()



# if hall_select == "Hoch (Harvey Mudd College)":
#     st.markdown(
#     '<h2 style="color:#b68958;">Hoch (Harvey Mudd College)</h2>',
#     unsafe_allow_html=True
#     )
#     # date_buttons()
#     with st.container():
#         st.divider()
#         with st.expander("Breakfast 7:30 AM - 9:30 AM"):
#             # meal_station_caption("hoch_breakfast")
#             for station in meal_stations["hoch_breakfast"]:
#                 st.markdown(f"<h3 style='color: #b68958'>{station}</h3>", unsafe_allow_html=True)
#                 display_menu_items_for_station("Hoch", station, "breakfast")
#                 st.divider()
#         with st.expander("Lunch 11:15 AM - 1:00 PM"):
#             # meal_station_caption("hoch")
#             for station in meal_stations["hoch"]:
#                 st.markdown(f"<h3 style='color: #b68958'>{station}</h3>", unsafe_allow_html=True)
#                 display_menu_items_for_station("Hoch", station, "lunch")
#                 st.divider()
#         with st.expander("Dinner 5:00 PM - 7:00 PM"):
#             # meal_station_caption("hoch")
#             for station in meal_stations["hoch"]:
#                 st.markdown(f"<h3 style='color: #b68958'>{station}</h3>", unsafe_allow_html=True)
#                 display_menu_items_for_station("Hoch", station, "dinner")
#                 st.divider()


# if hall_select == "Frank (Pomona College)":
#    st.markdown(
#     '<h2 style="color:#b68958;">Frank Dining Hall (Pomona College)</h2>',
#     unsafe_allow_html=True
#     )
#    # date_buttons()
#    with st.container():
#         st.divider()
#         with st.expander("Breakfast 7:30 AM - 9:30 AM", expanded=False):
#             st.markdown(
#             '<div style="color:#b68958; font-size:1.5rem; font-weight:bold;">Breakfast 7:30 AM - 9:30 AM</div>',
#             unsafe_allow_html=True
#             )
#             meal_station_caption("frank")
#         with st.expander("Lunch 10:30 AM - 1:30 PM"):
#             meal_station_caption("frank")
#         with st.expander("Dinner 5:00 PM - 7:30 PM"):
#             meal_station_caption("frank")


# if hall_select == "Frary (Pomona College)":
#     st.markdown(
#     '<h2 style="color:#b68958;">Frary Dining Hall (Pomona College)</h2>',
#     unsafe_allow_html=True
#     )
#     # date_buttons()
#     with st.container():
#         st.divider()
#         with st.expander("Breakfast 7:30 AM - 10:00 AM"):
#             meal_station_caption("frary")
#         with st.expander("Lunch 11:00 AM - 1:30 PM"):
#             meal_station_caption("frary")
#         with st.expander("Dinner 5:00 PM - 7:30 PM"):
#             meal_station_caption("frary")

# if hall_select == "Oldenborg (Pomona College)":
#     st.markdown(
#     '<h2 style="color:#b68958;">Oldenborg Dining Hall (Pomona College)</h2>',
#     unsafe_allow_html=True
#     )
#     # date_buttons()
#     with st.container():
#         st.divider()
#         with st.expander("Lunch 12:00 PM - 1:00 PM"):
#             meal_station_caption("oldenborg")

# if hall_select == "Collins (Claremont McKenna College)":
#     st.markdown(
#     '<h2 style="color:#b68958;">Frank Dining Hall (Pomona College)</h2>',
#     unsafe_allow_html=True
#     )
#     # date_buttons()
#     with st.container():
#         st.divider()
#         with st.expander("Breakfast 7:30 AM - 9:30 AM"):
#             meal_station_caption("collins")
#         with st.expander("Lunch 11:00 AM - 1:00 PM"):
#             meal_station_caption("collins")
#         with st.expander("Dinner 5:00 PM - 7:00 PM"):
#             meal_station_caption("collins")

# if hall_select == "McConell (Pitzer College)":
#     st.markdown(
#     '<h2 style="color:#b68958;">McConell (Pitzer College)</h2>',
#     unsafe_allow_html=True
#     )
#     # date_buttons()
#     with st.container():
#         st.divider()
#         with st.expander("Breakfast 7:45 AM - 10:00 AM"):
#             meal_station_caption("mcconell_breakfast")
#         with st.expander("Lunch 11:00 AM - 1:30 PM"):
#             meal_station_caption("mcconell")
#         with st.expander("Dinner 5:00 PM - 7:30 PM"):
#             meal_station_caption("mcconell")
    
# if hall_select == "Mallot (Scripps College)":
#     st.markdown(
#     '<h2 style="color:#b68958;">Mallot (Scripps College)</h2>',
#     unsafe_allow_html=True
#     )
#     # date_buttons()
#     with st.container():
#         st.divider()
#         with st.expander("Breakfast 7:30 AM - 10:00 AM"):
#             meal_station_caption("mallot_breakfast")
#         with st.expander("Lunch 11:00 AM - 2:00 PM"):
#             meal_station_caption("mallot")
#         with st.expander("Dinner 5:00 PM - 7:15 PM"):
#             meal_station_caption("mallot")
