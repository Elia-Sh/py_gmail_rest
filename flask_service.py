'''

Start the API service via flask_service.py
0. in case that you want to install py dependencies in 'node_modules' manager,
    meaning in the same dir as the service py files,
    run:
        export PIPENV_VENV_IN_PROJECT="enabled"
1. load/install pipenv using:
    pipenv install
2. uncomment the like:
        if __name__ == '__main__':
            ....
    in the flask_service.py
   NOTE: this will start the service with adhok ssl context.
3. to start the service run:
    pipenv run python flask_service.py
4. run POST request from bash !with JSON content! -
    curl -ki  -H 'Content-Type: application/json' -d "@sample.json"  -X POST https://localhost:5000/gmailSender

using uwsgi - using virtual env -> pipenv:
    option a: run from the root dir -
        .venv/bin/uwsgi --http 127.0.0.1:5000 --module flask_service:app -H .venv/
Known issue -> pipenv and deployments,
    example for such article:
    https://chriswarrick.com/blog/2018/07/17/pipenv-promises-a-lot-delivers-very-little/

For the docker image I've used pip install -r <requirements file>

Start API using docker and gunicorn
0. build the docker image:
    docker build -t gmail_rest_api ./
1. start docker container -
    docker run -d -p 80:80 -e MODULE_NAME="flask_service" myimage
3. curl away -
    curl -ki -H 'Content-Type: application/json' -d "@sample.json" -X POST http://localhost:80/gmailSender

'''

from flask import Flask
from flask_restful import Resource, Api, reqparse

import gmail_sender

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
service = gmail_sender.service_account_login()


# endpoints must start with a leading slash
ENDPOINT_PATH = '/gmailSender'

# those are pnly post PARAMETERS
PARAM_NAMES = ['to', 'message_subject', 'message_text']
SENDER_MAIL_ADDRESS = 'elia.shreidler@gmail.com'

class MailSend(Resource):
    def get(self):
        ## TODO this should get a ??
        ## a threadID? a list of mails?
        return {'hello': 'world'}

    def post(self):
        '''

        get as input a json with Email fields,
        use Google API to send a mail via Gmail.

        :return:
            thread ID
        '''
        for argument in PARAM_NAMES:
            parser.add_argument(argument, type=str, required=True,)
        args = parser.parse_args()

        # unpack the values from the supplied arguments into create_message
        message_obj_base64url = gmail_sender.create_message(SENDER_MAIL_ADDRESS, *args.values())
        sent = gmail_sender.send_message(service, message_obj_base64url)

        if not sent:
            return {
                       'Error': 'Something went wrong, could not get threadId from google API'
                   }, 500
        else:
            return {
                        'args': args,
                        'messae base64': message_obj_base64url,
                        'sent': sent,

                    }, 201



# End point
api.add_resource(MailSend, ENDPOINT_PATH)

#When running with: uwsgi, the bellow must be commented out.
# if __name__ == '__main__':
#     app.run(debug=True, ssl_context='adhoc') #Generates Adhoc Certs
