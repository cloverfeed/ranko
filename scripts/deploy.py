"""
Usage:
    deploy.py [--branch=<branch>] [--to=<location>]

Options:
    --branch=<branch>  the branch to deploy [default: master]
    --to=<location>    where to deploy it   [default: prod]
"""

import docopt
import os
import subprocess


def main():
    arguments = docopt.docopt(__doc__)
    branch = arguments['--branch']
    where = arguments['--to']
    if where == 'test':
        os.putenv('ANSIBLE_HOST_KEY_CHECKING', 'no')
        cmd = ['ansible-playbook',
               '--private-key=~/.vagrant.d/insecure_private_key',
               '-u', 'vagrant',
               '-i', 'vagrant_ansible_inventory_default',
               '--skip-tags', 'provision',
               'devops/site.yml',
               '-e', 'repo_version={}'.format(branch),
               ]
        subprocess.check_call(cmd)
    elif where == 'prod':
        cmd = ['ansible-playbook',
               '-i', 'devops/hosts',
               '--skip-tags', 'provision',
               'devops/site.yml',
               ]
        subprocess.check_call(cmd)
    else:
        assert False, 'unknown destination: ' + where


if __name__ == '__main__':
    main()
