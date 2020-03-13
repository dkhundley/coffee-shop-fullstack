import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
# -----------------------------------------------------------------------------
# Defining endpoint to return all drink information
@app.route('/drinks', methods = ['GET'])
def get_drinks():
    # Attempting to query and return drink information
    try:
        # Querying drinks using sqlalchemy
        drinks = Drink.query.all()

        # Returning shortened drink information as json
        return jsonify({
            'success': True,
            'drinks': [drink.short for drink in drinks]
        })
    except:
        abort(404)



# Defining endpoint to return drink detail information if user has proper creds
@app.route('/drinks-detail', methods = ['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    # Attempting to query and return long drink information
    try:
        # Querying drinks using sqlalchemy
        drinks = Drink.query.all()

        # Returning long drink information as json
        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks]
        })
    except:
        abort(404)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

# Defining endpoint to post new drinks and their respective info if user has proper creds
@app.route('/drinks', methods = ['POST'])
@requires_auth('post:drinks')
def post_new_drinks(jwt):
    # Pulling information from body of the request
    body = request.get_json()

    # Checking to see if proper info is present
    if not ('title' in body and 'recipe' in body):
        abort(422)

    # Pulling specific drink information from json body
    title = body.get('title')
    recipe = body.get('recipe')

    # Attempting to add new drink to database
    try:
        # Instantiating new drink object
        drink = Drink(title = title,
                      recipe = json.dumps(recipe))

        # Inserting new drink into database
        drink.insert()

        # Returning success information
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })

    except:
        abort(422)



# Defining endpoint to update drink information if user has proper creds
@app.route('drinks/<id>', methods = ['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, id):
    # Querying drink using provided ID
    drink = Drink.query.get(id)

    # Continuing if drink ID is valid and present in DB
    if drink:
        # Attempting to update drink with new info
        try:
            # Pulling information from body of the request
            body = request.get_json()

            # Pulling specific drink information from json body
            title = body.get('title')
            recipe = body.get('recipe')

            # Updating drink information if new info is present
            if title:
                drink.title = title
            if recipe:
                drink.recipe = recipe

            # Updating drink information formally in database
            drink.update()

            # Returning success information as json
            return jsonify({
                'success': True,
                'drinks': [drink.long()]
            })
        # Raising exception if error updating drink
        except:
            abort(422)
    # Raising exception if drink could not be found
    else:
        abort(404)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
# Defining endpoint to delete existing drink if user has proper creds
@app.route('/drinks/<id>', methods = ['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    # Querying information about the drink using given ID
    drink = Drink.query.get(id)

    # Continuing if drink information is present
    if drink:
        # Attempting to delete drink from database
        try:
            # Issuing delete command
            drink.delete()

            # Returning success information
            return jsonify({
                'success': True,
                'delete': id,
            })
        # Handling error scenario
        except:
            abort(422)
    # Raising error if drink not found
    else:
        abort(404)


## ERROR HANDLING
# -----------------------------------------------------------------------------
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "not found"
                    }), 404

@app.errorhandler(AuthError)
def handle_auth_errors(x):
    return jsonify({
        'success': False,
        'error': x.status_code,
        'message': x.error
    }), 401
