document.addEventListener('DOMContentLoaded', function() {
    const draggableTasks = document.querySelectorAll("[draggable='true']");

    //drag tasks
    draggableTasks.forEach(task => {
        task.addEventListener("dragstart", e => {
            e.dataTransfer.setData("text/plain", task.id);
        });
    });

    //drop tasks
    const taskLists = document.querySelectorAll(".task-list");
    taskLists.forEach(taskList => {
        taskList.addEventListener("dragover", e => {
            e.preventDefault();
            taskList.classList.add("task-list--over");
        });

        taskList.addEventListener("dragleave", e => {
            taskList.classList.remove("task-list--over");
        })

        taskList.addEventListener("drop", e => {
            e.preventDefault();
            const droppedTaskId = e.dataTransfer.getData("text/plain");
            const droppedTask = document.getElementById(droppedTaskId);

            taskList.appendChild(droppedTask);
            taskList.classList.remove("task-list--over");
        });
    });
});
