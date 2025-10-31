
// helper for messages showing, written by chatgpt
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
/*
// helper for direct access to form throw keyboard, written by chatgpt
document.addEventListener("DOMContentLoaded", () => {
    document.addEventListener("keydown", (e) => {
        if (e.key.toLowerCase() === "f") {
            e.preventDefault();

            const hint = document.createElement("div");
            hint.textContent = "Press F → Go to Add Task page";
            hint.style.position = "fixed";
            hint.style.top = "20px";
            hint.style.right = "20px";
            hint.style.background = "#007bff";
            hint.style.color = "white";
            hint.style.padding = "10px";
            hint.style.borderRadius = "5px";
            hint.style.zIndex = 1000;
            document.body.appendChild(hint);

            setTimeout(() => {
                hint.remove();
                window.location.href = "/addtask";
            }, 800); 
        }
    });
});*/

//drag tasks
function DragAndDrop() {
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

        taskList.addEventListener("drop", async e => {
            e.preventDefault();
            const droppedTaskId = e.dataTransfer.getData("text/plain");
            const droppedTask = document.getElementById(droppedTaskId);

            const originalList = droppedTask.closest(".task-list");

            taskList.appendChild(droppedTask);
            taskList.classList.remove("task-list--over");
            
            var entry = {
                taskID: droppedTask.id,
                status: taskList.id
            };

            console.log(entry);

            try {
                const res = await fetch(`${window.location.origin}/update-status`, {
                    method: "POST",
                    credentials: "include",
                    body: JSON.stringify(entry),
                    cache: "no-cache",
                    headers: { "content-type": "application/json" }
                });

                if (!res.ok) {
                    alert("Failed to update task status.");

                    if (originalList) originalList.appendChild(droppedTask);
                    console.log(`Response not OK: ${res.status}`);
                    return;
                }

                const data = await res.json();

                if (entry.status === "Done" && data.subtask_ids && data.subtask_ids.length > 0) {
                    alert("This task has subtasks. Press OK to refresh the page and update the board.")
                    location.reload(true);
                    return;
                }

                const ccolumnRes = await fetch(`/column/${entry.status}/html`);
                if (!ccolumnRes) throw new Error("Faild to fetch column html");

                const html = await ccolumnRes.text();
                const newCol = new DOMParser()
                    .parseFromString(html, "text/html")
                    .querySelector(`#${entry.status}`);

                if (newCol) {
                    const oldCol = document.getElementById(entry.status);
                    oldCol.innerHTML = newCol.innerHTML;
                }

                DragAndDrop();

                console.log(entry.status);
            } catch(err) {
                console.error("Fetch error:", err);
            } 
        });
    });
}

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
            const task = document.getElementById(id);
            if (task) task.remove();

            showMessage("Task deleted. Regresh the page if there are subtasks of it to be deleted");
            DragAndDrop();
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
                DragAndDrop();
            }
        })
        .catch(err => console.error("Error fetching next task:", err));
}

function getSummary() {
    fetch("/get_summary")
        .then(response => response.json())
        .then(data => {
            document.getElementById("summary-text").innerText = data.summary || "No summary yet.";
            DragAndDrop();
        })
        .catch(err => {
            console.error("Error fetching summary:", err);
            document.getElementById("summary-text").innerText = "⚠️ Failed to load summary.";
        });    
}

function refreshSummary() {
    fetch("/summary", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            document.getElementById("summary-text").innerText = data.summary || "No summary yet.";
        })
        .catch(err => {
            console.error("Error refreshing summary:", err);
            document.getElementById("summary-text").innerText = "⚠️ Failed to generate summary.";
        });
}

function updateBoard() {
    const searchInput = document.getElementById("search").value.trim();
    const priority = document.getElementById("priority-filter").value;
    const start = document.getElementById("start-date").value;
    const end = document.getElementById("end-date").value;

    const params = new URLSearchParams();
    if (searchInput) params.append("search", searchInput);
    if (priority) params.append("priority", priority);
    if (start) params.append("start", start);
    if (end) params.append("end", end);

    fetch(`/?${params.toString()}`)
        .then(res => res.text())
        .then(html => {
            const newBoard = new DOMParser()
                .parseFromString(html, "text/html")
                .querySelector("#kanban-board");
            if (newBoard)
                document.querySelector("#kanban-board").innerHTML = newBoard.innerHTML;
            DragAndDrop();
        })
        .catch(err => console.error("Error fetching board:", err));

}

function initBoardControls() {
    const searchInput = document.getElementById("search");
    if (searchInput)
        searchInput.addEventListener("input", updateBoard);

    ["priority-filter", "start-date", "end-date"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener("change", updateBoard);
    });
}

/*function refresh_event_listener() {
    DragAndDrop;
    initBoardControls;
}*/

document.addEventListener("DOMContentLoaded", DragAndDrop);
document.addEventListener("DOMContentLoaded", initBoardControls)