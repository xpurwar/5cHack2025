import requests
from bs4 import BeautifulSoup
import json

# URL for the dining hall menu
url = "https://hmc.sodexomyway.com/en-us/locations/hoch-shanahan-dining-commons"

# Set headers to mimic a real browser (helps if the site blocks bots)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
                  "(KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
}

# Fetch the page content
response = requests.get(url, headers=headers)
if response.status_code != 200:
    print("Error fetching page:", response.status_code)
    exit()

soup = BeautifulSoup(response.text, "html.parser")

# Prepare a dictionary to hold the menu data
menu_data = {}

# Assuming the page is divided into meal sections (e.g., Breakfast, Lunch, Dinner)
# You'll need to update the selectors based on the actual HTML structure.
meal_sections = soup.find_all("div", class_="menu-section")  # Update this selector

for section in meal_sections:
    # Extract the meal name, e.g., "Breakfast" or "Dinner"
    meal_name_elem = section.find("h2")  # Update if needed
    if not meal_name_elem:
        continue
    meal_name = meal_name_elem.get_text(strip=True)
    menu_data[meal_name] = []

    # Find all menu items within this meal section
    menu_items = section.find_all("div", class_="menu-item")  # Update this selector
    for item in menu_items:
        item_data = {}

        # Extract the item name
        name_elem = item.find("div", class_="item-name")  # Update this selector
        if name_elem:
            item_data["name"] = name_elem.get_text(strip=True)
        else:
            item_data["name"] = "Unknown"

        # Extract nutrition information container
        nutrition_elem = item.find("div", class_="nutrition-info")  # Update this selector
        if nutrition_elem:
            # Example: Extract calories
            calorie_elem = nutrition_elem.find("span", class_="calories")  # Update selector
            if calorie_elem:
                item_data["calories"] = calorie_elem.get_text(strip=True)
            else:
                item_data["calories"] = "N/A"

            # Extract any labels like vegan, gluten free, etc.
            label_elems = nutrition_elem.find_all("span", class_="label")  # Update selector
            labels = [label.get_text(strip=True) for label in label_elems]
            item_data["labels"] = labels
        else:
            item_data["calories"] = "N/A"
            item_data["labels"] = []

        # Append item to the current meal section
        menu_data[meal_name].append(item_data)

# Save the scraped menu as JSON
with open("dining_menu.json", "w", encoding="utf-8") as f:
    json.dump(menu_data, f, indent=4)

print("Scraping complete. Menu data saved to dining_menu.json")
