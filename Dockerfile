FROM python:2.7
ADD . /final
WORKDIR /final
#RUN https://github.com/ftalem/Ftu-sa.git
RUN pip install -r requirements.txt
