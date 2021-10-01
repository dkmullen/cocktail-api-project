import requests

base_url = "https://www.thecocktaildb.com/api/json/v1/1/"
search_url = f"{base_url}search.php?"
filter_url = f"{base_url}filter.php?"
lookup_url = f"{base_url}lookup.php?"
list_url = f"{base_url}list.php?"


# Will handle many (but not all) of the queries at this api
def get_me_a_drink(url, search_string):
    drinks = requests.get(url + search_string).json()['drinks']
    for drink in drinks:
        print(f"{drink['strDrink']}: {drink['strGlass']}")


get_me_a_drink(base_url, 'random.php')
# list_by_letter()
# get_random_drink()
