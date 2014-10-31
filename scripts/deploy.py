"""
Usage:
    deploy.py [--provision] [--branch=<branch>] [--to=<location>]

Options:
    --branch=<branch>  the branch to deploy [default: master]
    --to=<location>    where to deploy it   [default: prod]
    --provision        run provision commands too
"""

import os
import subprocess

import docopt


def main():
    arguments = docopt.docopt(__doc__)
    provision = arguments['--provision']
    branch = arguments['--branch']
    where = arguments['--to']
    if provision:
        provision_args = []
    else:
        provision_args = ['--skip-tags', 'provision']
    if where == 'test':
        os.putenv('ANSIBLE_HOST_KEY_CHECKING', 'no')
        cmd = ['ansible-playbook',
               '--private-key=~/.vagrant.d/insecure_private_key',
               '-u', 'vagrant',
               '-i', 'vagrant_ansible_inventory_default',
               ]
        cmd += provision_args
        cmd += ['devops/site.yml',
                '-e', 'repo_version={}'.format(branch),
                ]
        subprocess.check_call(cmd)
    elif where == 'prod':
        cmd = ['ansible-playbook',
               '-i', 'devops/hosts',
               ]
        cmd += provision_args
        cmd += ['devops/site.yml',
                ]
        subprocess.check_call(cmd)
    else:
        assert False, 'unknown destination: ' + where


if __name__ == '__main__':
    main()
