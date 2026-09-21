import json
from pathlib import Path

from flask import Flask, jsonify, redirect, request, send_file, url_for

app = Flask(__name__)
data_file = Path(__file__).with_name("data.json")


def read_users():
	with data_file.open(encoding="utf-8") as file:
		return json.load(file)


@app.route("/")
def home():
	return send_file("index.html")


@app.route("/api", methods=["GET", "POST"])
def api():
	if request.method == "GET":
		return jsonify(read_users())

	data = request.get_json(silent=True) or request.form
	name = str(data.get("name", "")).strip()
	age = data.get("age")
	if not name or age in (None, ""):
		return jsonify(error="Name and age are required."), 400

	try:
		age = int(age)
		if age < 0:
			raise ValueError("Age must be zero or greater.")
	except ValueError as error:
		return jsonify(error=str(error)), 400

	users = read_users()
	users.append({"name": name, "age": age})
	with data_file.open("w", encoding="utf-8") as file:
		json.dump(users, file, indent=2)

	return redirect(url_for("api"), code=303)


if __name__ == "__main__":
	app.run(port=5123)