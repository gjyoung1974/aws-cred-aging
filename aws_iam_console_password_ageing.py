import boto3
import datetime
from botocore.exceptions import ClientError
import csv
from time import sleep
from datetime import datetime
from datetime import timedelta
import dateutil.parser

email_from = 'someone@example.com'
email_to = 'someone@example.com'
email_cc = 'someone@example.com'

emaiL_subject = 'IAM console password aging report'

message_body = []


def lambda_handler(event, context):
    iam_client = boto3.client('iam')
    pass_max_days = 90

    # Request the credential report, download and parse the CSV.
    def get_credential_report(iam_client):
        resp1 = iam_client.generate_credential_report()
        if resp1['State'] == 'COMPLETE':
            try:
                response = iam_client.get_credential_report()
                credential_report = response['Content']
                reader = csv.DictReader(credential_report.splitlines())
                credential_report = []
                for row in reader:
                    credential_report.append(row)
                return credential_report
            except ClientError as e:
                print("Unknown error getting Report: " + e.message)
        else:
            sleep(2)
            return get_credential_report(iam_client)

    obj_credential_report = get_credential_report(iam_client)
    
    for row in obj_credential_report:
        if row['password_enabled'] != "true": continue  # Skip IAM Users without passwords, they are service accounts
        last_changed = dateutil.parser.parse(row['password_last_changed']);

        now = datetime.utcnow().replace(tzinfo=last_changed.tzinfo)
        diff = now - last_changed
        delta = timedelta(days=pass_max_days)

        if diff > delta:
            print row['user'] + ': Password has not been changed in {0} days'.format(diff.days)
            message_body.append(row['user'] + ': Password has not been changed in {0} days'.format(diff.days))

    ses = boto3.client('ses')

    ses_response = ses.send_email(
        Source=email_from,
        Destination={
            'ToAddresses': [
                email_to,
            ],
            'CcAddresses': [
                email_cc,
            ]
        },
        Message={
            'Subject': {
                'Data': emaiL_subject
            },
            'Body': {
                'Text': {
                    'Data': ''.join(map(str, message_body))
                }
            }
        }
    )

    return ses_response
