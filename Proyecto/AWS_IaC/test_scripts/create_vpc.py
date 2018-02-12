from troposphere import Tags, Ref, Parameter
from troposphere.ec2 import VPC, Subnet, InternetGateway, VPCGatewayAttachment, RouteTable, Route, \
    SubnetRouteTableAssociation, NetworkAcl, NetworkAclEntry, SubnetNetworkAclAssociation, PortRange


def add_vpc_to_template(my_template, ref_stack_id):

    sshlocation_param = my_template.add_parameter(
    Parameter(
        'SSHLocation',
        Description=' The IP address range that can be used to SSH to the EC2 instances',
        Type='String',
        MinLength='9',
        MaxLength='18',
        Default='0.0.0.0/0',
        AllowedPattern="(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})/(\d{1,2})",
        ConstraintDescription=(
            "must be a valid IP CIDR range of the form x.x.x.x/x."),
    ))

    my_vpc = my_template.add_resource(
        VPC(
            'VPC',
            CidrBlock='10.0.0.0/16',
            Tags=Tags(
                Application=ref_stack_id)))

    subnet = my_template.add_resource(
        Subnet(
            'Subnet',
            CidrBlock='10.0.0.0/24',
            VpcId=Ref(VPC),
            Tags=Tags(
                Application=ref_stack_id)))

    internetGateway = my_template.add_resource(
        InternetGateway(
            'InternetGateway',
            Tags=Tags(
                Application=ref_stack_id)))

    gatewayAttachment = my_template.add_resource(
        VPCGatewayAttachment(
            'AttachGateway',
            VpcId=Ref(VPC),
            InternetGatewayId=Ref(internetGateway)))

    routeTable = my_template.add_resource(
        RouteTable(
            'RouteTable',
            VpcId=Ref(VPC),
            Tags=Tags(
                Application=ref_stack_id)))

    route = my_template.add_resource(
        Route(
            'Route',
            DependsOn='AttachGateway',
            GatewayId=Ref('InternetGateway'),
            DestinationCidrBlock='0.0.0.0/0',
            RouteTableId=Ref(routeTable),
        ))

    subnetRouteTableAssociation = my_template.add_resource(
        SubnetRouteTableAssociation(
            'SubnetRouteTableAssociation',
            SubnetId=Ref(subnet),
            RouteTableId=Ref(routeTable),
        ))

    networkAcl = my_template.add_resource(
        NetworkAcl(
            'NetworkAcl',
            VpcId=Ref(VPC),
            Tags=Tags(
                Application=ref_stack_id),
        ))

    inboundSSHNetworkAclEntry = my_template.add_resource(
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

    subnetNetworkAclAssociation = my_template.add_resource(
        SubnetNetworkAclAssociation(
            'SubnetNetworkAclAssociation',
            SubnetId=Ref(subnet),
            NetworkAclId=Ref(networkAcl),
        ))