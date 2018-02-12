import boto3
import time
import traceback
import troposphere.s3 as s3
import troposphere.iam as iam
import os

from awacs.aws import Statement, Allow, Principal
from awacs.s3 import GetObject
from awacs.sts import AssumeRole
from botocore.exceptions import ClientError
from troposphere import Ref, Template, Parameter, Tags, Output, cloudformation
from troposphere import Base64, Join
import troposphere.ec2 as ec2


# access_key = os.environ['AWS_ACCESS_KEY_ID']
# secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
from troposphere.ecs import Service
from troposphere.iam import Policy, InstanceProfile, PolicyType
from troposphere.waf import Action


class StackState:
    creating = "CREATE_IN_PROGRESS"
    created = "CREATE_COMPLETE"
    updating = "UPDATE_IN_PROGRESS"
    deleting = "DELETE_IN_PROGRESS"
    deleted = "DELETE_COMPLETE"


def test():
    print("this is a small test. It describes an instance using troposphere and then creates a Cloud Formation "
          "stack including it.")

    # Connect to EC2. Get a cloudformation client
    client = boto3.client('cloudformation')
    stack_name = "ExampleCF"

    # Credentials:
    # aws_credentials = boto3.session.botocore.session.get_session().get_credentials()
    # Get temporary credentials
    sec_client = boto3.client('sts')
    '''
    response = sec_client.get_session_token(
        DurationSeconds=900  # seconds
        # SerialNumber='string',
        # TokenCode='string'
    )
    '''

    cloudformation_template = Template()

    # Key Pair must exist
    keyname_param = cloudformation_template.add_parameter(Parameter(
        'KeyName',
        Type='String',
        Default='pepe',
        Description='Name of an existing EC2 KeyPair to enable SSH access'
    ))

    security_group = create_security_group('SecurityGroup')

    # bucket_name = 'tesis.project.files'
    # bucket = add_bucket(bucket_name)
    # policy = allow_access_bucket(bucket_name)

    # cloudformation_template.add_resource(policy)
    # cloudformation_template.add_resource(bucket)
    cloudformation_template.add_resource(security_group)

    cloudformation_template.add_resource(bucket_role())
    cloudformation_template.add_resource(bucket_policy())
    cloudformation_template.add_resource(instance_profile_bucket())

    instance1 = create_instance('ExampleInstance', '172.31.0.10', keyname_param)
    # instance2 = create_instance('ExampleInstance2', '172.31.0.11', keyname_param)

    instance1.SecurityGroups = [Ref(security_group)]

    # instance2.SecurityGroups = [Ref(security_group)]

    cloudformation_template.add_resource(instance1)
    # cloudformation_template.add_resource(instance2)

    cloudformation_template.add_output([
        Output(
            "InstanceId1",
            Description="InstanceId of the newly created EC2 instance",
            Value=Ref(instance1),
        )  # ,
        # Output(
        #    "InstanceId2",
        #    Description="InstanceId of the newly created EC2 instance",
        #    Value=Ref(instance2),
        #  )
    ])

    # Launch an instance (ID for the instance must be retrieved) (Security group?)
    try:
        client.create_stack(StackName=stack_name,
                            TemplateBody=cloudformation_template.to_json(),
                            Capabilities=['CAPABILITY_IAM'],
                            Parameters=[{'ParameterKey': 'KeyName', 'ParameterValue': 'LinuxKeySSH'}])

        # Wait until it's created -> improve with the other states
        while client.describe_stacks(StackName=stack_name)["Stacks"][0]["StackStatus"] != StackState.created:
            # Add timeout -> and delete stack
            print("Creating stack...")
            time.sleep(10)
    except ClientError:
        formatted_lines = traceback.format_exc().splitlines()
        print(traceback.format_exc())
        print(formatted_lines[0])
        print(formatted_lines[-1])
        print("Stack not created!")

    print("End test!")


def add_cfn_init():
    return cloudformation.Metadata(
        cloudformation.Init(
            cloudformation.InitConfigSets(
                ascending=['config'],
                descending=['config']
            ),
            config=cloudformation.InitConfig(
                commands={
                    'test': {
                        'command': 'echo "$CFNTEST" > text.txt',
                        'env': {
                            'CFNTEST': 'I come from config.'
                        },
                        'cwd': '~'
                    }
                }
            )
        )
    )


def create_security_group(sg_name):
    security_group = ec2.SecurityGroup(
        sg_name,
        GroupDescription='Allows SSH access from anywhere',
        SecurityGroupIngress=[
            ec2.SecurityGroupRule(
                IpProtocol='tcp',
                FromPort=22,
                ToPort=22,
                CidrIp='0.0.0.0/0'
            )
        ],
        SecurityGroupEgress=[],
        # VpcId=Ref(vpc_id),
        Tags=Tags(
            Name='ops.cfninit-sg')
        )
    return security_group


