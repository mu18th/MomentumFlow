import os
from dotenv import load_dotenv
from openai import OpenAI
import re


load_dotenv()

def generate_subtasks(title: str, description: str) -> list[str]:

    # prompt for the AI
    prompt = f"""
    You are a project manager. Break the following task into exactly 3 subtasks.
    Each subtask must start with an action verb and be a single, clear action item.

    Main Task Title = {title}
    Main Task Description = {description if description else "No description provided"}
    
    Format: 
    (1) ...
    (2) ...
    (3) ...
    """

    # call the API and handle errors
    try:
        client = OpenAI(
        base_url = "https://openrouter.ai/api/v1",
        api_key = os.getenv("OPENROUTER_API_KEY"),
        )
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3.1:free",
            messages=[
                {"role": "system", "content": "You are a helpful AI project manager."},
                {"role": "user", "content": prompt}
            ]
        )
    
        # get content
        text_output = response.choices[0].message.content

        # clean data and save the important parts
        lines = [line.strip(" -•123)") for line in text_output.split("\n") if line.strip()]
        subtasks = lines[:3] # ensure exactly 3

        return subtasks  

    except Exception as e:
        print(e)
        return "Error"


def suggest_next_task(tasks):

    tasks_list = [
        {
            "id": t["id"],
            "title": t["title"],
            "description": t["description"],
            "status": t["status"],
            "priority": t["priority"],
            "due_date": t["due_date"].isoformat() if t["due_date"] else None
        }
        for t in tasks
    ]

    prompt = f"""
            You are a helpful AI project manager.
            Given the following tasks (id, title, description, status, priority, due_date), 
            suggest which task I should work on next.
            Reply with **only the task ID as a number**, nothing else.

            Tasks:
            {tasks_list}
            """

    try:
        client = OpenAI(
            base_url= "https://openrouter.ai/api/v1",
            api_key= os.getenv("OPENROUTER_API_KEY"),
        )

        response = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3.1:free",
            messages=[
                {"role": "system", "content": "You are a helpful AI project manager."},
                {"role": "user", "content": prompt}
            ]
        )

        raw_output = response.choices[0].message.content

        match = re.search(r"\d+", raw_output)
        return int(match.group(0))

            

    except Exception as e:
        print("Error in suggest_next_task:", e)  
        return None


def summarize_board(tasks):
    tasks_list = [
        {
            "id": t["id"],
            "title": t["title"],
            "description": t["description"],
            "status": t["status"],
            "priority": t["priority"],
            "due_date": t["due_date"].isoformat() if t["due_date"] else None
        }
        for t in tasks
    ]

    prompt = f"""
        Summarize the following board in 1–2 sentences, focusing on what’s urgent or pending:
        {tasks_list}
    """

    try:
        client = OpenAI(
            base_url= "https://openrouter.ai/api/v1",
            api_key= os.getenv("OPENROUTER_API_KEY"),
        )

        response = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3.1:free",
            messages=[
                {"role": "system", "content": "You are a helpful AI project manager."},
                {"role": "user", "content": prompt}
            ]
        )

        summary_text = response.choices[0].message.content.strip()

        return summary_text
    except Exception:
        return "⚠️ Could not generate summary right now."


# test
if __name__ == "__main__":
    title = "Develop and launch a new company website"
    description = "The new website needs a modern framework, an e-commerce section, and a blog."

    subtasks = generate_subtasks(title, description)

    print("\nGenerated Subtasks:")
    for task in subtasks:
        print(task)