from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from imap import fetch_unread_emails
from dotenv import load_dotenv

# load the end
load_dotenv()

# define the required model
model = OllamaLLM(model="gemma3")

# sample prompt template
template = """
You are an expert in analyzing all the email data given to you, 
Your task is to Look into the data given to you and answer the user's question in a formatted way

**User Question** : {user_question}

**Email Data** : {email_data}
"""

# pass data to prompt via templete
prompt = ChatPromptTemplate.from_template(template)

# fetch the emails
emails = fetch_unread_emails()

# format it
email_data = "\n\n".join(
    [f"📧 From: {e['from']}\n📌 Subject: {e['subject']}\n📝 Body: {e['body']}" for e in emails]
) if emails else "No new emails found."

user_question = input("Ask question: ")

# invoke chain. combine multiple things to run llm
# here the prompt is then formatted with the data and then pased to model below and response is generated
chain = prompt | model 

# invoke the ollama and pass it
result = chain.invoke({"email_data": email_data, "user_question": user_question})
print(result)