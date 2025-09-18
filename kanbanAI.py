import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

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
        api_key = api_key,
        )
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1:free",
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

# test
if __name__ == "__main__":
    title = "Develop and launch a new company website"
    description = "The new website needs a modern framework, an e-commerce section, and a blog."

    subtasks = generate_subtasks(title, description)

    print("\nGenerated Subtasks:")
    for task in subtasks:
        print(task)