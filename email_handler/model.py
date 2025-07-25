import os
from dotenv import load_dotenv
from openai import OpenAI
from IPython.display import display, Markdown

# Load environment variables from .env file
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

# Initialize the OpenAI client with the Gemini API key
client = OpenAI(api_key=gemini_api_key)

system_prompt = """ Imagine You are a obident Assistent for the user,you have to identify is the mail is about events, club related,\
            office ralted placements or internship,along with dates and time of the events or palcements deadline in it or any office ralted and return simple summary yet more informative and return it in markdown format."""

def user_prompt(email_content):
    return f"""
    You are an AI assistant that helps users manage their emails.\
    Your task is to analyze the following email content and provide a concise summary or action items.\
    Focus on identifying key information, deadlines, and any actions the user should take.\
    If the email contains any dates or deadlines, highlight them clearly.

    Email Content:
    {email_content}
    """


email_content = """"""
 
message = [
    {
        "role": "system",
        "content": system_prompt
    },
    {
        "role": "user",
        "content": user_prompt(email_content)
    }
]

def summerize(email_content):
    """
    Summarizes the given email content using the Gemini API.
    
    Args:
        email_content (str): The content of the email to summarize.
        
    Returns:
        str: The summary or action items extracted from the email.
    """
    if not email_content.strip():
        return "No email content provided."
    message[1]["content"] = user_prompt(email_content)
    gemini_via_openai_client = OpenAI(
    api_key=gemini_api_key, 
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    response = gemini_via_openai_client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=message,
    )
    summary = response.choices[0].message.content.strip()
    return summary



display(summerize(email_content))



# system_prompt = """
# You are a helpful assistant that can answer questions about email handling and management.\
#     Your responses should be concise and informative, providing clear instructions or explanations as needed.\
#         if there is any dates deadlines or specific information, make sure to highlight them clearly.\
#             look for mails that are related to the following topics:\
#                 - Palcement, projects, manager,Job applications and interviews, or job related, Internship opportunities or any updates to those category related emails\
#                 - Emails that require immediate attention or action\
#                 - Emails that contain important information or updates\
#                 - Emails from office or collage or from colleagues or from your manager\
#         return the reponse in markdown format."""