import troposphere.ec2 as ec2
from troposphere import Tags, Ref
from troposphere.ec2 import Subnet, InternetGateway, RouteTable, Route, SubnetRouteTableAssociation, \
    VPCGatewayAttachment, NetworkAcl, PortRange, SubnetNetworkAclAssociation, VPC, NetworkAclEntry


def add_ssh_security_group(sg_name):
    """This function creates a security group, where instances will be created.
    NOTE: The ports opened are for debugging. Consider disabling it after infrastructure is complete
    NOTE: Instances have public IP. Disable it after infrastructure is complete
    :param sg_name: Name for the Security Group
    :return:
    """
    security_group = ec2.SecurityGroup(
        sg_name,
        GroupDescription='Allow components to communicate and instance access anywhere',
        SecurityGroupIngress=[
            # SSH
            ec2.SecurityGroupRule(
                IpProtocol='tcp',
                FromPort=22,
                ToPort=22,
                CidrIp='0.0.0.0/0'
            ),
            # supervisord
            ec2.SecurityGroupRule(
                IpProtocol='tcp',
                FromPort=9001,
                ToPort=9001,
                CidrIp='0.0.0.0/0'
            ),
            # storm thrift (download topologies)
            ec2.SecurityGroupRule(
                IpProtocol='tcp',
                FromPort=6627,
                ToPort=6627,
                CidrIp='0.0.0.0/0'
            ),
            # PING
            ec2.SecurityGroupRule(
                IpProtocol='icmp',
                FromPort=-1,
                ToPort=-1,
                CidrIp='0.0.0.0/0'
            ),
            # Storm UI
            ec2.SecurityGroupRule(
                IpProtocol='tcp',
                FromPort=8080,
                ToPort=8080,
                CidrIp='0.0.0.0/0'
            ),
            # Zookeeper listen port
            ec2.SecurityGroupRule(
                IpProtocol='tcp',
                FromPort=2181,
                ToPort=2181,
                CidrIp='0.0.0.0/0'
            ),
            # RabbitMQ Management Console
            ec2.SecurityGroupRule(
                IpProtocol='tcp',
                FromPort=15672,
                ToPort=15672,
                CidrIp='0.0.0.0/0'
            ),
            # RabbitMQ AMQP port to accept connections
            ec2.SecurityGroupRule(
                IpProtocol='tcp',
                FromPort=5672,
                ToPort=5672,
                CidrIp='0.0.0.0/0'
            ),
            # Port to send responses to RabbitMQ
            ec2.SecurityGroupRule(
                IpProtocol='tcp',
                FromPort=6700,
                ToPort=6700,
                CidrIp='0.0.0.0/0'
            ),
            # RabbitMQ MQTT
            ec2.SecurityGroupRule(
                IpProtocol='tcp',
                FromPort=1883,
                ToPort=1883,
                CidrIp='0.0.0.0/0'
            )
        ],
        VpcId=Ref("VPC"),
        SecurityGroupEgress=[],
        Tags=Tags(
            Name='f-project-sg')
    )
    return security_group


