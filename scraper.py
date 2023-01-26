import time
import sys
import json
import re
import requests
import argparse
import itertools
from __utils__ import parse_category_urls, get_category, get_category_recipes_urls, get_recipe, read_progress, save_progress, get_proxies
from requests.adapters import HTTPAdapter, Retry


parser = argparse.ArgumentParser(
    description='Recipes scraper for allrecipes.com')

parser.add_argument('-nc', '--number-of-categories', type=int, default=sys.maxsize,
                    help='The number of recipe categories to scrape. The default is max.')
parser.add_argument('-nr', '--number-of-recipes', type=int, default=sys.maxsize,
                    help='The number of recipes to scrape. The default is max.')
parser.add_argument("-o", '--output-file', type=str, default='recipes.json',
                    help='The file to save the scraped recipes to. The default is "recipes.json".')
parser.add_argument("-c", '--continue-progress', default=False,
                    help='Continue scraping from the last progress.', action='store_true')
parser.add_argument('-p', '--proxy', default=None,
                    help='Enable proxies to scrape. Default is Disabled', action='store_true')
parser.add_argument('-pf', '--proxy-file', default="proxies.txt",
                    help='Specify custom proxies file to use.', required=False)

args = parser.parse_args()

max_recipes = args.number_of_recipes
max_categories = args.number_of_categories
output_file = args.output_file
continue_progress = args.continue_progress
use_proxy = args.proxy
proxy_file = args.proxy_file


s = requests.Session()
proxy_counter = 0

retries = Retry(total=5,
                backoff_factor=0.1,
                status_forcelist=[500, 502, 503, 504])
s.mount('http://', HTTPAdapter(max_retries=retries))
s.headers = {
    "User-Agent": "Mozilla/5.0 (X11 Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome /"
}
s.timeout = 10


progress = {
    "category": None,
    "recipe": None,
    "downloaded_count": 0,
    "categories": [],
    "category_urls": [],
    "recipe_urls": [],
    "failed_recipes": []
}

proxies = []
if use_proxy:
    proxies = get_proxies(proxy_file)
    s.proxies = proxies


if continue_progress:
    progress = read_progress()
    recipe_categories = progress["categories"]
else:
    recipe_categories, proxy_counter = parse_category_urls(
        s, proxy_counter, proxies, max_categories, use_proxy)


recipes_count = 0


def scrape_recipes(s, progress, recipe_categories, max_categories, max_recipes):
    global proxy_counter, recipes_count, proxies, use_proxy
    for i, category_url in enumerate(recipe_categories):
        if i == max_categories:
            break
        progress["category"] = category_url
        category, proxy_counter = get_category(
            s, category_url, proxy_counter, proxies, use_proxy)
        if continue_progress:
            category_urls = progress["category_urls"]
        else:
            category_urls = get_category_recipes_urls(
                category)
            progress["category_urls"] = category_urls
        for j, recipe_url in enumerate(category_urls):
            if recipes_count == max_recipes:
                break
            recipes_count += 1
            progress["recipe"] = recipe_url
            recipe_data, proxy_counter = get_recipe(
                s, recipe_url, proxy_counter, proxies, use_proxy)
            if recipe_data:
                try:
                    with open("recipes.json", "r") as f:
                        data = json.load(f)
                except Exception:
                    data = []
                data.append(recipe_data)
                with open("recipes.json", "w") as f:
                    json.dump(data, f)
                print("successfully scraped recipe: " + recipe_url)
                progress["recipe"] = recipe_url
            else:
                progress["failed_recipes"].append(recipe_url)
                print("failed to scrape recipe: " + recipe_url)
            progress["downloaded_count"] += 1
            progress["category_urls"].pop(j)
            save_progress(progress)

        if len(progress["categories"]) != 0:
            progress["categories"].pop(i)


scrape_recipes(s, progress, recipe_categories, max_categories, max_recipes)
