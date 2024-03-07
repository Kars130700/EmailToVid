import imaplib
import email
from email.header import decode_header
import webbrowser
import os
import re
import html2text

def login():
    # account credentials
    username = "in2carepython@outlook.com"
    password = "Hoihoi123"
    imapport = 993
    # use your email provider's IMAP server, you can look for your provider's IMAP server on Google
    # or check this page: https://www.systoolsgroup.com/imap/
    # for office 365, it's this:
    imap_server = "outlook.office365.com"
    imap = imaplib.IMAP4_SSL(imap_server, imapport)
    # authenticate
    imap.login(username, password)
    return imap



def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

def ReadEmail(messages, no_of_messages, imap):
    EmailInfoList = []
    for i in range(messages, messages-no_of_messages, -1):
        # fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)
                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    From = From.decode(encoding)
                # if the email message is multipart
                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        # get the email body
                        try:
                            body = part.get_payload(decode=True).decode()
                            text = html_to_plain_text(body)
                            CompInf = ReadCompanyInfo(text)
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            print()
                            # print(body)
                        elif "attachment" in content_disposition:
                            # download attachment
                            filename = part.get_filename()
                            if filename:
                                folder_name = CompInf['company_name']
                                if not os.path.isdir(folder_name):
                                    # make a folder for this email (named after the subject)
                                    os.mkdir(folder_name)
                                filepath = os.path.join(folder_name, filename)
                                CompInf['logo_path'] = filepath
                                # download attachment and save it
                                if not os.path.exists(filepath):
                                    with open(filepath, "wb") as f:
                                        f.write(part.get_payload(decode=True))
                        
                                
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        # print only text email parts
                        print(body)
                if content_type == "text/html":
                    # if it's HTML, create a new HTML file and open it in browser
                    folder_name = clean(subject)
                    if not os.path.isdir(folder_name):
                        # make a folder for this email (named after the subject)
                        os.mkdir(folder_name)
                    filename = "index.html"
                    filepath = os.path.join(folder_name, filename)
                    # write the file
                    open(filepath, "w").write(body)
                    # open in the default browser
                    webbrowser.open(filepath)
                print("="*100)
        print(f"{CompInf['company_name']} is done")
        EmailInfoList.append(CompInf)
    return EmailInfoList


def html_to_plain_text(html_content):
    # Create an HTML to text converter
    converter = html2text.HTML2Text()
    # Convert HTML to plain text
    plain_text = converter.handle(html_content)
    return plain_text

def ReadCompanyInfo(text):
    # Define regular expressions to match the desired patterns
    name_pattern = r'Company name \(in video\) \| (.+)'
    email_pattern = r"e-mail\s+\|\s+([\w.-]+@[\w.-]+)"
    company_email_pattern = r"Company e-mail \(in video\)\s+\|\s+([\w.-]+@[\w.-]+)"
    website_pattern = r"Website/URL \(in video\)\s+\|\s+(https?://\S+)"
    phone_pattern = r'Company Phone \(in video\) \| (.+)'
    address_pattern = r'Address \(in video\) \| (.*)(?=\nVideo)'
    video_pattern = r"Video (\d+):"
    print(text)
    # Find matches using regular expressions
    name_match = re.search(name_pattern, text)
    email_match = re.search(email_pattern, text)
    company_email_match = re.search(company_email_pattern, text)
    website_match = re.search(website_pattern, text)
    phone_match = re.search(phone_pattern, text)
    address_match = re.search(address_pattern, text, re.DOTALL)
    # Find all matches for video selections
    video_matches = re.findall(video_pattern, text)

    # Initialize CompanyInfo dictionary
    CompanyInfo = {}

    # Populate CompanyInfo dictionary with extracted information
    if name_match:
        CompanyInfo['company_name'] = name_match.group(1).strip()
    if email_match:
        CompanyInfo['email'] = email_match.group(1)
    if company_email_match:
        CompanyInfo['company_email'] = company_email_match.group(1)
    if website_match:
        CompanyInfo['website'] = website_match.group(1)
    if phone_match:
        CompanyInfo['company_phone'] = phone_match.group(1).strip()
    if address_match:
        CompanyInfo['address'] = address_match.group(1)
        CompanyInfo['address']= extract_address_lines(CompanyInfo['address'])

    CompanyInfo['selected_videos'] = list(set(map(int, video_matches)))
    # Print the CompanyInfo dictionary
    return CompanyInfo

def extract_address_lines(address_text):
    # Split the address into lines
    address_lines = address_text.split('\n')
    
    # Remove leading and trailing whitespaces from each line
    address_lines = [line.strip() for line in address_lines]
    
    # Remove empty lines
    address_lines = list(filter(None, address_lines))
    
    return address_lines

def main():
    imap = login()
    status, messages = imap.select("INBOX")

    # number of top emails to fetch
    if DebugYN():
        no_of_messages = 1
    else:
        no_of_messages = int(messages[0])
    # total number of emails
    messages = int(messages[0])
    print(messages)
    CompanyInfo = ReadEmail(messages, no_of_messages, imap)
    #CompanyInfo = ReadCompanyInfo(text)
    # close the connection and logout
    imap.close()
    imap.logout()
    return CompanyInfo

def DebugYN():
    user_input = input("Are you debugging? If so, I will only make the first video (Y/N): ").lower()
    if user_input == "y":
        print("Continuing...")
        return True
    else:
        print("Continuing...")
        return False