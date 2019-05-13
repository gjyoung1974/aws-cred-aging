import boto3
import datetime
import time

email_from = 'someone@example.com'
email_to = 'someone@example.com'
email_cc = 'someone@example.com'

emaiL_subject = 'IAM Access Key Aging Report'

message_body = []


def lambda_handler(event, context):
    client = boto3.client('iam')

    response = client.list_users()  # List all the users

    for user in response["Users"]:
        username = user['UserName']

        res = client.list_access_keys(UserName=username)  # for each user get the each access key
        for key in res['AccessKeyMetadata']:

            accesskeydate = key['CreateDate']  # format the dates
            accesskeydate = accesskeydate.strftime("%Y-%m-%d %H:%M:%S")
            currentdate = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            accesskeyd = time.mktime(datetime.datetime.strptime(accesskeydate, "%Y-%m-%d %H:%M:%S").timetuple())
            currentd = time.mktime(datetime.datetime.strptime(currentdate, "%Y-%m-%d %H:%M:%S").timetuple())
            active_days = (currentd - accesskeyd) / 60 / 60 / 24  # We get the data in seconds and convert it to days
            if active_days >= 90:
                if key['Status'] == 'Active':
                    message_body.append(
                        key['UserName'] + ', ' + key['AccessKeyId'] + ", " + str((int(round(active_days)))))

    ses = boto3.client('ses')

    response = ses.send_email(
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

    return response
