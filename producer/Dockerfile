FROM python:3.10.9

WORKDIR /producer

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT [ "python", "continuous_event_publication.py" ]
