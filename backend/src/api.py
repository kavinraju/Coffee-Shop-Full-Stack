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
@TODO DONE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@TODO DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        data = Drink.query.order_by(Drink.id).all()
        drinks = [drink.short() for drink in data]
        return jsonify({
            'success': 'True',
            'drinks': drinks
        })

    except Exception as e:
        print(e)
        abort(422)

'''
@TODO DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        data = Drink.query.order_by(Drink.id).all()
        drinks = [drink.long() for drink in data]

        return jsonify({
            'success': True,
            'drinks': drinks
        })

    except Exception as e:
        print(e)
        abort(422)


'''
@TODO DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(payload):
    body = request.get_json()

    if body is None:
        abort(422)
    else:

        new_drink_title = body.get('title', None)
        new_drink_recipe = body.get('recipe', None)

        try:
            if new_drink_title and new_drink_recipe:
                new_drink = Drink(title=new_drink_title, recipe=json.dumps(new_drink_recipe))
                new_drink.insert()

                print('new_drink: ', new_drink.long)
                return jsonify({
                    'success': True,
                    'drinks': [new_drink.long()]
                })

            else:
                abort(422)
        except Exception as e:
            print(e)
            abort(422)


'''
@TODO DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):

    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        print(drink.long())
        if drink is None:
            abort(404)

        else:
            body = request.get_json()
            updated_drink_title = body.get('title', None)
            updated_drink_recipe = body.get('recipe', None)

            if updated_drink_title:
                drink.title = updated_drink_title
            if updated_drink_recipe:
                drink.recipe = json.dumps(updated_drink_recipe)

            drink.update()

            return jsonify({
                'success': True,
                'drinks': [drink.long()]
            })

    except Exception as e:
        print(e)
        abort(422)


'''
@TODO DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):

    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        else:
            drink.delete()
            return jsonify({
                'success': True,
                'delete': drink_id
            })

    except Exception as e:
        print(e)
        abort(422)

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO DONE implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@TODO DONE implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def autherror(error):
    return jsonify({
                    "success": False,
                    "error": error.status_code,
                    "message": error.error
                    }) , error.status_code
