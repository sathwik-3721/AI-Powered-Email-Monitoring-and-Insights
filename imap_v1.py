from imap_tools import MailBox #type: ignore
from dotenv import load_dotenv
import os

load_dotenv()

with MailBox(os.getenv("IMAP_HOST")).login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD")) as mailbox:
    emails = []
    for msg in mailbox.fetch(mark_seen=False, reverse= True, bulk=True):
        to = msg.to
        from_ = msg.from_
        date = msg.date
        body = msg.text

        emails.append({
            "to": to,
            "from": from_,
            "date": date,
            "body": body
        })

        print("subject", msg.subject)
        print("date", msg.date)
        print("from", msg.from_)
        print("to", msg.to)
        print("cc", msg.cc)
        print("bcc", msg.bcc)
        print("body", msg.text)
        print("flags", msg.flags)
        print("--------------------------------------------------")
    print("Length emails", len(emails))