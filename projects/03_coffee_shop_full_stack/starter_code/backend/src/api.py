import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json

from sqlalchemy.sql.expression import false
from sqlalchemy.sql.sqltypes import Integer
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


db_drop_and_create_all()

# ROUTES


@app.route('/drinks')
def get_drinks():
    # returns list of drinks
    drinks = Drink.query.all()
    return jsonify(
        {
            'success': True,
            'drinks': [drink.short() for drink in drinks]
        }
    )


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload=''):
    # returns list of drinks with their recipe
    # requires get:drinks-detail permission
    drinks = Drink.query.all()
    return jsonify(
        {
            'success': True,
            'drinks': [drink.long() for drink in drinks]
        }
    )


def ingredient_validator(ingredient):
    # simple ingredient validator - checks for required parametres and data types
    requirements = {
        'color': str,
        'name': str,
        'parts': int
    }
    for requirement in requirements:
        if requirement not in ingredient:
            #print("MISSING", requirement)
            return False
        if not isinstance(ingredient[requirement], requirements[requirement]):
            #print("INVALID", requirement)
            return False
    return True


def recipe_validator(recipe):
    # simple recipe validator - data type and ingredients check
    if isinstance(recipe, list):
        for ingredient in recipe:
            if not ingredient_validator(ingredient):
                return false
    elif isinstance(recipe, dict):
        return ingredient_validator(recipe)
    else:
        return False
    return True


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload=''):
    # adds a drink into database
    # requires post:drinks permission
    # returns newly added drink
    body = request.get_json()
    title = body['title']
    recipe = body['recipe']
    if not recipe_validator(recipe):
        abort(422)
    drink = Drink(title=title, recipe=json.dumps(recipe))
    drink.insert()
    return jsonify(
        {
            'success': True,
            'drinks': [drink.long()]
        }
    )


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(id):
    # edits a drink
    # requires patch:drinks permission
    # returns updated drink
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)
    body = request.get_json()
    if 'title' in body:
        drink.title = body['title']
    if 'recipe' in body:
        recipe = body['recipe']
        if not recipe_validator(recipe):
            abort(422)
        drink.recipe = json.dumps(recipe)
    drink.update()
    return jsonify(
        {
            'success': True,
            'drinks': [drink.long()]
        }
    )


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    # deletes a drink from database
    # requires delete:drinks permission
    # returns id of deleted drink
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)
    drink.delete()
    return jsonify(
        {
            'success': True,
            'delete': id
        }
    )

# Error Handling


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 422


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code
