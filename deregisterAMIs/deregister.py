import boto3
import datetime

ec2_client = boto3.client('ec2')

def list_amis():
    response = ec2_client.describe_images(Owners=['self'])
    return response['Images']

def filter_amis(amis, days=90):
    filtered_amis = []
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
    for ami in amis:
        creation_date = datetime.datetime.strptime(ami['CreationDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
        if creation_date < cutoff_date:
            filtered_amis.append(ami['ImageId'])
    return filtered_amis

def deregister_amis(filtered_amis):
    for ami_id in filtered_amis:
        ec2_client.deregister_image(ImageId=ami_id)
amis = list_amis()
filtered_amis = filter_amis(amis)
deregister_amis(filtered_amis)
print(filtered_amis)
print(f"Deregistered {len(filtered_amis)} AMIs.")