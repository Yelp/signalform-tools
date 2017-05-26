# -*- coding: utf-8 -*-
import boto3
from contextlib import contextmanager
from contextlib import suppress
import os
import subprocess


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
            if "account" not in d:
                raise ValueError("Error: missing account value in {0}".format(tfvars))
    except FileNotFoundError:
        raise ValueError("Error: missing file {0}".format(tfvars))
    command = "git rev-parse --show-toplevel"
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error:
        raise ValueError("Error: can't execute bash command")
    output = output.decode("utf-8").strip()
    relative_dir = os.getcwd().replace(output, "")

    client = boto3.client('s3', 'us-east-1', aws_access_key_id=aws_key, aws_secret_access_key=aws_secret_key)
    transfer = boto3.s3.transfer.S3Transfer(client)
    # Download s3://bucket/key to filename
    try:
        transfer.download_file("".join(("tf-rs-", d["account"])), "/".join((relative_dir[1:], "terraform.tfstate")), tfstate)
        yield
    except OSError:
        print("Impossible downloading file")
    finally:
        with suppress(FileNotFoundError):
            os.remove(tfstate)
