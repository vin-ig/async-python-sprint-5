FROM python:3.10

RUN mkdir /sprint_5

WORKDIR /sprint_5
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x docker/*.sh