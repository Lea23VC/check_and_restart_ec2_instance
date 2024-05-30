import boto3
import requests
import os
from utils.email import send_email


def reboot_if_down(event, context):
    instance_ids = os.getenv("INSTANCE_IDS").split(',')
    region = os.getenv("AWS_REGION")

    # Create EC2 client
    ec2 = boto3.client('ec2', region_name=region)

    def check_ip(public_ip):
        print("Checking IP...")
        print(f"Public IP: {public_ip}")
        try:
            # Assuming the instance has a web server
            response = requests.get(f'http://{public_ip}', timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    for instance_id in instance_ids:
        # Get the public IP address of the instance
        instances = ec2.describe_instances(InstanceIds=[instance_id])
        public_ip = instances['Reservations'][0]['Instances'][0].get(
            'PublicIpAddress')

        if public_ip is None:
            print(f"No public IP found for instance {instance_id}")
            continue

        if not check_ip(public_ip):
            print(f"""Instance {instance_id} at IP {
                  public_ip} is not responding. Rebooting...""")
            ec2.reboot_instances(InstanceIds=[instance_id])

            # Send an email notification
            subject = f"Instance {instance_id} is down"
            message = f"""Instance {instance_id} at IP {
                public_ip} is not responding. Rebooting..."""
            send_email(subject, message)
        else:
            print(f"Instance {instance_id} at IP {public_ip} is responding.")

    return {'message': 'IP check complete'}