def set_cloudformation_settings(cloudformation_template, ref_stack_id):
    my_VPC = cloudformation_template.add_resource(
        VPC(
            'VPC',
            CidrBlock='172.31.0.0/16',
            Tags=Tags(
                Application=ref_stack_id)))

    subnet = cloudformation_template.add_resource(
        Subnet(
            'Subnet',
            CidrBlock='172.31.0.0/22',
            VpcId=Ref(my_VPC),
            MapPublicIpOnLaunch=True,
            Tags=Tags(
                Application=ref_stack_id)))

    internetGateway = cloudformation_template.add_resource(
        InternetGateway(
            'InternetGateway',
            Tags=Tags(
                Application=ref_stack_id)))

    gatewayAttachment = cloudformation_template.add_resource(
        VPCGatewayAttachment(
            'AttachGateway',
            VpcId=Ref(my_VPC),
            InternetGatewayId=Ref(internetGateway)))

    routeTable = cloudformation_template.add_resource(
        RouteTable(
            'RouteTable',
            VpcId=Ref(my_VPC),
            Tags=Tags(
                Application=ref_stack_id)))

    route = cloudformation_template.add_resource(
        Route(
            'Route',
            DependsOn='AttachGateway',
            GatewayId=Ref('InternetGateway'),
            DestinationCidrBlock='0.0.0.0/0',
            RouteTableId=Ref(routeTable),
        ))

    subnetRouteTableAssociation = cloudformation_template.add_resource(
        SubnetRouteTableAssociation(
            'SubnetRouteTableAssociation',
            SubnetId=Ref(subnet),
            RouteTableId=Ref(routeTable),
        ))

    networkAcl = cloudformation_template.add_resource(
        NetworkAcl(
            'NetworkAcl',
            VpcId=Ref(my_VPC),
            Tags=Tags(
                Application=ref_stack_id),
        ))

    inBoundPrivateNetworkAclEntry = cloudformation_template.add_resource(
        NetworkAclEntry(
            'InboundHTTPNetworkAclEntry',
            NetworkAclId=Ref(networkAcl),
            RuleNumber='100',
            Protocol='6',
            PortRange=PortRange(To='80', From='80'),
            Egress='false',
            RuleAction='allow',
            CidrBlock='0.0.0.0/0',
        ))

    inboundSSHNetworkAclEntry = cloudformation_template.add_resource(
        NetworkAclEntry(
            'InboundSSHNetworkAclEntry',
            NetworkAclId=Ref(networkAcl),
            RuleNumber='101',
            Protocol='6',
            PortRange=PortRange(To='22', From='22'),
            Egress='false',
            RuleAction='allow',
            CidrBlock='0.0.0.0/0',
        ))

    inboundResponsePortsNetworkAclEntry = cloudformation_template.add_resource(
        NetworkAclEntry(
            'InboundResponsePortsNetworkAclEntry',
            NetworkAclId=Ref(networkAcl),
            RuleNumber='102',
            Protocol='6',
            PortRange=PortRange(To='65535', From='1024'),
            Egress='false',
            RuleAction='allow',
            CidrBlock='0.0.0.0/0',
        ))

    outBoundHTTPNetworkAclEntry = cloudformation_template.add_resource(
        NetworkAclEntry(
            'OutBoundHTTPNetworkAclEntry',
            NetworkAclId=Ref(networkAcl),
            RuleNumber='100',
            Protocol='6',
            PortRange=PortRange(To='80', From='80'),
            Egress='true',
            RuleAction='allow',
            CidrBlock='0.0.0.0/0',
        ))

    outBoundHTTPSNetworkAclEntry = cloudformation_template.add_resource(
        NetworkAclEntry(
            'OutBoundHTTPSNetworkAclEntry',
            NetworkAclId=Ref(networkAcl),
            RuleNumber='101',
            Protocol='6',
            PortRange=PortRange(To='443', From='443'),
            Egress='true',
            RuleAction='allow',
            CidrBlock='0.0.0.0/0',
        ))

    outBoundResponsePortsNetworkAclEntry = cloudformation_template.add_resource(
        NetworkAclEntry(
            'OutBoundResponsePortsNetworkAclEntry',
            NetworkAclId=Ref(networkAcl),
            RuleNumber='102',
            Protocol='6',
            PortRange=PortRange(To='65535', From='1024'),
            Egress='true',
            RuleAction='allow',
            CidrBlock='0.0.0.0/0',
        ))

    subnetNetworkAclAssociation = cloudformation_template.add_resource(
        SubnetNetworkAclAssociation(
            'SubnetNetworkAclAssociation',
            SubnetId=Ref(subnet),
            NetworkAclId=Ref(networkAcl),
        ))

    return cloudformation_template, subnet
