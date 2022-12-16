FROM python:3.10.9

WORKDIR /consumer

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT [ "python", "application.py" ]
