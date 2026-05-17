from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

FILE = "tasks.txt"
tasks = []


# ------------------ Task Class ------------------
class Task:
    def __init__(self, task_id, title, description, status="Pending"):
        self.id = task_id
        self.title = title
        self.description = description
        self.status = status

    def serialize(self):
        return f"{self.id}|{self.title}|{self.description}|{self.status}"

    @staticmethod
    def deserialize(text):
        tid, t, d, s = text.split("|")
        return Task(int(tid), t, d, s)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status
        }


# ------------------ File I/O ------------------
def load_tasks():
    tasks.clear()
    if not os.path.exists(FILE):
        open(FILE, "w").close()

    with open(FILE, "r") as f:
        for line in f:
            if line.strip():
                tasks.append(Task.deserialize(line.strip()))


def save_tasks():
    with open(FILE, "w") as f:
        for t in tasks:
            f.write(t.serialize() + "\n")


# ------------------ API ROUTES ------------------
@app.route("/tasks", methods=["GET"])
def get_tasks():
    load_tasks()
    return jsonify([t.to_dict() for t in tasks])


@app.route("/tasks", methods=["POST"])
def add_task():
    load_tasks()
    data = request.json
    new_id = len(tasks) + 1
    task = Task(new_id, data["title"], data["description"])
    tasks.append(task)
    save_tasks()
    return jsonify({"message": "task added"})


@app.route("/tasks/<int:id>", methods=["PUT"])
def update_task(id):
    load_tasks()
    data = request.json

    for t in tasks:
        if t.id == id:
            t.title = data["title"]
            t.description = data["description"]
            t.status = data["status"]
            save_tasks()
            return jsonify({"message": "task updated"})

    return jsonify({"error": "not found"}), 404


@app.route("/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):
    load_tasks()
    for t in tasks:
        if t.id == id:
            tasks.remove(t)
            save_tasks()
            return jsonify({"message": "task deleted"})
    return jsonify({"error": "not found"}), 404


# ------------------ FRONTEND HTML WITH JS & CSS ------------------
@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Modern Task Manager</title>
    <style>

        body {
            background: linear-gradient(135deg,#6a11cb,#2575fc);
            font-family: Poppins, sans-serif;
            padding: 40px;
            color: white;
        }
        .container { width: 80%; margin: auto; }
        h1 { text-align: center; font-size: 40px; margin-bottom: 20px; }

        .add-btn {
            padding: 12px 22px;
            background: #fff;
            color: #000;
            border-radius: 12px;
            display: block;
            margin: 0 auto 20px;
            cursor: pointer;
            font-size: 18px;
            transition: 0.2s;
        }
        .add-btn:hover { transform: scale(1.05); }

        .task-card {
            background: rgba(255,255,255,0.2);
            padding: 20px;
            margin: 12px 0;
            border-radius: 15px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        }

        button {
            padding: 8px 16px;
            border-radius: 10px;
            border: none;
            margin-right: 10px;
            cursor: pointer;
            transition: 0.2s;
        }
        .update-btn { background: #ffd700; }
        .delete-btn { background: #ff4a4a; color: white; }

        /* Modal */
        .modal { 
            display: none; 
            position: fixed; inset:0; 
            background: rgba(0,0,0,0.5); 
            justify-content:center; 
            align-items:center;
        }
        .modal-content {
            width: 380px; padding: 25px;
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
        }
        .modal input, .modal textarea, .modal select {
            width: 100%; padding: 10px;
            margin: 10px 0;
            border-radius: 10px; border: none;
        }
        #saveBtn { background: #00ff99; }
        .close { float:right; cursor:pointer; font-size:26px; }
    </style>
</head>

<body>

<div class="container">
    <h1>✨ Task Manager</h1>

    <button class="add-btn" onclick="openAddModal()">+ Add Task</button>

    <div id="taskList"></div>
</div>


<!-- Modal -->
<div id="taskModal" class="modal">
    <div class="modal-content">
        <span class="close" onclick="closeModal()">&times;</span>

        <h2 id="modalTitle">Add Task</h2>

        <input type="text" id="title" placeholder="Task Title">
        <textarea id="description" placeholder="Task Description"></textarea>

        <select id="status">
            <option value="Pending">Pending</option>
            <option value="Completed">Completed</option>
        </select>

        <button id="saveBtn" onclick="saveTask()">Save</button>
    </div>
</div>


<script>

const API = "/tasks";
let updateId = null;

function openAddModal() {
    updateId = null;
    document.getElementById("modalTitle").innerText = "Add Task";
    document.getElementById("title").value = "";
    document.getElementById("description").value = "";
    document.getElementById("status").value = "Pending";
    document.getElementById("taskModal").style.display = "flex";
}

function closeModal() {
    document.getElementById("taskModal").style.display = "none";
}

async function loadTasks() {
    const res = await fetch(API);
    const tasks = await res.json();

    let html = "";
    tasks.forEach(t => {
        html += `
            <div class="task-card">
                <h2>${t.title}</h2>
                <p>${t.description}</p>
                <p>Status: ${t.status}</p>
                <button class="update-btn" onclick="openUpdateModal(${t.id}, '${t.title}', '${t.description}', '${t.status}')">Update</button>
                <button class="delete-btn" onclick="deleteTask(${t.id})">Delete</button>
            </div>
        `;
    });

    document.getElementById("taskList").innerHTML = html;
}

function openUpdateModal(id, title, desc, status) {
    updateId = id;
    document.getElementById("modalTitle").innerText = "Update Task";
    document.getElementById("title").value = title;
    document.getElementById("description").value = desc;
    document.getElementById("status").value = status;
    document.getElementById("taskModal").style.display = "flex";
}

async function saveTask() {
    const data = {
        title: document.getElementById("title").value,
        description: document.getElementById("description").value,
        status: document.getElementById("status").value
    };

    if (updateId === null) {
        await fetch(API, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });
    } else {
        await fetch(`${API}/${updateId}`, {
            method: "PUT",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });
    }

    closeModal();
    loadTasks();
}

async function deleteTask(id) {
    await fetch(`${API}/${id}`, { method: "DELETE" });
    loadTasks();
}

loadTasks();

</script>

</body>
</html>
"""


# ------------------ RUN APP ------------------
if __name__ == "__main__":
    load_tasks()
    app.run(debug=True)
