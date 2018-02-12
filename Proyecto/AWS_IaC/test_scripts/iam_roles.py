from awacs.s3 import GetObject
from troposphere import Template, Ref

from troposphere.iam import Role, InstanceProfile
from troposphere.iam import Policy as TPolicy

from awacs.aws import Allow, Statement, Principal, Policy
from awacs.sts import AssumeRole

t = Template()

t.add_description("AWS CloudFormation Sample Template: This template "
                  "demonstrates the creation of IAM Roles and "
                  "InstanceProfiles.")

'''
cfnrole = t.add_resource(Role(
    "CFNRole",
    AssumeRolePolicyDocument=Policy(
        Statement=[
            Statement(
                Effect=Allow,
                Action=[AssumeRole],
                Principal=Principal("Service", ["ec2.amazonaws.com"])
            )
        ]
    ),
    Path="/",
    Policies=Policy(
        "S3Download",
        PolicyDocument=Statement(
            Effect=Allow,
            Action=
        )
    )
))
'''
'''
cfninstanceprofile = t.add_resource(InstanceProfile(
    "InstanceRole",
    Roles=[Ref(cfnrole)],
    Path="/"
))
'''

print(t.to_json())