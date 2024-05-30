import boto3
import os


def send_email(subject: str, message: str):
    from_email = os.getenv('FROM_EMAIL')
    to_emails = os.getenv('TO_EMAILS').split(',')
    ses = boto3.client('ses')
    response = ses.send_email(
        Source=from_email,
        Destination={
            'ToAddresses': to_emails
        },
        Message={
            'Subject': {
                'Data': subject
            },
            'Body': {
                'Text': {
                    'Data': message
                }
            }
        }
    )

    return response
