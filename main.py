import json
import selenium
import re
import requests
from bs4 import BeautifulSoup

recipe_url_regex = r"https://www\.allrecipes\.com/recipe/\d+/.+"
recipes_url_regex = r"https:\/\/www\.allrecipes\.com\/recipes\/\d+\/.+\/"

req = requests.get("https://www.allrecipes.com/recipes-a-z-6735880", headers={
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
})


soup = BeautifulSoup(req.text, "html.parser")
soup = soup.find("div", {"class": "alphabetical-list"})
soup = soup.find_all("a")

# Getting all the Recipes Category Urls
recipes_category = []
for i in soup:
    if re.match(recipes_url_regex, i["href"]):
        recipes_category.append(i["href"])

# Getting all the Recipes Urls
recipes_urls = []
for recipe_category in recipes_category[0:2]:
    recipes_req = requests.get(recipe_category, headers={
        "User-Agent": "Mozilla/5.0 (X11 Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome /"
    })
    recipes_soup = BeautifulSoup(recipes_req.text, "html.parser")
    recipes_soup = recipes_soup.find_all("a", {"class": "card"})
    for recipe_link in recipes_soup:
        if re.match(recipe_url_regex, recipe_link["href"]):
            recipes_urls.append(recipe_link["href"])

# Filtering out unnecessary data
def filter_recipe_json(recipe_data):
    recipe_data.pop("@context", None)
    recipe_data.pop("@type", None)
    try:
        recipe_data["image"].pop("@type", None)
    except Exception:
        pass
    try:
        recipe_data["video"].pop("@type", None)
    except Exception:
        pass
    recipe_data.pop("publisher", None)
    recipe_data.pop("mainEntityOfPage", None)
    try:
        recipe_data["aggregateRating"].pop("@type", None)
    except Exception:
        pass
    try:
        recipe_data["nutrition"].pop("@type", None)
    except Exception:
        pass
    try:
        for review in recipe_data["review"]:
            review.pop("@type", None)
            review["author"].pop("@type", None)
            review["reviewRating"].pop("@type", None)
    except Exception:
        pass
    for author in recipe_data["author"]:
        author.pop("@type", None)
    for instruction in recipe_data["recipeInstructions"]:
        instruction.pop("@type", None)
        try:
            if instruction["image"]:
                for image in instruction["image"]:
                    image.pop("@type", None)
        except Exception:
            pass
    return recipe_data


data = []
for recipe_url in recipes_urls:
    recipe_req = requests.get(recipe_url, headers={
        "User-Agent": "Mozilla/5.0 (X11 Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome /"
    })
    recipe_soup = BeautifulSoup(recipe_req.text, "html.parser")
    recipe_data = recipe_soup.find("script", {"class": "allrecipes-schema"})
    try:
        data.append(filter_recipe_json(json.loads(str(recipe_data.text))[0]))
        print(f"Successfully scraped recipe: {recipe_url}")
    except Exception:
        print(f"Failed to scrape recipe: {recipe_url}")

with open("data.json", "w") as f:
    json.dump(data, f, indent=4)
