"""
Script file containing configuration parameters and auxiliary classes related to the Cloud Formation stack
"""
from troposphere import Parameter, Output, Ref


class StackState:
    """
    This class maps all possible stack states. When a stack is successfully created, the status is "CREATE_COMPLETE"
    """
    creating = "CREATE_IN_PROGRESS"
    created = "CREATE_COMPLETE"
    updating = "UPDATE_IN_PROGRESS"
    deleting = "DELETE_IN_PROGRESS"
    deleted = "DELETE_COMPLETE"


def ssh_parameter(key_name_value):
    """
    :param key_name_value: the name of the AWS key to SSH the resources
    :return: object describing the SSH key parameter
    """
    return Parameter(
        'KeyName',
        Type='String',
        Default=key_name_value,
        Description='Name of an existing EC2 KeyPair to enable SSH access'
    )


def cf_output(name, description, value):
    return Output(
            name,
            Description=description,
            Value=Ref(value)
    )

