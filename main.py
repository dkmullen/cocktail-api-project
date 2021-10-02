from flask import Flask, render_template, redirect, url_for, request
import requests

app = Flask(__name__)
base_url = "https://www.thecocktaildb.com/api/json/v1/1/"
search_url = f"{base_url}search.php?"
filter_url = f"{base_url}filter.php?"
lookup_url = f"{base_url}lookup.php?"
list_url = f"{base_url}list.php?"


# Will handle many (but not all) of the queries at this api
def get_me_a_drink(url, search_string):
    drinks = requests.get(url + search_string).json()['drinks']
    return drinks


@app.route("/")
def home():
    random_drink = get_me_a_drink(base_url, 'random.php')[0]
    return render_template("index.html", drink=random_drink)


@app.route("/list/<letter>")
def list_drinks(letter):
    drink_list = get_me_a_drink(search_url, f"f={letter}")
    return render_template('list.html', drinks=drink_list)


@app.route("/details/<drink_id>")
def show_details(drink_id):
    drink = get_me_a_drink(lookup_url, f"i={drink_id}")
    return render_template('details.html', drink=drink)


if __name__ == '__main__':
    app.run(debug=True)
