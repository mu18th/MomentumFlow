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
    div.style.backgroundColor = isError ? "#e74c3c" : "#2785aeff";
    div.style.zIndex = "9999";
    document.body.appendChild(div);
    setTimeout(() => div.remove(), 3000);
}

// helper for direct access to form throw pressing + in the keyboard, written by chatgpt
document.addEventListener("DOMContentLoaded", () => {
    document.addEventListener("keydown", (e) => {
        if (e.key.toLowerCase() === "+") {
            e.preventDefault();

            const hint = document.createElement("div");
            hint.textContent = "Press + → Go to Add Task page";
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
});

function DragAndDrop() {
    /* Drag and Drop function: method that give the ability to grap and drop tasks and refresh the board after dropping */

    //Drap part
    const draggableTasks = document.querySelectorAll("[draggable='true']");

    draggableTasks.forEach(task => {
        task.addEventListener("dragstart", e => {
            e.dataTransfer.setData("text/plain", task.id);
        });
    });

    const taskLists = document.querySelectorAll(".task-list");
    taskLists.forEach(taskList => {
        // effect showing when dragging over a column
        taskList.addEventListener("dragover", e => {
            e.preventDefault();
            taskList.classList.add("task-list--over");
        });

        // remove effect
        taskList.addEventListener("dragleave", () => {
            taskList.classList.remove("task-list--over");
        });

        // Drop part
        taskList.addEventListener("drop", async e => {
            e.preventDefault();
            const droppedTaskId = e.dataTransfer.getData("text/plain");
            const droppedTask = document.getElementById(droppedTaskId);

            const originalList = droppedTask.closest(".task-list");

            taskList.appendChild(droppedTask);
            taskList.classList.remove("task-list--over");
            
            // Data to be send to the route
            var entry = {
                taskID: droppedTask.id,
                status: taskList.id
            };

            console.log(entry);

            // Updating part
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

                // if moved to done and has subtasks, move sub tasks with their father
                if (entry.status === "Done" && data.subtasks) {
                    alert("This task has subtasks. Press OK to refresh the page and update the board.")
                    location.reload(true);
                    return;
                }

                // update the board if not 
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

                // refresh the method to not lose the Drag and Drop ability
                DragAndDrop();

                console.log(entry.status);
            } catch(err) {
                console.error("Fetch error:", err);
            } 
        });
    });
}

function generateTask(id, btn) {
    /*Generate Task function, connected to generate_subtasks route and Generate 3 subtasks btn
      it is responsiable of the generating of subtasks using AI */
    
    btn.setAttribute("data-loading", "true");
    
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
        .catch(err => console.error("Fetch error:", err))
        .finally(() => btn.setAttribute("data-loading", "false"));
}

function deleteTask(id) { 
    /* deleteTaks function: it is connected to delete-task route and delete Task btn
       it is responsiable of deleting a single tasks using given ID and it subtasks 
       if exist (need a refresh to be shown in the board) */
    
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
            // refresh Drag and Drop 
            DragAndDrop();
            return response.json();
        })
        .then(data => {
            if (data) console.log(data);
        })
        .catch(err => console.error("Fetch error:", err));
}

function getNextTask(btn) {
    /* a function connected to next_task route and (what should I do now?) btn, 
       responsiable of chosing one tasks that is the most important in the exiting board 
       through AI or a specific chosen order */
    
    btn.setAttribute("data-loading", "true");
    
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
                // refresh Drag and Drop
                DragAndDrop();
            }
        })
        .catch(err => console.error("Error fetching next task:", err))
        .finally(() => btn.setAttribute("data-loading", "false"));
}

function getSummary() {
    /* a function connected to get_summary route and (Get Summary) btn,
       responsiable of showing the last saved summary of the tasks in the DB 
       and show it in the summary area under the board */

    fetch("/get_summary")
        .then(response => response.json())
        .then(data => {
            document.getElementById("summary-text").innerText = data.summary || "No summary yet, click Refresh Summary to generate one.";
            document.getElementById("summary-text").classList.add("showin");
            // refresh  Drag and Drop
            DragAndDrop();
        })
        .catch(err => {
            console.error("Error fetching summary:", err);
            document.getElementById("summary-text").innerText = "⚠️ Failed to load summary.";
        });    
}

function refreshSummary(btn) {
    /* a function connected to summary route and (Refresh Summary) btn,
       responsiable of generating a summary of the existing tasks in the board 
       through AI and show it in the summary area under the board */
    
    btn.setAttribute("data-loading", "true");
    
    fetch("/summary", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            document.getElementById("summary-text").innerText = data.summary || "No summary yet.";
            document.getElementById("summary-text").classList.add("showin");
        })
        .catch(err => {
            console.error("Error refreshing summary:", err);
            document.getElementById("summary-text").innerText = "⚠️ Failed to generate summary.";
        })
        .finally(() => btn.setAttribute("data-loading", "false"));
}

function updateBoard() {
    /* a function connected to the main route and responsiable of updating the board
       according to the search input and filters (priority, start date, end date) */
    
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
            // refresh Drag and Drop
            DragAndDrop();
        })
        .catch(err => console.error("Error fetching board:", err));

}

function initBoardControls() {
    /* a function that init the board controls: search input and filters */

    const searchInput = document.getElementById("search");
    if (searchInput)
        searchInput.addEventListener("input", updateBoard);

    ["priority-filter", "start-date", "end-date"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener("change", updateBoard);
    });
}

// Initialize Drag and Drop and Board Controls on DOMContentLoaded
document.addEventListener("DOMContentLoaded", DragAndDrop);
document.addEventListener("DOMContentLoaded", initBoardControls)