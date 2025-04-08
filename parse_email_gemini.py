from google import genai
from dotenv import load_dotenv
from imap import fetch_all_emails
from utils.store_emails import store_emails_data
from pydantic import BaseModel, Field
import os
import json
import time

# load the env
load_dotenv()
start_time = time.time()
print(f"Started at {start_time}")   

# initialize gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
print("client", client)

# define prompt
prompt = """  You are a highly skilled data analyst specializing in extracting actionable insights from email communications. 
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
                "tags": "Analyze the email and assign relevant tags from the list below. Select the most appropriate tags based on the email's content.  Tags should be comma-separated."
              }}
              ```           
              ### **Important Guidelines & Constraints:**
                - **Content Preservation: Absolutely do not modify or alter the original email content unless it contains HTML**. Maintain the original wording and formatting as closely as possible.
                - **HTML Handling**: If the email contains HTML content, parse and convert it into a simple text format.** Ensure that the essence of the message is retained while removing any unnecessary HTML tags or attributes.
                - **Tagging**: Use only the specified tags for categorizing the email. The tags are: "Invoice, Order Confirmation, Payments, Meeting Invite/Calendar Invite, Meeting Update, Newsletter, Promotional / Marketing / Advertisement, Support Ticket Confirmation, Support Ticket Update, Banking, Travel, Health/Medical, Event/Registration, Approval Request, Approval Confirmation, Urgent/High priority, For review". Ensure that the tags accurately reflect the content of the email.
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
        
# define a pydantic model to validate the response from the model
class EmailResponse(BaseModel):
    to: str = Field(..., description="Receiver's email id")
    from_: str = Field(..., alias='from', description="Sender email id")
    cc: str = Field(..., description="Email id present in cc")
    bcc: str = Field(..., description="Email id present in bcc")
    subject: str = Field(..., description="Subject of the email")
    body: str = Field(..., description="Body of the email")
    tags: list[str] = Field(..., description="Tags assigned to the email")
    
# get the emails from the inbox
emails = fetch_all_emails()

print("length", len(emails))
# print("emails", emails)
# print("prompt", prompt)

processed_emails = []
for email_data in emails:
    try:
        # pass the data in prompt
        response = client.models.generate_content(
            model = os.getenv("MODEL_NAME"),
            contents = prompt.format(email_data=email_data),
            config={
                'response_mime_type': 'application/json',
                'response_schema': EmailResponse
            }
        )
        
        json_response = response.parsed.json()
        print("json response ", json_response, type(json_response))
        
        response_dict = json.loads(json_response)
        print("Formatted json", json.dumps(response_dict, indent=4))
        processed_emails.append(response_dict)
        # print("response text", response.text, type(response.text))
        # print("response parsed", response.parsed, type(response.parsed))
        
    except Exception as e:
        print(f"❌ Error processing email: {e}")
        print("error", e.with_traceback())

# print("processed emails", processed_emails)
print("Ended at ", time.time())
print("Total time taken: ", time.time() - start_time)
print("processed emails", processed_emails)
# store the emails in the file
store_emails_data(processed_emails)