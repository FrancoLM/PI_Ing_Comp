import sys, traceback
import boto3
from botocore.exceptions import ClientError
from troposphere import Template, Tags
from troposphere import Base64, Join
import troposphere.ec2 as tp_ec2

def test():
    client = boto3.client('ec2')
    sg_template = Template()

    sg_name = 'SomeName'
    sg_group_name = 'MySecurityGroup3'
    sg_description = 'This is some information / explanation of the SG'

    try:
        my_sg = client.create_security_group(
            DryRun=False,
            # GroupName=sg_group_name,
            Description=sg_description
        )

        created_sec_group = boto3.resource('ec2').SecurityGroup(my_sg['GroupId'])

        print("Security Group created!")

    except ClientError as e:
        formatted_lines = traceback.format_exc().splitlines()
        print(formatted_lines[0])
        print(formatted_lines[-1])
        # I should handle the ClientError exceptions in a class or dict
        if e.response['Error']['Code'] == 'InvalidGroup.Duplicate':
            print("Security Group Already Exists")
        else:
            print("Unexpected error: %s" % e)


if __name__ == "__main__":
    test()