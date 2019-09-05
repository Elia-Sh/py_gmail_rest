FROM tiangolo/meinheld-gunicorn:python3.7

COPY ./* /app/
COPY ./credentials/* /app/credentials/


RUN pip install -r py_requirements.txt

EXPOSE 80
ENV MODULE_NAME="flask_service"
