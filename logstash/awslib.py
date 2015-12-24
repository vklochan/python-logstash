__author__ = 'navat'

import boto.utils
import os

IS_NOT_EC2_PATH = os.path.expanduser('~/.adience/is_not_ec2')
METADATA_RED_RETRIES = 2
METADATA_REQ_TIMEOUT = 0.3


def get_ec2_metadata():
    import boto.utils
    if os.path.isfile(IS_NOT_EC2_PATH):
        return {}

    return boto.utils.get_instance_metadata(
        timeout=METADATA_REQ_TIMEOUT, num_retries=METADATA_RED_RETRIES)