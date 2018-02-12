import troposphere.iam as iam
from troposphere import Ref


def bucket_access_policy(policy_name, role_name, bucket_name):
    return iam.PolicyType(
        policy_name,
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
                    "Resource":"arn:aws:s3:::{0}/*".format(bucket_name)
                }
            ]
        },
        Roles=[Ref(role_name)]
    )


def allow_bucket_access_role(role_name):
    return iam.Role(
        role_name,
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


def instance_profile_bucket(profile_name, role_name):
    return iam.InstanceProfile(
        profile_name,
        Path="/",
        Roles=[Ref(role_name)]
    )
