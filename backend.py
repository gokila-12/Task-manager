from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

FILE_NAME = "tasks.txt"
tasks = []


class Task:
    def __init__(self, task_id, title, description, status="Pending"):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.status = status

    def to_string(self):
        return f"{self.task_id}|{self.title}|{self.description}|{self.status}"

    @staticmethod
    def from_string(data):
        task_id, title, description, status = data.split("|")
        return Task(int(task_id), title, description, status)

    def to_dict(self):
        return {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "status": self.status
        }


def load_tasks():
    tasks.clear()
    if not os.path.exists(FILE_NAME):
        open(FILE_NAME, "w").close()

    with open(FILE_NAME, "r") as file:
        for line in file:
            if line.strip():
                tasks.append(Task.from_string(line.strip()))


def save_tasks():
    with open(FILE_NAME, "w") as file:
        for t in tasks:
            file.write(t.to_string() + "\n")


@app.route("/tasks", methods=["GET"])
def get_tasks():
    load_tasks()
    return jsonify([t.to_dict() for t in tasks])


@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.json
    load_tasks()
    task_id = len(tasks) + 1
    task = Task(task_id, data["title"], data["description"], "Pending")
    tasks.append(task)
    save_tasks()
    return jsonify({"message": "Task added"})


@app.route("/tasks/<int:id>", methods=["PUT"])
def update_task(id):
    load_tasks()
    data = request.json

    for t in tasks:
        if t.task_id == id:
            t.title = data["title"]
            t.description = data["description"]
            t.status = data["status"]
            save_tasks()
            return jsonify({"message": "Task updated"})

    return jsonify({"message": "Task not found"}), 404


@app.route("/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):
    load_tasks()
    for t in tasks:
        if t.task_id == id:
            tasks.remove(t)
            save_tasks()
            return jsonify({"message": "Task deleted"})
    return jsonify({"message": "Task not found"}), 404


if __name__ == "__main__":
    load_tasks()
    app.run(debug=True)
