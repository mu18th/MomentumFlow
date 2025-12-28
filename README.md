# MomwntumFlow
#### Video Demo:  <URL HERE>
#### Description: 
MomwntumFlow is a **simple Smart Task Manager** web application featuring a Kanban-style board helps users to organize their work efficiently.
It allows users to manage tasks visually, drag and drop them between colmuns, and leverage AI-powered features to improve produactivity and reduce distractions.

## Technologies Used
* Flask
* HTML5
* CSS3
* python3
* JS
* PostgreSQL
* AI API

## Features
* User authentication (register, login, logout)
* Kanban board with three columns: **To Do → In Progress → Done**
* Due dates, priorities, and repeating tasks
* Drag and drop tasks between columens.
* Visual workfolw organization
* Distinctive colors for columns, buttons, priority, deadlines
* AI-generated **subtasks**, **summaries**, and **next-task suggestion**
* Subtasks fully connected to their parent task 
* Task filtering and searching within the board
* Buttons to update and delete tasks
* Keyboard shorcut: press + to instatly add a task
* Flash messages to indicate successful or failed actions
* Persistent PostgreSQL database
* Fully deployed on Render
* Secure sessions + protected API keys


# Project Files 
1. HTML templates
   - layout.htmlThe base template inherited by all other templates.
     It includes:
      * The <head> section with all CSS and JS links.
      * The navigation bar (for both logged-in and logged-out users).
      * Flash message rendering.
      * The footer.

   - index.html:
     The main page of the application.
     It contains:
      * Search and filter controls.
      * The Kanban board.
      * Action buttons below the board.
      This template uses _column.html to render tasks inside each board column.

   - _column.hrml:
      A partial Jinja template responsible for rendering tasks within each Kanban column. 
      It handles differences between task states:
       * **Done tasks display fewer details**, since completed tasks are less relevant in daily workflow.
       * **Done tasks are not draggable** by design
         From a logical workflow perspective, if a user wants to move a completed task back to another status, the **Update Task** action must be used instead.
       * This helps prevent accidental changes and keeps task history intentional.
   - addtask.html:
      Represents the form used to add a new task to the Kanban board.
      The form includes the following fields:
       * **Title**: text field, **required**
       * **Description**: optional text area for task details, more valeable for heavy tasks .
       * **Priority**: selectable value (Low / Medium / High), defulate is Low.
       * **Status**: selectable value (To Do / In progress / Done), defulate is To Do.
       * **Due Date**: optional date picker.
      The form is intentionally simple to allow fast task creation, with sensible defaults so the user only needs to provide a title if desired.
   - edittask.html:
      Represent the form to update exict task in the Kanban board.
      The form includes **same fields as** addtask.html, but with all inputs are **pre-filled with the task’s currently saved data**, allowing the user to:
       * Modify the task title or description.
       * Change priority or due date.
       * Update the task status (including moving it between columns).
      This design ensures **full control over task updates** while keeping the user experience consistent with task creation.
      This property is mainly useful for AI generated subtasks.
   - register.html:
     Represent the form to register a new user.
     The form includes the following fields:
      * **Username**: text field, **required**.
      * **email**: optional.
      * **Password**: text field, **required**, min length **8**, max length **20**.
      * **Confirme Password**: used to confirme entered password.
      Basic validation is applied to ensure correct and secure user input before account creation.
   - login.html:
     Represent the form to login.
     The form includes the following fields:
      * **Username**: text field, **required**.
      * **Password**: text field, **required**, min length **8**, max length **20**.
   - appology.html:
     Represent the apology page.
     Displays an appropriate error message when something goes wrong (such as invalid input, unauthorized access, or missing data) and allows the user to return safely.

