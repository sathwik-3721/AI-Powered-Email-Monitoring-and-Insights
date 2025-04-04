from utils.store_emails import store_emails_data, extract_valid_json
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from imap import fetch_all_emails
from dotenv import load_dotenv

# load the end
load_dotenv()

model = OllamaLLM(model="gemma3")

template = """You are an expert in transforming email data into informational insights. Your task is to convert the given raw email data into processed data into the below JSON format
            The email data to be parsed is given at the end of the prompt.

            ### **Output JSON format:**
            ```json
            {{
                "to": "receiver's email id",
                "from": "sender email id",
                "cc": "return any email id present in cc else null",
                "bcc": "return any email id present in bcc else null",
                "subject": "return the subject of the email",
                "body": "return the exact body of the email if it does not contain any html content. If the body contains any html content, then return it in markdown format",
                "tags": "Analyze the email and add tags/categories for the email like task, call, remainder etc. Select the tags from below given Points to remember"
            }}
            Points to be remembered:
            1. **Do not alter/change/modify any email content unless it contains any html code**.
            2. **If the email contains html content, then parse and understand it into simple text contents**
            3. **Use only the following appropriate tags for the email - "Invoice, Order Confirmation, Payments, Meeting Invite/Calendar Invite, Meeting Update, Newsletter, Promotional / Marketing / Advertisement, Support Ticket Confirmation, Support Ticket Update, Banking, Travel, Health/Medical, Event/Registration, Approval Request, Approval Confirmation, Urgent/High priority, For review"
            4. **Make sure to tag an email based on its content and tags must be added based on the tags which are provided in above point**. 
            5. **Make sure to add their name followed by email id in their respective fields like to, from, cc and bcc.
            6. **Return** your final output **as JSON** **

            **Email Data** : {email_data}
        """

# create prompt template to pass the data
prompt = ChatPromptTemplate.from_template(template)

# fetch the emails
emails = fetch_all_emails()

print("length", len(emails))
print("emails", emails)
print("prompt", prompt)

# process email 
processed_emails = []
for email_data in emails:
    try:
        # make a chain to pass the prompt to model
        chain = prompt | model

        # invoke the chain
        result = chain.invoke({"email_data": email_data})
        print("result before parsing: ", result)

        # remove the markdown content
        parsed_email_data = result.replace("```json", "").replace("```", "").strip()
        print("result after parsing: ", parsed_email_data)

        email_json = extract_valid_json(parsed_email_data)
        if email_json and isinstance(email_json, dict):
           processed_emails.append(email_json)
        else:
            print("Invalid email response: ", email_json)
            
    except Exception as e:
        print(f"❌ Error processing email in parse email: {e}") 
        
# store the processed emails
store_emails_data(processed_emails)