def create_instance(instance_key_name, private_ip, key_name, bootstrap_file=None):
    # Instance ID for an Amazon Linux AMI
    ami_id = 'ami-fb890097'
    # Instance size (t2.micro is the free-tier compatible size)
    instance_size = "t2.micro"

    instance = ec2.Instance(instance_key_name)
    instance.ImageId = ami_id
    instance.InstanceType = instance_size
    instance.PrivateIpAddress = private_ip

    instance.KeyName = Ref(key_name)

    # instance.UserData = base64.b64encode("""#!touch /tmp/heythere.txt""".encode("ascii")).decode('ascii')
    instance.UserData = Base64(Join('', ['#!/bin/bash\n',
                                         'touch /tmp/heythere.txt\n',
                                         'aws s3 cp s3://tesis.project.files/zookeeper.sh ~/ --region sa-east-1\n']))

    instance.IamInstanceProfile = Ref('InstanceProfile')
    instance.Metadata = {
        "AWS::CloudFormation::Authentication": {
            "S3AccessCreds": {
                "type": "S3",
                "roleName": {
                    "Ref": "InstanceRole"
                },
                "buckets": [
                    "S3Download"
                ]
            }
        }
    }
    # instance.DependsOn = ["InstanceRole", "InstanceProfile", "RolePolicies"]
    return instance


def add_bucket(bucket_name):
    # UNUSED
    return s3.Bucket(
        'WebsiteS3Bucket',
        BucketName=bucket_name
    )


def bucket_role():
    return iam.Role(
        'InstanceRole',
        AssumeRolePolicyDocument={
           "Statement": [
              {
                 "Effect": "Allow",
                 "Principal": {
                    "Service": [
                       "ec2.amazonaws.com"
                    ]
                 },
                 "Action":[
                    "sts:AssumeRole"
                 ]
              }
           ]
        },
        Path="/"
    )

def bucket_role2():
    return iam.Role(
        'InstanceRole',
        AssumeRolePolicyDocument=
        Statement(
            Effect="Allow",
            Principal={
                "Service": [
                    "ec2.amazonaws.com"
                ]
            },
            Action=Action(
                sts="AssumeRole"
            )
        )
    )

def bucket_policy():
    return PolicyType(
        'RolePolicies',
        PolicyName="S3Download",
        # PolicyDocument=awacs.aws.Policy(
        PolicyDocument={
            "Statement": [
                {
                    "Action": [
                        "s3:GetObject",
                        "kms:decrypt"
                    ],
                    "Effect": "Allow",
                    "Resource":"arn:aws:s3:::tesis.project.files/*"
                }
            ]
        },
        Roles=[Ref('InstanceRole')]
    )


def bucket_policy2():
    return PolicyType(
        'RolePolicies',
        PolicyName="S3Download",
        # PolicyDocument=awacs.aws.Policy(
        PolicyDocument={
            Statement(
                Action=Action(
                    s3="GetObject"
                ),
                Effect="Allow",
                Resource="arn:aws:s3:::tesis.project.files/*"
            )
        },
        Roles=[Ref('InstanceRole')]
    )


def instance_profile_bucket():
    return InstanceProfile(
        "InstanceProfile",
        Path="/",
        Roles=[Ref('InstanceRole')]
    )


# {"Fn::Join": ["", ["arn:aws:s3:::", { "Ref" : "tesis.project.files"}, "/*"]]}
def allow_access_bucket(bucket_name):
    # UNUSED
    return s3.BucketPolicy(
        'S3BucketPolicy',
        Bucket=Ref(bucket_name),
        PolicyDocument={
          "Version": "2016-05-21",
          "Statement": [
            {
              "Effect": "Allow",
              "Action": [
                "s3:GetBucketLocation",
                "s3:ListAllMyBuckets"
              ],
              "Resource": {"Fn::Join": ["", ["arn:aws:s3:::", "/tesis.project.files"]]}
            },
            {
              "Effect": "Allow",
              "Action": ["s3:ListBucket"],
              "Resource":{"Fn::Join": ["", ["arn:aws:s3:::", {"Ref": "tesis.project.files"}]]}
            },
            {
              "Effect": "Allow",
              "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject"
              ],
              "Resource": {"Fn::Join": ["", ["arn:aws:s3:::", {"Ref": "tesis.project.files"}, "/zookeeper.sh"]]}
            }
          ]
        }
    )

if __name__ == "__main__":
    test()
