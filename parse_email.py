from utils.store_emails import store_emails_data, extract_valid_json
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from imap import fetch_all_emails
from dotenv import load_dotenv

# load the end
load_dotenv()

# select the req model
model = OllamaLLM(model="gemma3")

# define a prompt template with data to be passed
template = """You are a highly skilled data analyst specializing in extracting actionable insights from email communications. 
              Your primary task is to meticulously transform raw email data into a structured JSON format, providing a concise and informative representation of each email.
              
              ### **Objective**: Convert the provided raw email data into a JSON object adhering to the specified schema.

              ### **Output JSON format:**
              ```json
              {
                "to": "receiver's email id",
                "from": "sender email id",
                "cc": "return any email id present in cc else null",
                "bcc": "return any email id present in bcc else null",
                "subject": "return the subject of the email",
                "body": "return the exact body of the email if it does not contain any html content. If the body contains any html content, then return it in markdown format",
                "tags": "Analyze the email and assign relevant tags from the list below. Select the most appropriate tags based on the email's content.  Tags should be comma-separated."
              }
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