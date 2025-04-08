from utils.store_emails import store_emails_data, extract_valid_json
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from pydantic import BaseModel, Field
from imap import fetch_all_emails
from dotenv import load_dotenv
from typing import Optional
import time
import json

# load the end
load_dotenv()
start_time = time.time()
print(f"Started at {start_time}")

# define a pydantic class to get structured output from the model
class EmailResponse(BaseModel):
    to: str = Field(..., description="Receiver's email id")
    from_: str = Field(..., alias='from', description="Sender email id")
    cc: Optional[str] = Field(..., description="Email id present in cc")
    bcc: Optional[str] = Field(..., description="Email id present in bcc")
    subject: str = Field(..., description="Subject of the email")
    body: str = Field(..., description="Body of the email")
    tags: list[str] = Field(..., description="Tags assigned to the email")
    
# select the req model
model = OllamaLLM(model="gemma3")

# set up a parser to get JSON output
parser = PydanticOutputParser(pydantic_object=EmailResponse)

# define a prompt template with data to be passed
template = """You are a highly skilled data analyst specializing in extracting actionable insights from email communications. 
              Your primary task is to meticulously transform raw email data into a structured JSON format, providing a concise and informative representation of each email.
              
              ### **Objective**: Convert the provided raw email data into a JSON object adhering to the specified schema.

              ### **Output JSON format:**
              ```json
              {{
                "to": "receiver's email id",
                "from": "sender email id",
                "cc": "return any email id present in cc else null",
                "bcc": "return any email id present in bcc else null",
                "subject": "return the subject of the email",
                "body": "return the exact body of the email if it does not contain any html content. If the body contains any html content, then return it in markdown format",
                "tags": "Analyze the email and assign relevant tags from the list below. Select the most appropriate tags based on the email's content. The tags should be returned as a JSON list of strings. Example: `["Project Update", "Urgent/High priority"]"
              }}
              ```           
              ### **Important Guidelines & Constraints:**
                - **Content Preservation: Absolutely do not modify or alter the original email content unless it contains HTML**. Maintain the original wording and formatting as closely as possible.
                - **HTML Handling**: If the email contains HTML content, parse and convert it into a simple text format.** Ensure that the essence of the message is retained while removing any unnecessary HTML tags or attributes.
                - **Tagging**: Use only the specified tags for categorizing the email. The tags should be returned as a JSON list of strings. Example: `["Project Update", "Urgent/High priority"]. The tags are: "Invoice, Order Confirmation, Payments, Meeting Invite/Calendar Invite, Meeting Update, Newsletter, Promotional / Marketing / Advertisement, Support Ticket Confirmation, Support Ticket Update, Banking, Travel, Health/Medical, Event/Registration, Approval Request, Approval Confirmation, Urgent/High priority, For review, Project Update, Internal Anouncement, Report, Expense Report, IT Notification, HR". Ensure that the tags accurately reflect the content of the email.
                - **Email Address Formatting**: Ensure that email addresses are formatted correctly. Include the name followed by the email ID in the respective fields (to, from, cc, bcc).
                - **JSON Output**: **Strictly return your final output as a valid JSON object. Ensure the JSON is well-formed and easily parsable.**
                - **Error Handling**: If any errors occur during processing, provide a clear and concise error message indicating the nature of the issue.
                
              ### **Points to Remember (Reiteration for Clarity):**
                - ### **No Modification**: Preserve original email content.
                - ### **HTML Parsing**: Extract plain text from HTML emails.
                - ### **Limited Tags**: Use only the provided tag list.
                - ### **Accurate Identification**: Correctly populate recipient fields.
                - ### **JSON Format**: Return only valid JSON.
                - ### **Error Reporting**: Clearly indicate any errors encountered.
              **Email Data** : {email_data}
          """
          
# create prompt template to pass the data
prompt = ChatPromptTemplate.from_template(template).partial(format_instructions=parser.get_format_instructions())

# fetch the emails
emails = fetch_all_emails()

print("length", len(emails))
print("emails", emails, end="\n\n")
print("prompt", prompt, end="\n\n")

# process email 
processed_emails = []
for email_data in emails:
    try:
        # Make a chain to pass the prompt to the model along with the parser to get the required output
        chain = prompt | model | parser
        print("chain", chain)

        # Invoke the chain
        result = chain.invoke({"email_data": email_data})

        print("✅ Parsed result: ", result, end="\n\n")

        if isinstance(result, EmailResponse):
            processed_emails.append(result.model_dump())
        else:
            print(f"❌ Invalid response format: {type(result)}")

    except Exception as e:
        print(f"❌ Error processing email in parse email: {e}")
        
print("Ended at ", time.time())
print("Total time taken: ", time.time() - start_time)
print("processed emails", processed_emails)

# Store the processed emails
store_emails_data(processed_emails)