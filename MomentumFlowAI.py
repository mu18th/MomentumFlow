"""here are the three functions that call AI to give the app features where each function role is 
   explained in a variable named prompt (inspired from CS50x AI lecture)
   limitation is that it is using free AI API for now"""

# Standard library imports
import os
import re

# Third-party imports
from dotenv import load_dotenv
from openai import OpenAI

env_path = os.path.join("MomentumFlow", ".env")
load_dotenv(dotenv_path=env_path)

def generate_subtasks(title: str, description: str):

    prompt = f"""
    You are a project manager. Break the following task into exactly 3 actionable subtasks.
    Each subtask must 
    - begin with an action verb 
    - be concise
    - describe a clear action.

    Main Task Title = {title}
    Main Task Description = {description if description else "No description provided"}
    
    Output format (plain text only):
    (1) ...
    (2) ...
    (3) ...

    Do NOT add extra commentary, bullet points, special tokens, or explanations.
    """

    # call the API and handle errors
    try:
        client = OpenAI(
        base_url = "https://openrouter.ai/api/v1",
        api_key = os.getenv("OPENROUTER_API_KEY"),
        )
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b:free",
            messages=[
                {"role": "system", "content": "You are a helpful AI project manager."},
                {"role": "user", "content": prompt}
            ]
        )
    
        # get content, clean data and save the important parts
        text_output = response.choices[0].message.content
        text_output = re.sub(r"<[^>]+>", "", text_output)

        lines = [
            re.sub(r"^[\s\-•\d\).]*", "", line).strip()
            for line in text_output.split("\n")
            if line.strip()
        ]
        # ensure exactly 3 subtasks and return
        subtasks = lines[:3] 

        return subtasks  

    except Exception as e:
        print(e)
        return "Error"


def suggest_next_task(tasks: list):

    # specific data of given tasks to be sent to AI
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
            suggest which task I should work on next. Consider urgency, priority.
            Reply with ONLY the task ID as a number. Do not include explanations, text, symbols, JSON, or special tokens.
            If multiple tasks are equally important, choose the one with the earliest due date.

            Tasks:
            {tasks_list}
            """

    try:
        client = OpenAI(
            base_url= "https://openrouter.ai/api/v1",
            api_key= os.getenv("OPENROUTER_API_KEY"),
        )

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b:free",
            messages=[
                {"role": "system", "content": "You are a helpful AI project manager."},
                {"role": "user", "content": prompt}
            ]
        )

        # get content, clean data and save the important parts, then return
        raw_output = response.choices[0].message.content
        raw_output = re.sub(r"<[^>]+>", "", raw_output)

        match = re.search(r"\d+", raw_output)
        return int(match.group(0))

    except Exception as e:
        print("Error in suggest_next_task:", e)  
        return None


def summarize_board(tasks: list):
    tasks_list = [
        {
            "title": t["title"],
            "description": t["description"],
            "status": t["status"],
            "priority": t["priority"],
            "due_date": t["due_date"].isoformat() if t["due_date"] else None
        }
        for t in tasks
    ]

    prompt = f"""
        You are summarizing a task board. Write a concise summary in 1–2 sentences (maximum 3). 
        Focus on what is urgent, pending, or blocked. Do NOT return bullet points, lists, JSON, or special tokens.
        Output plain text only.

        board data:
        {tasks_list}
    """

    try:
        client = OpenAI(
            base_url= "https://openrouter.ai/api/v1",
            api_key= os.getenv("OPENROUTER_API_KEY"),
        )

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b:free",
            messages=[
                {"role": "system", "content": "You are a helpful AI project manager."},
                {"role": "user", "content": prompt}
            ]
        )

        # get content, clean data and save the important parts, then return
        summary_text = response.choices[0].message.content.strip()
        summary_text = re.sub(r"<[^>]+>", "", summary_text)
        summary_text = summary_text.replace("▁", " ")

        return summary_text
    
    except Exception:
        return "Could not generate summary right now."

# test I used for functions to ensure it works
if __name__ == "__main__":
    title = "Develop and launch a new company website"
    description = "The new website needs a modern framework, an e-commerce section, and a blog."

    subtasks = generate_subtasks(title, description)

    print("\nGenerated Subtasks:")
    for task in subtasks:
        print(task)