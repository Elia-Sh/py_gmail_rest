from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# imports for message creation
from email.mime.text import MIMEText
import base64

# sending message imports
from apiclient import errors

# If modifying these scopes, delete the file credentials/token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send',
          ]


def service_account_login():
    creds = None
    # The file credentials/token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    ####
    # Note that credentials/credentials.json is the file that need to be imported from google API.
    if os.path.exists('credentials/token.pickle'):
        with open('credentials/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('credentials/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    ### this is the service,
    return service


def create_message(sender, to, subject, message_text):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    # TODO why encode and then to decode?
    encoded_base64 = base64.urlsafe_b64encode(message.as_bytes())
    raw = encoded_base64.decode()

    return {'raw': raw }


def send_message(service, message, user_id="me"):
    """Send an email message.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      message: Message to be sent.

    Returns:
      Sent Message.
    """
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def main():
    """
    Small service for interaction with gmail via google API
    """

    service = service_account_login()

    EMAIL_FROM = 'elia.shreidler@gmail.com'
    EMAIL_TO = 'hassonronnie@gmail.com'
    EMAIL_SUBJECT = 'Hello  from Tusik!'
    EMAIL_CONTENT = 'Hello, this is your tusik calling'

    message_obj_base64url = create_message(EMAIL_FROM, EMAIL_TO, EMAIL_SUBJECT, EMAIL_CONTENT)

    sent = send_message(service, message_obj_base64url)
    print(sent)


    # # Call the Gmail API
    # results = service.users().labels().list(userId='me').execute()
    # labels = results.get('labels', [])
    #
    # if not labels:
    #     print('No labels found.')
    # else:
    #     print('Labels:')
    #     for label in labels:
    #         print(label['name'])


# if __name__ == '__main__':
#     main()
