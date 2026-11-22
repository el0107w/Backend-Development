from flask import Flask, jsonify, request
import logging

app = Flask(__name__)

logging.basicConfig(filename='access.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s')


@app.before_request
def log_request():
    logging.info(f"{request.method} {request.path}")


items = [
    {"id": 1, "title": "Борщ", "time": 60, "difficulty": "Средне"},
    {"id": 2, "title": "Сырники", "time": 20, "difficulty": "Легко"},
    {"id": 3, "title": "Хинкали", "time": 45, "difficulty": "Сложно"}
]
next_id = 4


@app.route('/items', methods=['GET'])
def get_all_items():
    # Поиск
    search = request.args.get('search')
    if search:
        filtered = [i for i in items if search.lower() in i["title"].lower()]
    else:
        filtered = items.copy()

    # Сортировка
    sort_field = request.args.get('sort')
    order = request.args.get('order', 'asc')
    if sort_field and filtered and sort_field in filtered[0]:
        reverse = (order == 'desc')
        filtered.sort(key=lambda x: x.get(sort_field, ""), reverse=reverse)

    # Пагинация
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    start = (page - 1) * limit
    end = start + limit
    paginated = filtered[start:end]

    return jsonify({
        "count": len(paginated),
        "items": paginated
    })


@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = next((i for i in items if i["id"] == item_id), None)
    if item is None:
        return jsonify({"error": "Элемент не найден"}), 404
    return jsonify(item)


# POST /items (создание с валидацией)
@app.route('/items', methods=['POST'])
def create_item():
    global next_id
    data = request.get_json()

    # Валидация
    if not data or 'title' not in data:
        return jsonify({"error": "Поле title обязательно"}), 400
    if 'time' in data and not isinstance(data['time'], int):
        return jsonify({"error": "Поле time должно быть числом"}), 400

    new_item = {
        "id": next_id,
        "title": data['title'],
        "time": data.get('time', 0),
        "difficulty": data.get('difficulty', "Не указано")
    }
    items.append(new_item)
    next_id += 1
    return jsonify(new_item), 201


# PUT /items/<id>
@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = next((i for i in items if i["id"] == item_id), None)
    if item is None:
        return jsonify({"error": "Элемент не найден"}), 404

    data = request.get_json()
    item["title"] = data.get("title", item["title"])
    item["time"] = data.get("time", item["time"])
    item["difficulty"] = data.get("difficulty", item["difficulty"])
    return jsonify(item)


# DELETE /items/<id> (возвращает 204 No Content)
@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    global items
    item = next((i for i in items if i["id"] == item_id), None)
    if item is None:
        return jsonify({"error": "Элемент не найден"}), 404

    items = [i for i in items if i["id"] != item_id]
    return '', 204  # 204 No Content


# PATCH /items/<id> (частичное обновление)
@app.route('/items/<int:item_id>', methods=['PATCH'])
def patch_item(item_id):
    item = next((i for i in items if i["id"] == item_id), None)
    if item is None:
        return jsonify({"error": "Элемент не найден"}), 404

    data = request.get_json()
    for key in data:
        if key in item:
            item[key] = data[key]
    return jsonify(item)


# DELETE /items (удалить всё)
@app.route('/items', methods=['DELETE'])
def delete_all_items():
    global items
    items.clear()
    return '', 204


# POST /items/bulk (массовое создание)
@app.route('/items/bulk', methods=['POST'])
def create_bulk_items():
    global next_id
    data_list = request.get_json()
    if not isinstance(data_list, list):
        return jsonify({"error": "Ожидается массив элементов"}), 400

    new_items = []
    for data in data_list:
        new_item = {
            "id": next_id,
            "title": data.get('title', 'Без названия'),
            "time": data.get('time', 0),
            "difficulty": data.get('difficulty', "Не указано")
        }
        items.append(new_item)
        new_items.append(new_item)
        next_id += 1
    return jsonify(new_items), 201


# GET /items/stats (статистика: среднее время)
@app.route('/items/stats', methods=['GET'])
def get_stats():
    if not items:
        return jsonify({"average_time": 0, "total_recipes": 0})

    total_time = sum(i.get("time", 0) for i in items)
    avg_time = total_time / len(items)

    return jsonify({
        "total_recipes": len(items),
        "average_time": round(avg_time, 2)
    })


# GET /items/<id>/related (связанные по сложности)
@app.route('/items/<int:item_id>/related', methods=['GET'])
def get_related_items(item_id):
    item = next((i for i in items if i["id"] == item_id), None)
    if item is None:
        return jsonify({"error": "Элемент не найден"}), 404

    difficulty = item.get("difficulty")
    related = [i for i in items if i["difficulty"] == difficulty and i["id"] != item_id]
    return jsonify({
        "difficulty": difficulty,
        "related_items": related
    })


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Маршрут не найден"}), 404


@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Ошибка сервера: {e}")
    return jsonify({"error": "Внутренняя ошибка сервера"}), 500


if __name__ == '__main__':
    app.run(port=3000, debug=True)
