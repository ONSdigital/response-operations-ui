#!/usr/bin/python
import argparse
import json
import re
import sys
import time
import uuid

import requests
from requests import HTTPError

from sdc.crypto.encrypter import encrypt
from sdc.crypto.key_store import KeyStore
from sdc.crypto.key_store import validate_required_keys

KEY_PURPOSE = "authentication"

eq_url_mapping = {
    "preprod": "https://eq.onsdigital.uk/flush",
    "prod": "https://eq.ons.gov.uk/flush"
}


def parse_args():
    parser = argparse.ArgumentParser(description="Flush partially completed responses from EQ. In order to run, a file"
                                                 "with eq keys must be in the same folder this script is run from.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("environment", help="Environment the flush is being run in. Must be either preprod or prod")
    parser.add_argument("eq_id", help="The eq id of the submission (usually the name, i.e., mbs")
    parser.add_argument("form_type", help="The formtype of the submission")
    parser.add_argument("collection_exercise_id", help="The uuid of the collection exercise")
    parser.add_argument("ru_ref", help="ru ref with checkletter (e.g. 12345678901A")
    parser.add_argument('--keys', dest='keys', help='Name of file with eq keys.', default='eq-keys.json')
    return parser.parse_args()


def generate_token(json_secret_keys, payload):
    """
    Generates the token by encrypting the payload with sdc-cryptography.
    """
    print("Generating token")
    keys = json.loads(json_secret_keys)
    validate_required_keys(keys, KEY_PURPOSE)
    key_store = KeyStore(keys)
    encrypted_data = encrypt(payload, key_store=key_store, key_purpose=KEY_PURPOSE)
    return encrypted_data


def call_flush_endpoint(eq_url, token):
    """
    Calls the flush endpoint with the token.
    """
    print("About to flush")
    print(f"eq url is: {eq_url}")
    response = requests.post(eq_url + f'?token={token}')
    try:
        print(f'Response status: {response.status_code}')
        response.raise_for_status()
        print("Flush succeeded")
    except HTTPError as e:
        print(e)
        print("Flush failed.  A 404 might indicate that the payload was correct, but EQ doesn't have a record of "
              "the submission")


def get_payload(eq_id, form_type, collection_exercise_id, ru_ref):
    """
    Generates the payload required by EQ that will be later encoded.  Note, this came from an integration test so
    there may be superfluous bits to it.
    """
    return {
        'jti': str(uuid.uuid4()),
        'iat': time.time(),
        'exp': time.time() + 1000,
        'eq_id': eq_id,
        'form_type': form_type,
        'collection_exercise_sid': collection_exercise_id,
        'ru_ref': ru_ref,
        'roles': ['flusher'],
    }


if __name__ == '__main__':
    args = parse_args()
    environment = args.environment
    eq_id = args.eq_id
    form_type = args.form_type
    collection_exercise_id = args.collection_exercise_id
    ru_ref = args.ru_ref
    key_file = args.keys

    try:
        eq_url = eq_url_mapping[environment]
    except KeyError:
        sys.exit(f"Environment [{environment}] isn't in the mapping, choose between preprod and prod")

    try:
        json_secret_keys = open(key_file).read()
    except FileNotFoundError as e:
        sys.exit(f"Must have a file named {key_file} in the same folder this script is run from")

    try:
        uuid.UUID(collection_exercise_id)
    except ValueError:
        sys.exit(f"The collection exercise id [{collection_exercise_id}] is not a real uuid")

    if not re.match('^[0-9]{11}[a-zA-Z]$', ru_ref):
        sys.exit(f"The ru ref [{ru_ref}] needs to be 11 digits and a letter")

    print("Beginning flushing")
    payload = get_payload(eq_id, form_type, collection_exercise_id, ru_ref)
    token = generate_token(json_secret_keys, payload)
    call_flush_endpoint(eq_url, token)
    print("Flushing complete")
