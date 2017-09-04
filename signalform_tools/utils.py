# -*- coding: utf-8 -*-
import boto3
from contextlib import contextmanager
import os
import subprocess

DEFAULT_REGION = "us-east-1"


@contextmanager
def download_tfstate():
    tfstate = "/".join((os.getcwd(), "terraform.tfstate"))
    tfvars = "/".join((os.getcwd(), "terraform.tfvars"))
    if os.path.isfile(tfstate):
        raise ValueError("Error: {0} already exists".format(tfstate))
    aws_key = os.getenv('AWS_ACCESS_KEY_ID', None)
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY', None)
    if aws_key is None or aws_secret_key is None:
        raise ValueError("Error: missing keys")
    try:
        with open(tfvars, 'r') as tfvar_file:
            splitstrs = (line.split("=") for line in tfvar_file)
            d = {key.strip(): value.strip().replace('"', '') for key, value in splitstrs}
    except FileNotFoundError:
        raise ValueError("Error: missing file {0}".format(tfvars))

    s3_path = {"bucket": d["s3_bucket"], "key": d["s3_key"]} if d.keys() & {'s3_bucket', 's3_key'} else extract_s3_path(d)

    if not s3_path:
        raise ValueError("Error: missing s3 path information {0}".format(tfvars))
    client = boto3.client('s3', d.get("s3_bucket_region", DEFAULT_REGION), aws_access_key_id=aws_key, aws_secret_access_key=aws_secret_key)
    transfer = boto3.s3.transfer.S3Transfer(client)
    # Download s3://bucket/key to filename
    try:
        transfer.download_file(s3_path["bucket"], s3_path["key"], "terraform.tfstate")), tfstate)
        yield
    except OSError:
        print("Impossible downloading file")
    else:
        os.remove(tfstate)


def extract_s3_path(d):
    if "account" not in d:
        return None
    command = "git rev-parse --show-toplevel"
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error:
        raise ValueError("Error: can't execute bash command")
    output = output.decode("utf-8").strip()
    relative_dir = os.getcwd().replace(output, "")
    return {"bucket": "".join(("tf-rs-", d["account"])), "key": "/".join((relative_dir[1:], "terraform.tfstate"))}
