from flask import Flask, render_template, request, redirect, jsonify, url_for
import json
import os

app = Flask(__name__, static_url_path='/static')
DATA_FILE = "quota_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"servers": []}
    with open(DATA_FILE, "r") as file:
        return json.load(file)

def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Функция для получения следующего уникального id для сервера
def get_next_server_id(data):
    if data["servers"]:
        return max(server.get("id", 0) for server in data["servers"]) + 1
    return 1

@app.route('/')
def index():
    data = load_data()
    servers_with_usage = []

    for server in data["servers"]:
        companies = server.get("companies", [])
        used_storage = sum(company.get("allocated_quota", 0) for company in companies)
        total_storage = server.get("total_storage", 0)
        free_storage = total_storage - used_storage

        servers_with_usage.append({
            "id": server.get("id"),
            "name": server.get("name"),
            "total_storage": total_storage,
            "used_storage": used_storage,
            "free_storage": free_storage
        })

    return render_template('index.html', servers=servers_with_usage)

@app.route('/admin')
def admin():
    data = load_data()
    return render_template('admin.html', servers=data["servers"])

@app.route('/server/<int:server_id>')
def view_server(server_id):
    data = load_data()
    for server in data["servers"]:
        if server.get("id") == server_id:
            companies = server.get("companies", [])
            used_storage = sum(company.get("allocated_quota", 0) for company in companies)
            total_storage = server.get("total_storage", 0)
            free_storage = total_storage - used_storage
            return render_template('server.html', server=server,
                                   used_storage=used_storage, free_storage=free_storage)
    return "Server not found", 404

@app.route('/edit_resources/<int:server_id>', methods=['GET', 'POST'])
def edit_resources(server_id):
    data = load_data()
    for server in data["servers"]:
        if server.get("id") == server_id:
            if request.method == 'POST':
                server["total_storage"] = int(request.form['total_storage'])
                save_data(data)
                return redirect(url_for('edit_resources', server_id=server_id))
            return render_template('edit_resources.html', server=server)
    return "Server not found", 404

@app.route('/server/<int:server_id>/edit_company/<company_name>', methods=['POST'])
def edit_company(server_id, company_name):
    data = load_data()
    for server in data["servers"]:
        if server.get("id") == server_id:
            for company in server.get("companies", []):
                if company.get("name") == company_name:
                    company["allocated_quota"] = int(request.form['allocated_quota'])
                    save_data(data)
                    return redirect(url_for('edit_resources', server_id=server_id))
            return "Company not found", 404
    return "Server not found", 404

@app.route('/server/<int:server_id>/delete_company/<company_name>', methods=['POST'])
def delete_company(server_id, company_name):
    data = load_data()
    for server in data["servers"]:
        if server.get("id") == server_id:
            server["companies"] = [c for c in server.get("companies", []) if c.get("name") != company_name]
            save_data(data)
            return redirect(url_for('edit_resources', server_id=server_id))
    return "Server not found", 404

@app.route('/delete_server/<int:server_id>', methods=['POST'])
def delete_server(server_id):
    data = load_data()
    data["servers"] = [server for server in data["servers"] if server.get("id") != server_id]
    save_data(data)
    return redirect(url_for('admin'))

# Новый маршрут для добавления сервера
@app.route('/add_server', methods=['POST'])
def add_server():
    data = load_data()
    new_server = {
        "id": get_next_server_id(data),
        "name": request.form['name'],
        "total_storage": int(request.form['total_storage']),
        "companies": []
    }
    data["servers"].append(new_server)
    save_data(data)
    return redirect(url_for('admin'))

@app.route('/server/<int:server_id>/add_company', methods=['POST'])
def add_company(server_id):
    data = load_data()
    # Находим сервер по его id
    server = next((s for s in data["servers"] if s.get("id") == server_id), None)
    if not server:
        return "Server not found", 404

    # Получаем данные из формы
    company_name = request.form.get("name")
    try:
        allocated_quota = int(request.form.get("allocated_quota", 0))
    except ValueError:
        allocated_quota = 0

    # Инициализируем список компаний, если он отсутствует
    if "companies" not in server:
        server["companies"] = []

    # Добавляем новую компанию
    server["companies"].append({
        "name": company_name,
        "allocated_quota": allocated_quota
    })

    save_data(data)
    # Перенаправляем обратно на страницу редактирования ресурсов сервера
    return redirect(url_for('edit_resources', server_id=server_id))


if __name__ == '__main__':
    app.run(debug=True)
