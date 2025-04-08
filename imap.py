import os
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv

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
        # in the search we can modify it by changing it from ALL --> complete inbox, UNSEEN --> new/unread emails
        status, messages = mail.search(None, "UNSEEN")
        email_ids = messages[0].split()
        
        # empty list for storing all the emails
        emails = []
        
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
                    
                    emails.append({
                        "to": to_email,
                        "from": from_email,
                        "cc": cc_email,
                        "bcc": bcc_email,
                        "subject": subject,
                        "body": body
                    })
            # mark the email as unseen
            # mail.store(e_id, '-FLAGS', '\\Seen')
        
        # close the mail connection and logout
        mail.close()
        mail.logout()
        
        return emails
    except Exception as e:
        print(f"❌ Error fetching emails: {e}")
        return []

# example 
if __name__ == "__main__":
    emails = fetch_all_emails()
    print("length", len(emails))
    print("Email data", emails, "type of ", type(emails))
    for email_data in emails:
        print(f"📧 To: {email_data['to']}")
        print(f"📤 From: {email_data['from']}")
        print(f"📨 CC: {email_data['cc']}")
        print(f"📭 BCC: {email_data['bcc']}")
        print(f"📌 Subject: {email_data['subject']}")
        print(f"📝 Body: {email_data['body']}")
        print("--------------------------------------------------")