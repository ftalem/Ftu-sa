FROM python:2.7
ADD . /final
WORKDIR /final
RUN pip install -r requirements.txt