2. Python Files
   - app.py:
   Main file that manage the whole app pages and routes.

   It includes:
    * Application configuration.
    * Session configuration using the filesystem.
    * 13 Routes with functions:
      + **index(status)**: 
        The main application page.
        Displays the Kanban board and handles task filtering and searching.
      + **column_html()**:
        Updates an entire column when a task is dropped into it (used mainly for the **Done** column).
        Certain buttons and task details (such as subtasks generation, due date, and priority) are hidden in this column.
      + **addtask()**: 
        Connected to the Add Task form.
        Receives task data from the user and stores it in the database.
      + **editTask(id)**: 
        Updates an existing task.
        Displays a form similar to the Add Task form and is especially useful for editing AI-generated subtasks.
        Can be accessed via a URL (similar to a button action).
      + **deleteTask()**: 
        Deletes a task using a POST request via JavaScript.
        If the deleted task is a parent task, all related subtasks are deleted from the database.
        The user is prompted to refresh the page using the showMessage JavaScript function.
      + **updateTaskStatus()**:
        Updates the task status via JavaScript (drag & drop).
        If a parent task is moved to **Done**, all its child tasks are automatically moved to **Done** as well, and a refresh is triggered in the DragAndDrop method.
      + **generateSubtasks()**: 
        Calls the AI to generate **three subtasks** for a selected task (breaking it into smaller steps).
        Connected to the **Generate 3 subtasks** button.
      + **nextTask()**: 
        Calls the AI to suggest the most important task the user should work on next.
        If the AI fails, the system falls back to returning the highest-priority task from the database.
        Connected to the **What should I do now?** button.
      + **summarizeBoard()**: 
        Calls the AI to generate a summary of the current board state and stores it in the database.
        Connected to the **Refresh Summary** button.
      + **getSummay()**: 
        Returns the last saved board summary from the database.
        Connected to the **Summarize the Board** button.
      + **register()**: 
        Registers a new user and stores their credentials securely in the users table.
      + **login()**:
        Authenticates the user and starts a new session.
      + **logout()**: 
        Logs the user out, clears the session, and flashes a confirmation message.

   - MomentumFlowAI.py:
   Handles all **AI-related logic** in the application.

   It includes **three functions**:
     + **generate_subtasks(title: str, description: str)**:
        Receives a task **title** and **description**, then breaks the task into **exactly three actionable subtasks**.
        The design principle is to always divide work into three smaller logical steps—if a subtask is still complex, it can later be broken down again into three subtasks.
        The generated subtasks:
         * Inherit the same structure and fields as the parent task.
         * Are linked to the original task via parent_id (in the db).
         * Appear in the **parent card** above the task action buttons, showing their **title** and **status**.
      + **suggest_next_task(tasks: list)**:
        Receives a list of tasks (excluding **Done** tasks) and returns the **ID of the task with the highest urgency and priority**, based on AI reasoning and task attributes.
      + **summarize_board(tasks: list)**:
        Receives a list of tasks and returns a **concise summary (1–3 sentences)** describing the current state of the board, highlighting urgency and pending work.

   - db.py:
   A dedicated module that **separates database logic from application logic**, encapsulating all PostgreSQL queries and reducing redundancy by exposing reusable database methods.
   
   This file centralizes all database access and contains **16 commands methods**, in addition to the following core utilities:
      + **get_db()**:
        Returns an active database connection for the current request context.
      + **close_db()**:
        Safely closes the database connection at the end of the request lifecycle.
      + **init_db()**:
        Initializes the database schema if it does not already exist.
      + **delete_subtasks_tree(user_id, task_id)**:
        Recursively traverses the subtask tree and deletes all child subtasks belonging to a parent task.
      + **update_subtasks_tree(user_id, task_id, status)**:
        Recursively traverses the subtask tree and updates the status of all child subtasks when a parent task is marked as **Done**.

   - helpers.py:
   A collection of **utility functions** that are not tied to a specific feature or route, inspired by **CS50 Finance** helpers.

   It includes:
      + **apology(message, code=400)**:
        Renders the apology page when an unexpected or unhandled error occurs, displaying an appropriate error message and HTTP status code.
      + **login_required(f)**:
        A decorator that protects routes by requiring the user to be logged in before accessing them.
      + **get_date_deatails()**:
        Returns date-related values which are **today’s date** and **the date after tomorrow**, used for handling **due-soon** and **overdue** task logic.
         
