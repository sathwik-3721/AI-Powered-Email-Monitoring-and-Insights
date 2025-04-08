import json
import os
import re
from datetime import datetime

def sanitize_filename(filename):
    """Sanitizes the filename by removing invalid characters."""
    return re.sub(r'[<>:"/\\|?*\r\n]', '_', filename).strip()

def normalize_subject(subject):
    """Removes common reply/forward prefixes to group email threads."""
    return re.sub(r'^(Re|Fwd|FW):\s*', '', subject, flags=re.IGNORECASE).strip()

def extract_valid_json(response):
    """Extracts and parses valid JSON from the model response, handling markdown formatting and invalid escape characters."""
    try:
        match = re.search(r"```json\n(.*?)\n```", response, re.DOTALL)
        if match:
            response = match.group(1).strip()

        response = response.replace('\\n', ' ').replace('\\r', ' ').replace('\\t', ' ')
        response = response.encode('utf-8').decode('unicode_escape')

        return json.loads(response)

    except json.JSONDecodeError as e:
        print(f"❌ JSON Parsing Error: {e}")
        return None
    except UnicodeDecodeError as e:
        print(f"❌ Unicode Decode Error: {e}")
        return None

def store_emails_data(email_data_list):
    """Stores email threads into single files based on normalized subject."""
    if isinstance(email_data_list, dict):
        email_data_list = [email_data_list]

    if not isinstance(email_data_list, list):
        print(f"❌ Invalid email data format: {type(email_data_list)}")
        return

    output_folder = "parsed_emails"
    os.makedirs(output_folder, exist_ok=True)

    for idx, email_json in enumerate(email_data_list):
        try:
            if not isinstance(email_json, dict):
                raise TypeError(f"Invalid email entry at index {idx}: {type(email_json)}")

            subject = email_json.get("subject", f"No_Subject_{idx+1}")
            normalized_subject = normalize_subject(subject)
            sanitized_subject = sanitize_filename(normalized_subject)

            file_path = os.path.join(output_folder, f"{sanitized_subject}.txt")

            body_text = email_json.get("body", "").replace("\n", " ").replace("\r", " ")
            email_text = (
                f"To: {email_json.get('to', '')}\n"
                f"From: {email_json.get('from_', '') or email_json.get('from', '')}\n"
                f"CC: {email_json.get('cc', 'N/A')}\n"
                f"BCC: {email_json.get('bcc', 'N/A')}\n"
                f"Subject: {email_json.get('subject', '')}\n"
                f"Body:\n{body_text}\n"
                f"Tags: {email_json.get('tags', '')}\n"
                f"{'-' * 80}\n"
            )

            write_mode = "a" if os.path.exists(file_path) else "w"
            with open(file_path, write_mode, encoding="utf-8") as f:
                f.write(email_text)

            print(f"✅ Stored email in: {file_path}")
        except Exception as e:
            print(f"❌ Error storing email {idx+1}: {e}")