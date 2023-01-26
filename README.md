# Scraper for allrecipes.com
## Installation
### To install the Recipes Scraper, follow these steps:

- Clone the repository: ```git clone https://github.com/DyingintheDarkness/recipes-scraper.git```<br/>
- Navigate to the project directory: cd recipes-scraper<br/>
- Install the dependencies: pip install -r requirements.txt<br/>

Usage
To use the Recipes Scraper, run the following command:
python scraper.py [options]

## Here are the available options for the Recipes Scraper:
- --num-recipes: The number of recipes to scrape. The default is unlimited.
- --num-category: The number of recipe categories to scrape. The default is unlimited.
- --output-file: The file to save the scraped recipes to. The default is "recipes.json".
- --continue-progress: Continue scraping from the last progress.
- --proxy: Enable the use of proxies while scraping. This option is disabled by default.
- --proxy-file: Specify a custom proxies file to use. Default is "proxies.txt".

## Disclaimer
Please note that scraping websites may be against their terms of service. Use this tool at your own risk.