3. JS:
   - **scripts.js**: 
     A client-side JavaScript file that handles all dynamic behaviors and interactions of the Kanban board.
     Each method is responsible for a specific UI or API-related logic.

     It includes the following methods: 
      + **showMessage(message, isError = false)**:
        Displays a temporary floating message to the user for success or error feedback.
      + **Keyboard shortcut (+ key handler)**:
        Allows direct navigation to the Add Task page by pressing the + key, with a visual hint shown before redirection.
      + **DragAndDrop()**:
        Enables drag-and-drop functionality between Kanban columns, updates task status in the backend, refreshes affected columns, and preserves drag-and-drop behavior after updates.
      + **generateTask(task_id, btn)**:
        Calls the AI subtask generation route to generate **exactly 3 subtasks** for a given task and refreshes the board after generation.
      + **deleteTask(task_id)**:
        Deletes a task and its subtasks (if exist) using the backend route and updates the UI accordingly.
      + **getNextTask(btn)**:
        Requests the AI-recommended next task based on urgency and position, highlights it on the board, and scrolls to it smoothly.
      + **getSummary()**:
        Fetches and displays the last saved board summary from the database.
      + **refreshSummary(btn)**:
        Generates a new AI-powered summary of the current board and displays it under the Kanban board.
      + **updateBoard()**:
        Updates the Kanban board dynamically based on search input and filters (priority, start date, end date).
      + **initBoardControls()**:
        Initializes search and filter controls and binds them to board update logic.

4. CSS:
   The application styling is split into two CSS files to separate design system (theme) from layout and component styling, improving maintainability and clarity.

   - theme.css:
     Defines the **global visual theme** of the application using CSS variables.
     Acts as a **design system** and centralizes all colors, gradients, shadows, transitions, and reusable style tokens.

     It includes:
      + **Color palette variables**: primary, secondary, accent, success, warning, danger, and general colors.
      + **Background variables**: main background, cards, navigation bar, buttons, forms, and controls.
      + **Kanban column themes**: distinct gradients and borders for **Todo**, **In Progress**, and **Done** columns.
      + **Text colors**: main text, light text, and muted gray text.
      + **Borders, shadows, and radius variables**: unified border colors, soft/strong shadows, and consistent rounded corners.
      + **Transition presets**: reusable animation timing for smooth UI interactions.
      + **Button and board action themes**: styles for update, delete, generate subtasks, next task, summarize, and refresh actions.
      + **Selected and highlighted states**: styles for selected tasks, due-soon, overdue, and priority indicators.

     In addition, it applies:
      * Global reset and box sizing.
      * Base styling for html, body, navigation bar, headers, buttons, inputs, and footer.
      * Dark mode–friendly defaults across the entire application.

   - style.css:
     Contains the **main structural and component styling** of the application.
     This file builds on top of theme.css variables to style actual UI elements and layouts.

     It includes:
      + **Navigation bar styling**: navbar layout, links, app name, logo animations, and hover effects.
      + **Form styling**: add/edit task forms, inputs, textareas, selects, labels, and submission buttons.
      + **Search and filter controls**: search bar, priority filter, date filters, and their interactive states.
      + **Kanban board layout**: three-column grid layout, column headers, and responsive spacing.
      + **Column-specific styles**: Todo, In Progress, and Done columns with visual separation and emphasis.
      + **Task cards styling**: task containers, titles, descriptions, hover effects, and drag-and-drop feedback.
      + **Task action buttons**: generate subtasks, delete task, update task, and under-board action buttons.
      + **AI interaction indicators**: loading states, progress indicators, and visual feedback when AI actions are running.
      + **Special task states**:
         + Selected task highlight
         + Due soon tasks
         + Overdue tasks
         + Priority-based coloring
      + **Apology page styling** for error handling pages.



