FROM python:2

COPY requirements.txt ./
RUN pip install -r requirements.txt

ADD ./* ./

CMD [ "python", "aws_iam_accesskey_ageing.py" ]