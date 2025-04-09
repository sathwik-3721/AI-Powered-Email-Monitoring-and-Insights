import os
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv
import re

def fetch_all_emails():
    # load env
    load_dotenv()

    # IMAP config
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    IMAP_HOST = os.getenv("IMAP_HOST")
    IMAP_PORT = int(os.getenv("IMAP_PORT", 993))

    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(EMAIL_USER, EMAIL_PASSWORD)
        mail.select("INBOX")
        
        # search for all emails(read and unread)
        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()
        
        # empty lists for storing emails and calls
        emails = []
        calls = []
        
        for e_id in email_ids:
            status, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Decode email headers
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    
                    from_email, encoding = decode_header(msg.get("From"))[0]
                    if isinstance(from_email, bytes):
                        from_email = from_email.decode(encoding if encoding else "utf-8")
                    
                    to_email, encoding = decode_header(msg.get("To"))[0]
                    if isinstance(to_email, bytes):
                        to_email = to_email.decode(encoding if encoding else "utf-8")
                    
                    cc_email = msg.get("Cc", "N/A")
                    bcc_email = msg.get("Bcc", "N/A")
                    
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            if "attachment" not in content_disposition:
                                try:
                                    body = part.get_payload(decode=True).decode()
                                    break
                                except:
                                    continue
                    else:
                        body = msg.get_payload(decode=True).decode()
                    
                    # Check if the email is a meeting invite or call
                    if "meeting" in subject.lower() or "call" in subject.lower() or "invite" in subject.lower():
                        # Extract call details
                        call_time = re.search(r"\b(\d{1,2}:\d{2}\s?(AM|PM)?)\b", body, re.IGNORECASE)
                        call_time = call_time.group(0) if call_time else "N/A"

                        meet_url = re.search(r"https?://[^\s]+", body)
                        meet_url = meet_url.group(0) if meet_url else "N/A"

                        attendees = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", body)
                        attendees = attendees if attendees else ["N/A"]

                        agenda = re.search(r"agenda[:\-]?\s*(.*)", body, re.IGNORECASE)
                        agenda = agenda.group(1).strip() if agenda else "N/A"

                        client_name = re.search(r"client[:\-]?\s*(.*)", body, re.IGNORECASE)
                        client_name = client_name.group(1).strip() if client_name else "N/A"

                        calls.append({
                            "from": from_email,
                            "attendees": attendees,
                            "client_name": client_name,
                            "call_time": call_time,
                            "agenda": agenda,
                            "meet_url": meet_url
                        })
                    else:
                        # Store as a regular email
                        emails.append({
                            "to": to_email,
                            "from": from_email,
                            "cc": cc_email,
                            "bcc": bcc_email,
                            "subject": subject,
                            "body": body
                        })
            # mark the email as unseen
            mail.store(e_id, '-FLAGS', '\\Seen')
        
        # close the mail connection and logout
        mail.close()
        mail.logout()
        
        return {"emails": emails, "calls": calls}
    except Exception as e:
        print(f"❌ Error fetching emails: {e}")
        return {"emails": [], "calls": []}

# example 
if __name__ == "__main__":
    data = fetch_all_emails()
    print("Emails:", len(data["emails"]))
    print("Calls:", len(data["calls"]))
    print("Email Data:", data["emails"])
    print("Call Data:", data["calls"])