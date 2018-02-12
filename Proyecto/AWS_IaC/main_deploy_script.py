"""
This is the main script. Running this script will create a Cloud-Formation stack in Amazon
A Cloud Formation stack is created by using a Json template. This template contains parameters and resources that
define and configure the system.
"""
import argparse
import os
import boto3
import traceback
import time

from botocore.exceptions import ClientError
from configobj import ConfigObj
from troposphere import Template, Ref
from access_policy_helpers import bucket_access_policy, allow_bucket_access_role, instance_profile_bucket
from cloudformation_settings import add_ssh_security_group, set_cloudformation_settings
from stack_helpers import StackState, ssh_parameter, cf_output
from environment_instance import EnvInstance

CFG_FILE = os.path.join(os.getcwd(), "instances_info.cfg")
BOOTSTRAP_FOLDER = 'configuration_files'


def create_cloudformation_stack(args):
    print("Hello AWS!")

    # Connect to EC2. Get a cloudformation client
    session = boto3.Session(profile_name='f_project')
    client = session.client('cloudformation', region_name='sa-east-1')
    stack_name = args.stack_name
    ssh_key = args.ssh_key_name
    sec_group_name = 'TesisSecurityGroup'

    # Create stack template.
    cloudformation_template = Template()

    # Add parameters -> SSH key
    ssh_key_parameter = cloudformation_template.add_parameter(ssh_parameter(ssh_key))
    cloudformation_template.add_output(cf_output("SSHKey", "SSH Key to log into instances", 'KeyName'))

    # Add roles and policies (bucket)
    policy_name = 'RolePolicies'
    role_name = 'InstanceRole'
    profile_name = 'InstanceProfile'

    ref_stack_id = Ref('AWS::StackId')
    ref_region = Ref('AWS::Region')
    ref_stack_name = Ref('AWS::StackName')

    cloudformation_template, subnet = set_cloudformation_settings(cloudformation_template, ref_stack_id)

    # Add security group
    ssh_sec_group = add_ssh_security_group(sec_group_name)
    cloudformation_template.add_resource(ssh_sec_group)

    # Read the environment information from the config file
    cfg_parser = ConfigObj(CFG_FILE)

    instance_size = cfg_parser['aws_config']['INSTANCE_SIZE']
    bucket_name = cfg_parser['aws_config']['BUCKET']

    # Add bucket access policies
    cloudformation_template.add_resource(allow_bucket_access_role(role_name))  # 1
    cloudformation_template.add_resource(bucket_access_policy(policy_name, role_name, bucket_name))  # 2
    cloudformation_template.add_resource(instance_profile_bucket(profile_name, role_name))  # 3

    for instance_id in cfg_parser["Instances"]:

        instance = cfg_parser["Instances"][instance_id]
        name = instance['name']
        print("Instance name:", name)
        ami_id = instance['ami_id']
        ip = instance['ip']
        bootstrap_file = instance['local_bootstrap_file']
        bootstrap_path = os.path.join(os.getcwd(), BOOTSTRAP_FOLDER, name, bootstrap_file)

        aws_instance = EnvInstance(name)
        aws_instance.create_instance_template(ami_id,
                                              instance_size,
                                              ip, ssh_key_parameter,
                                              bootstrap_path,
                                              sec_group_name, # TODO: unused
                                              subnet)
        aws_instance.set_bucket_access(role_name, profile_name, bucket_name)
        aws_instance.add_to_security_group(ssh_sec_group)
        # aws_instance.add_to_security_group(ref_stack_id)

        cloudformation_template.add_resource(aws_instance)
        cloudformation_template.add_output(cf_output("%sInstance" % name, "%s: IP %s" % (name, ip), name))

        print("Instance added to template!")

    try:
        # Create stack
        client.create_stack(StackName=stack_name, TemplateBody=cloudformation_template.to_json(), Capabilities=['CAPABILITY_IAM'])

        # Wait until stack is created
        while client.describe_stacks(StackName=stack_name)["Stacks"][0]["StackStatus"] != StackState.created:
            # Add timeout -> and delete stack
            print("Creating Environment...")
            time.sleep(15)
        else:
            print("CloudFormation Stack created")
    except ClientError:
        formatted_lines = traceback.format_exc().splitlines()
        print(traceback.format_exc())
        print(formatted_lines[0])
        print(formatted_lines[-1])
        print("CloudFormation Stack could not be created!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script that creates a Cloud Formation stack on AWS')
    parser.add_argument('--stack_name', type=str, help='Stack Name', required=True)
    parser.add_argument('--ssh_key_name', metavar='KeyName', type=str, nargs='?',
                        help='Key Name used to SSH to instances (authentication)', default='LinuxKeySSH')

    args = parser.parse_args()
    create_cloudformation_stack(args)
