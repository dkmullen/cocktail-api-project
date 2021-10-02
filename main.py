from flask import Flask, render_template, redirect, url_for, request
import requests

app = Flask(__name__)
base_url = "https://www.thecocktaildb.com/api/json/v1/1/"
search_url = f"{base_url}search.php?"
filter_url = f"{base_url}filter.php?"
lookup_url = f"{base_url}lookup.php?"
list_url = f"{base_url}list.php?"
alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'v', 'w', 'y', 'z']


# Will handle many (but not all) of the queries at this api
def get_me_a_drink(url, search_string):
    drinks = requests.get(url + search_string).json()['drinks']
    return drinks


# Dict comprehension to clear out empty values (esp. ingredients)
def clean_null_terms(d):
    return {
        k: v
        for k, v in d.items()
        if v is not None
    }


# Put ingredients and amounts into their own dictionaries
def filter_items(search_key, d):
    res = dict(filter(lambda item: search_key in item[0], d.items()))
    return res


def parse_drink_data(drink):
    drink = clean_null_terms(drink)
    ingredients = filter_items("strIngredient", drink)
    amounts = filter_items("strMeasure", drink)

    # Pad the amounts dict with empty values to match length of ingredients
    counter = 1
    while len(amounts) < len(ingredients):
        amounts[f"placeholder{counter}"] = ''
        counter = counter + 1

    # Put ingredients and amounts together for a more useful dictionary
    new = []
    for (k, v), (k2, v2) in zip(ingredients.items(), amounts.items()):
        if v2:
            new.append({'ingredient': v, 'amount': v2})
        else:
            new.append({'ingredient': v, 'amount': ''})
    drink['ingredients'] = new
    return drink


@app.route("/")
def home():
    drink = get_me_a_drink(base_url, 'random.php')[0]
    random_drink = parse_drink_data(drink)
    return render_template("index.html", random_drink=random_drink, alphabet=alphabet)


@app.route("/list/<letter>")
def list_drinks(letter):
    drink_list = get_me_a_drink(search_url, f"f={letter}")
    return render_template('list.html', drinks=drink_list)


@app.route("/details/<drink_id>")
def show_details(drink_id):
    drink = get_me_a_drink(lookup_url, f"i={drink_id}")[0]
    drink = parse_drink_data(drink)
    return render_template('details.html', drink=drink)


if __name__ == '__main__':
    app.run(debug=True)
