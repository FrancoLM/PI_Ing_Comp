from troposphere import ec2, Ref, Base64, Join, Tags
from configobj import ConfigObj
from troposphere.ec2 import NetworkInterfaceProperty


class EnvInstance(ec2.Instance):

    def __init__(self, instance_name):
        super().__init__(instance_name)
        # Does this concatenate tags? I should add them in case I need/have other tags
        self.Tags = Tags(Name=instance_name)

    def create_instance_template(self, ami_id, instance_size, private_ip, ssh_key_name, bootstrap_script_path, sec_group_name, subnet):
        self.ImageId = ami_id
        self.InstanceType = instance_size
        self.PrivateIpAddress = private_ip

        if ssh_key_name:
            self.KeyName = Ref(ssh_key_name)

        self.SubnetId = Ref(subnet)
        self.DependsOn='AttachGateway'

        # instance.UserData = base64.b64encode("""#!touch /tmp/heythere.txt""".encode("ascii")).decode('ascii')
        if bootstrap_script_path:
            with open(bootstrap_script_path, "r") as bootstrap:
                # Add logging to the script...
                self.UserData = Base64(Join('', bootstrap.readlines()))

    def set_bucket_access(self, role_name, profile_name, bucket_name):
        self.Metadata = {
            "AWS::CloudFormation::Authentication": {
                "S3AccessCreds": {
                    "type": "S3",
                    "roleName": {
                        "Ref": role_name
                    },
                    "buckets": [
                        "S3Download"
                    ]
                }
            }
        }
        self.IamInstanceProfile = Ref(profile_name)

    def add_dependency(self, dependency):
        self.DependsOn = dependency

    def add_to_security_group(self, security_group):
        try:
            self.SecurityGroupIds.append(Ref(security_group))
        except:
            self.SecurityGroupIds = [Ref(security_group)]
