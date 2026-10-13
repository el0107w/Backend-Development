from flask import Flask, jsonify, request
import time

app = Flask(__name__)

# Console request logging


@app.before_request
def log_request():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {request.method} {request.path}")

# 1. Text endpoint


@app.route('/')
def home():
    return 'Добро пожаловать на сервер рецептов и поваров!'

# 2. JSON endpoint 1


@app.route('/api/recipes')
def get_recipes():
    recipes = [
        {"id": 1, "name": "Сырники", "calories": 160},
        {"id": 2, "name": "Роллы Филадельфия", "calories": 180},
        {"id": 3, "name": "Хинкали", "calories": 200}
    ]
    return jsonify(recipes)

# 3. JSON endpoint 2


@app.route('/api/chefs')
def get_chefs():
    chefs = [
        {"id": 1, "name": "Ивлев", "cuisine": "Русская"},
        {"id": 2, "name": "Агзамов", "cuisine": "Десерты со всего мира"},
        {"id": 3, "name": "Гроле", "cuisine": "Французская"}
    ]
    return jsonify(chefs)

# 4. JSON endpoint with a parameter 1


@app.route('/api/recipes/<int:recipe_id>')
def get_recipe(recipe_id):
    return jsonify({
        "requestedId": recipe_id,
        "status": "success"
    })

# 5.JSON endpoint with a parameter 2


@app.route('/api/chefs/<name>')
def get_chef(name):
    return jsonify({
        "requestedName": name,
        "status": "success"
    })

# Processing 404


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Маршрут не найден"}), 404


if __name__ == '__main__':
    app.run(port=3000, debug=True)
