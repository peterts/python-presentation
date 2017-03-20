
from oauth2client import tools, client, file
from oauth2client.clientsecrets import InvalidClientSecretsError
import argparse
from httplib2 import Http
from apiclient import discovery
from email.mime.text import MIMEText
import base64
import os

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
PATH_CLIENT_SECRETS = os.path.join(DIR_PATH, "resources", "client_secrets.json")
PATH_CREDENTIALS = os.path.join(DIR_PATH, "resources", "gmail-credentials.json")
SCOPES = "https://www.googleapis.com/auth/gmail.compose"


def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    encoded_message = str(base64.urlsafe_b64encode(bytes(message.as_string(), "utf8")), 'utf-8')
    return {'raw': encoded_message}


def get_credentials():
    store = file.Storage(PATH_CREDENTIALS)
    credentials = store.get()
    if not credentials or credentials.invalid:
        try:
            flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
            flow = client.flow_from_clientsecrets(PATH_CLIENT_SECRETS, SCOPES)
            credentials = tools.run_flow(flow, store, flags)
        except InvalidClientSecretsError:
            return None
    return credentials


def init_service():
    credentials = get_credentials()
    if credentials:
        http = credentials.authorize(Http())
        return discovery.build('gmail', 'v1', http=http)
    return None


def send_message(service, message):
    if service:
        (service.users().messages().send(userId="me", body=message)).execute()


service = init_service()
message = create_message("peter.sandberg@visma.com", "petthosan@gmail.com", "Test", "Hello")
send_message(service, message)