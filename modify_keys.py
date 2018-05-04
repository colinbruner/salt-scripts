#!/usr/bin/env python

""" The script is intended to be run as the user running 'salt-master' process 
    while on the salt-master host itself. We can optionally add/delete arbitrary 
    minion(s) from the keychain on the salt-master host. 

    We emit a JSON string with the results of the command. 

    Calling this script via the RunnersClient api, be sure to call gen_accept
    or delete functions directly. Provided a minion 'arg'.
    
    Some example curl commands can be viewed below.

    # Add a minion key to keychain
    curl -sSk https://localhost:8000/run \
        -H 'Accept: application/x-yaml' \
        -H 'Content-type: application/json' \
        -d '[{
            "client": "runner",
            "fun": "modify_keys.gen_accept",
            "arg": "test-minion",
            "token": "<eauth_token>"
        }]'

    # Delete a minion key from keychain
    curl -sSk https://localhost:8000/run \
        -H 'Accept: application/x-yaml' \
        -H 'Content-type: application/json' \
        -d '[{
            "client": "runner",
            "fun": "modify_keys.delete",
            "arg": "test-minion",
            "token": "<eauth_token>"
        }

    # Add Multiple minions to salt-keychain
    curl -sSk https://localhost:8000/run \
    -H 'Accept: application/x-yaml' \
    -H 'Content-type: application/json' \
    -d '[{
        "client": "runner",
        "fun": "modify_keys.gen_accept",
        "kwarg": {"minion" : ["test1-minion", "test2-minion"]},
        "token": "3f3ddb231904bd9d3ffb9d5df8e692cfbd653fd193a4d7e1a2629050026bdf4d"
    }]'

    # Delete Multiple minions from salt-keychain
    curl -sSk https://localhost:8000/run \
    -H 'Accept: application/x-yaml' \
    -H 'Content-type: application/json' \
    -d '[{
        "client": "runner",
        "fun": "modify_keys.delete",
        "kwarg": {"minion" : ["test1-minion", "test2-minion"]},
        "token": "3f3ddb231904bd9d3ffb9d5df8e692cfbd653fd193a4d7e1a2629050026bdf4d"
    }]'

    """

import json

import salt.config
import salt.wheel

opts = salt.config.master_config('/etc/salt/master')
wheel = salt.wheel.WheelClient(opts)

def gen_accept(minion=None):
    """ This will generate and autoaccept a new key for a specified minion or minions. 
        Will return a dictionary containing generated keys, priv/pub, OR an empty dictionary 
        if no key was generated. This happens when the key for supplied 'minion' already exists.
        
        :param minion: the name of the minion to generate a key for
        :type minion: string or list """

    res = {}
    if isinstance(minion, str):
        res = [wheel.cmd('key.gen_accept', [minion])]
    elif isinstance(minion, list):
        res = []
        for m in minion:
            res.append(wheel.cmd('key.gen_accept', [m]))
        
    print(json.dumps(res))

def delete(minion=None):
    """ This will generate and autoaccept a new key for a specified minion. Will return
        the a dictionary containing generated keys, an empty dictionary if no key was 
        generated. This happens when the key for supplied 'minion' already exists.
        
        :param minion: the name(s) of the minion to generate a key for
        :type minion: string or list """

    res = {}
    if isinstance(minion, str):
        res = [wheel.cmd_async({'fun': 'key.delete', 'match' : minion})]
    elif isinstance(minion, list):
        res = wheel.cmd_async({'fun': 'key.delete_dict', 'match' : { 'minions': minion } })

    print(json.dumps(res))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('-a', '--add', help='Generate keys and add provided minion to accepted keychain. ', nargs="*", required=False)
    parser.add_argument('-d', '--delete', help='Delete provided minion(s) from accepted keychain.', nargs="*", required=False)
    args = parser.parse_args()
    
    if args.add:
        if len(args.add) == 1:
            minion = args.target[0]
        elif len(args.add) > 1:
            minion = args.target

        gen_accept(minion=minion)


    if args.delete:
        if len(args.add) == 1:
            minion = args.target[0]
        elif len(args.add) > 1:
            minion = args.target

        delete(minion=minion)

    if not args.add and not args.delete:
        parser.print_help()
