#!/usr/bin/python

import requests
from bs4 import BeautifulSoup

source_url = 'http://www.tabeladecalorias.net/'
output_csv = 'ingredients.csv'

# Retrieve food categories links from www.tabeladecalorias.net
def get_links(url):
    links = list()
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    menu = soup.find('ul', attrs={'id':'menu-calorie-tables'})
    for menu_item in menu.find_all('li'):
        links.append(str(menu_item.find('a',href=True)['href']))
    return links

# Retrieve food name, portion and calories per portion
def get_ingredients(url):
    ingredients = list()
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    ingredients_table = soup.find('table', attrs={'id':'calories-table'})
    for ingredient in ingredients_table.find_all('tr', attrs={'class':'kt-row'}):
        ingredient_name = ingredient.find('td', attrs={'class':'food'}).get_text().encode('utf-8')
        ingredient_portion = ingredient.find('td', attrs={'class':'serving portion'}).get_text().encode('utf-8')
        ingredient_calories = ingredient.find('td', attrs={'class':'kcal'}).get_text().encode('utf-8')
        ingredients.append(ingredient_name + "," + ingredient_portion + "," + ingredient_calories)
    return ingredients



links = get_links(source_url)
for link in links:
    ingredients = get_ingredients(link)
    with open(output_csv,'ab') as file:
        for ingredient in ingredients:
            file.write(ingredient+'\n')