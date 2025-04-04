import json
import os
import re

def sanitize_filename(filename):
    """Sanitizes the filename by removing invalid characters."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename).strip()

def extract_valid_json(response):
    """Extracts and parses valid JSON from the model response, handling markdown formatting and invalid escape characters."""
    try:
        # Step 1: Remove markdown code block formatting
        match = re.search(r"```json\n(.*?)\n```", response, re.DOTALL)
        if match:
            response = match.group(1).strip()

        # Step 2: Clean up control characters and escape sequences safely
        response = response.replace('\\n', ' ').replace('\\r', ' ').replace('\\t', ' ')
        response = response.encode('utf-8').decode('unicode_escape')  # Handles \x, \u, etc. safely

        # Step 3: Load JSON safely
        return json.loads(response)

    except json.JSONDecodeError as e:
        print(f"❌ JSON Parsing Error: {e}")
        return None
    except UnicodeDecodeError as e:
        print(f"❌ Unicode Decode Error: {e}")
        return None

def store_emails_data(email_data_list):
    """Ensures email_data_list is a list and stores emails correctly."""

    # Convert single dictionary to a list
    if isinstance(email_data_list, dict):
        email_data_list = [email_data_list]  

    # Ensure it's a valid list
    if not isinstance(email_data_list, list):
        print(f"❌ Invalid email data format: {type(email_data_list)}")
        return  

    # Ensure the output folder exists
    output_folder = "parsed_emails"
    os.makedirs(output_folder, exist_ok=True)

    for idx, email_json in enumerate(email_data_list):
        try:
            if not isinstance(email_json, dict):  # Ensure it's a dictionary
                raise TypeError(f"Invalid email entry at index {idx}: {type(email_json)}")

            # Extract and sanitize subject
            subject = email_json.get("subject", f"No_Subject_{idx+1}")
            subject = sanitize_filename(subject)

            # Define file path
            file_path = os.path.join(output_folder, f"{subject}.txt")

            # Clean up the body text
            body_text = email_json.get("body", "").replace("\n", " ").replace("\r", " ")

            # Format email data as text
            email_text = (
                f"To: {email_json.get('to', '')}\n"
                f"From: {email_json.get('from', '')}\n"
                f"CC: {email_json.get('cc', 'N/A')}\n"
                f"BCC: {email_json.get('bcc', 'N/A')}\n"
                f"Subject: {email_json.get('subject', '')}\n"
                f"Tags: {email_json.get('tags', '')}\n"
                f"Body:\n{body_text}\n"
                f"{'-' * 80}\n"
            )

            # Append if it's a chain, otherwise create a new file
            write_mode = "a" if os.path.exists(file_path) else "w"
            with open(file_path, write_mode, encoding="utf-8") as f:
                f.write(email_text)

            print(f"✅ Stored email in: {file_path}")
        except Exception as e:
            print(f"❌ Error storing email {idx+1}: {e}")