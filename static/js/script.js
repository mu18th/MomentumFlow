
// helper for messages, writen by chatgpt
function showMessage(message, isError = false) {
    const div = document.createElement("div");
    div.textContent = message;
    div.style.position = "fixed";
    div.style.bottom = "20px";
    div.style.right = "20px";
    div.style.padding = "8px 12px";
    div.style.borderRadius = "6px";
    div.style.color = "#fff";
    div.style.backgroundColor = isError ? "#e74c3c" : "#2ecc71";
    div.style.zIndex = "9999";
    document.body.appendChild(div);
    setTimeout(() => div.remove(), 3000);
}
//drag tasks
document.addEventListener("DOMContentLoaded", () => {
    const draggableTasks = document.querySelectorAll("[draggable='true']");

    draggableTasks.forEach(task => {
        task.addEventListener("dragstart", e => {
            e.dataTransfer.setData("text/plain", task.id);
        });
    });

    const taskLists = document.querySelectorAll(".task-list");
    taskLists.forEach(taskList => {
        taskList.addEventListener("dragover", e => {
            e.preventDefault();
            taskList.classList.add("task-list--over");
        });

        taskList.addEventListener("dragleave", () => {
            taskList.classList.remove("task-list--over");
        });

        taskList.addEventListener("drop", e => {
            e.preventDefault();
            const droppedTaskId = e.dataTransfer.getData("text/plain");
            const droppedTask = document.getElementById(droppedTaskId);

            taskList.appendChild(droppedTask);
            taskList.classList.remove("task-list--over");

            var entry = {
                taskID: droppedTask.id,
                status: taskList.id
            };

            console.log(entry);

            fetch(`${window.location.origin}/update-status`, {
                method: "POST",
                credentials: "include",
                body: JSON.stringify(entry),
                cache: "no-cache",
                headers: new Headers({
                    "content-type": "application/json"
                })
            })
                .then(response => {
                    if (!response.ok) {
                        alert("Failed to update task status.");
                        location.reload(true);
                        console.log(`Response status was not 200 ${response.status}`);
                        return;
                    }
                    return response.json();
                })
                .then(data => {
                    console.log(data);
                })
                .catch(err => console.error("Fetch error:", err));
        });
    });
});

function generateTask(id) {
    var entry = { taskID: id };

    fetch(`${window.location.origin}/generate_subtasks`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(entry),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
        .then(response => {
            if (!response.ok) {
                showMessage("Failed to generate subtasks.", true);
                console.error(`Response status was ${response.status}`);
                return;
            }
            alert("Subtasks generation in progress. Please refresh the page after a few moments.");
            location.reload(true);
            return response.json();
        })
        .then(data => {
            if (data) console.log(data);
        })
        .catch(err => console.error("Fetch error:", err));
}

function deleteTask(id) {
    var entry = { taskID: id };

    fetch(`${window.location.origin}/delete-task`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(entry),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
        .then(response => {
            if (!response.ok) {
                showMessage("Failed to delete task.", true);
                console.error(`Response status was ${response.status}`);
                return;
            }
            // remove task element dynamically
            const task = document.getElementById(id);
            if (task) task.remove();

            showMessage("Task deleted. Regresh the page if there are subtasks of it to be deleted");
            return response.json();
        })
        .then(data => {
            if (data) console.log(data);
        })
        .catch(err => console.error("Fetch error:", err));
}

function getNextTask() {
    fetch("/next_task")
        .then(response => response.json())
        .then(data => {
            document.querySelectorAll(".task").forEach(el => {
                el.classList.remove("selected");
            });

            const task = document.getElementById(data.task_id);
            if (task) {
                task.classList.add("selected");
                console.log("done");

                task.scrollIntoView({behavior: "smooth", block: "center"});
            }
        })
        .catch(err => console.error("Error fetching next task:", err));
}

function getSummary() {
    fetch("/get_summary")
        .then(response => response.json())
        .then(data => {
            document.getElementById("summary-text").innerText = data.summary || "No summary yet.";
        })
        .catch(error => {
            console.error("Error fetching summary:", error);
            document.getElementById("summary-text").innerText = "⚠️ Failed to load summary.";
        });    
}

function refreshSummary() {
    fetch("/summary", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            document.getElementById("summary-text").innerText = data.summary || "No summary yet.";
        })
        .catch(error => {
            console.error("Error refreshing summary:", error);
            document.getElementById("summary-text").innerText = "⚠️ Failed to generate summary.";
        });
}

//written by chatgpt
function searchTasks() {
    const searchInput = document.getElementById("search");
    if (!searchInput) return;

    searchInput.addEventListener("input", async (e) => {
        const query = e.target.value;
        try {
            const res = await fetch(`/?search=${encodeURIComponent(query)}`);
            if (!res.ok) throw new Error("Network response was not ok");
            
            const html = await res.text();
            const newBoard = new DOMParser()
                .parseFromString(html, "text/html")
                .querySelector("#kanban-board");

            if (newBoard) {
                document.querySelector("#kanban-board").innerHTML = newBoard.innerHTML;
            }
        } catch (err) {
            console.error("Error fetching search results:", err);
        }
    });
}