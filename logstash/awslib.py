__author__ = 'navat'

import boto.utils
import os

IS_NOT_EC2_PATH = os.path.expanduser('~/.adience/is_not_ec2')
METADATA_RED_RETRIES = 2
METADATA_REQ_TIMEOUT = 0.3


def get_ec2_metadata(metadata_req_timeout=None, metadata_red_retries=None):
    if metadata_req_timeout is None:
        metadata_req_timeout = METADATA_REQ_TIMEOUT
    if metadata_red_retries is None:
        metadata_red_retries = METADATA_RED_RETRIES

    import boto.utils
    if os.path.isfile(IS_NOT_EC2_PATH):
        return {}

    return boto.utils.get_instance_metadata(
        timeout=metadata_req_timeout, num_retries=metadata_red_retries)