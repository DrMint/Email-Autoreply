import imaplib
from email import message_from_bytes
from email.parser import HeaderParser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 5:45

# CONFIG

imapIp = "imap.server.com"
imapPort = 993
imapUser = "user@server.com"
imapPassword = "password"
checkEmailFrom = "INBOX"

smtpIp = "smtp.server.com"
smtpPort = 465
smtpUser = "user@server.com"
smtpPassword = "password"

replyTitle = "Subject of my auto-reply message"

# END CONFIG


def isToBeExcluded(sender, substringsBlacklist):
    for substring in substringsBlacklist:
        if substring in sender:
            return True
    return False

# Load blacklist
with open("blacklist.txt", "r") as file:
    substringsBlacklist = file.read().splitlines()

# Load html reply template
replyBody = ""
with open("template.html", "r", encoding="utf-8") as file:
    replyBody = file.read()

# Login to IMAP server
imap = imaplib.IMAP4_SSL(imapIp, imapPort)
imap.login(imapUser, imapPassword)
print("IMAP CONNECTED")

# Login to SMTP server
smtp = smtplib.SMTP_SSL(smtpIp, smtpPort)
smtp.login(smtpUser, smtpPassword)
print("SMTP CONNECTED")

# We select the folder to analyse
imap.select(checkEmailFrom)

# Get list of unseen mails
returnCode, data = imap.search(None, "UNSEEN")
mailIds = data[0].decode().split()

parser = HeaderParser()
for mailId in mailIds:
    result, header = imap.fetch(mailId, '(BODY[HEADER])')
    parsedHeader = parser.parsestr(str(message_from_bytes(header[0][1])))

    sender = parsedHeader["From"]
    receiver = parsedHeader["To"]

    if not isToBeExcluded(sender, substringsBlacklist):
        msg = MIMEMultipart('alternative')
        msg["Subject"] = replyTitle
        msg["From"] = receiver
        msg["To"] = sender
        part1 = MIMEText(replyBody, 'html')
        msg.attach(part1)
        smtp.send_message(msg)

        print("Email sent to", sender)
