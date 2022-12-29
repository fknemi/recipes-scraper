import sys
import json
import selenium
import re
import requests
import argparse
from bs4 import BeautifulSoup


parser = argparse.ArgumentParser(description='Process some integers.')


parser.add_argument('--num-category', type=int, default=sys.maxsize,
                    help='The number of recipe categories to scrape. The default is max.')
parser.add_argument('--num-recipes', type=int, default=sys.maxsize,
                    help='The number of recipes to scrape. The default is max.')
parser.add_argument('--output-file', type=str, default='recipes.json',
                    help='The file to save the scraped recipes to. The default is "recipes.json".')


args = parser.parse_args()



num_recipes = args.num_recipes
num_category = args.num_category
output_file = args.output_file or "recipes.json"


if num_recipes == 0:
    print("The number of recipes to scrape must be greater than 0.")
    sys.exit(1)
if num_category == 0:
    print("The number of categories to scrape must be greater than 0.")
    sys.exit(1)


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
for k, i in enumerate(soup):
    if len(recipes_category) == num_category:
        break
    if re.match(recipes_url_regex, i["href"]):
        recipes_category.append(i["href"])

# Getting all the Recipes Urls
recipes_urls = []
for recipe_category in recipes_category:
    recipes_req = requests.get(recipe_category, headers={
        "User-Agent": "Mozilla/5.0 (X11 Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome /"
    })
    recipes_soup = BeautifulSoup(recipes_req.text, "html.parser")
    recipes_soup = recipes_soup.find_all("a", {"class": "card"})
    for k, recipe_link in enumerate(recipes_soup):
        if len(recipes_urls) == num_recipes:
            break
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

with open(output_file if output_file.endswith(".json") else output_file + ".json", "w") as f:
    json.dump(data, f, indent=4)
