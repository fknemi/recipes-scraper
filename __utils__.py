import sys
import json
import re
import argparse
from bs4 import BeautifulSoup
import time


recipe_url_regex = r"https://www\.allrecipes\.com/recipe/\d+/.+"
recipes_url_regex = r"https:\/\/www\.allrecipes\.com\/recipes\/\d+\/.+\/"


class ProgressFileError(Exception):
    pass


def get_proxies(file_path):
    with open(file_path, "r") as f:
        proxies = f.read().split("\n")
    return proxies


def rotate_proxy(proxy_counter, proxies):
    proxy_counter += 1
    proxy_counter %= len(proxies)
    return proxy_counter


def parse_category_urls(s, proxy_counter, proxies, max_categories, use_proxy=False):
    global recipes_url_regex
    recipes_categories = []
    categories_req = None
    try:
        categories_req = s.get(
            "https://www.allrecipes.com/recipes-a-z-6735880")
    except Exception:
        if use_proxy:
            proxy_counter = rotate_proxy(proxy_counter, proxies)
    if categories_req and categories_req.status_code == 200:
        soup = BeautifulSoup(categories_req.text, "html.parser")
        soup = soup.find("div", {"class": "alphabetical-list"})
        soup = soup.find_all("a")
        for k, i in enumerate(soup):
            if max_categories == len(recipes_categories):
                break
            if re.match(recipes_url_regex, i["href"]):
                recipes_categories.append(i["href"])
    return recipes_categories, proxy_counter


def get_category(s, category_url, proxy_counter, proxies, use_proxy=False):
    category_req = None
    try:
        category_req = s.get(category_url)
    except Exception as e:
        if use_proxy:
            proxy_counter = rotate_proxy(proxy_counter, proxies)
    return category_req, proxy_counter


def get_category_recipes_urls(category):
    global recipe_url_regex
    category_urls = []
    recipes_soup = BeautifulSoup(category.text, "html.parser")
    recipes_soup = recipes_soup.find_all("a", {"class": "card"})
    for k, recipe_link in enumerate(recipes_soup):
        if re.match(recipe_url_regex, recipe_link["href"]):
            category_urls.append(recipe_link["href"])
    return category_urls


def filter_recipe_json(recipe_data):
    try:
        recipe_data.pop("@context", None)
    except:
        pass
    try:
        recipe_data.pop("@type", None)
    except:
        pass
    try:
        recipe_data.pop("publisher", None)
    except:
        pass
    try:
        recipe_data.pop("mainEntityOfPage", None)
    except:
        pass
    try:
        recipe_data["image"].pop("@type", None)
    except Exception:
        pass
    try:
        recipe_data["video"].pop("@type", None)
    except Exception:
        pass
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


def get_recipe(s, recipe_url, proxy_counter, proxies, use_proxy=False):
    recipe_req = None
    data = None
    try:
        recipe_req = s.get(recipe_url)
    except Exception:
        if use_proxy:
            proxy_counter = rotate_proxy(proxy_counter, proxies)
    try:
        if recipe_req and recipe_req.status_code == 200:
            recipe_soup = BeautifulSoup(recipe_req.text, "html.parser")
            recipe_data = recipe_soup.find(
                "script", {"class": "allrecipes-schema"})
            return filter_recipe_json(json.loads(str(recipe_data.text))[0]), proxy_counter
    except Exception:
        pass
    return None, proxy_counter


def read_progress():
    progress = None
    try:
        with open("temp.json", "r") as f:
            progress = json.loads(f.read())
    except Exception as e:
        raise ProgressFileError("Failed to read progress file.") from e
    return progress


def save_progress(progress):
    with open("temp.json", "w") as f:
        f.write(json.dumps(progress))
