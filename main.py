from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)

# Using SQLAlchemy - set up the DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cached-drinks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Model the records
class DrinksByLetter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    letter = db.Column(db.String(5), unique=True, nullable=False)
    drink_list = db.Column(db.String)


# Create the DB
db.create_all()

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


def make_ingredients_string(ingredients):
    # Make a string of the ingredients for later use :)
    temp_list = []
    for item in ingredients:
        temp_list.append(ingredients[item])
    return ', '.join(temp_list)


def parse_drink_data(drink):
    drink = clean_null_terms(drink)
    ingredients = filter_items("strIngredient", drink)
    amounts = filter_items("strMeasure", drink)

    # Make a string of the ingredients for later use :)
    temp_list = []
    for item in ingredients:
        temp_list.append(ingredients[item])
    drink['ingredients_str'] = ', '.join(temp_list)

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
    return render_template("index.html", drink=random_drink, alphabet=alphabet)


@app.route("/list/<letter>")
def list_drinks(letter):
    letter_from_db = db.session.query(DrinksByLetter).filter(DrinksByLetter.letter == letter).first()
    if letter_from_db:
        drink_list = eval(letter_from_db.drink_list)
    else:
        drink_list = get_me_a_drink(search_url, f"f={letter}")
        new_list = DrinksByLetter(letter=letter, drink_list=str(drink_list))
        db.session.add(new_list)
        db.session.commit()
    for drink in drink_list:
        ingredients = filter_items("strIngredient", drink)
        ingredients = clean_null_terms(ingredients)
        drink['ingredients_str'] = make_ingredients_string(ingredients)
    return render_template('list.html', drinks=drink_list, alphabet=alphabet)


@app.route("/details/<drink_id>")
def show_details(drink_id):
    drink = get_me_a_drink(lookup_url, f"i={drink_id}")[0]
    drink = parse_drink_data(drink)
    return render_template('details.html', drink=drink, alphabet=alphabet)


if __name__ == '__main__':
    app.run(debug=True)
