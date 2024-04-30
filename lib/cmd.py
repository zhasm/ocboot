#!/usr/bin/env python3
# encoding: utf-8

import subprocess
import os

from lib import utils
from lib.utils import init_local_user_path


def init_ansible_playbook_path():
    if '/usr/local/bin' not in os.environ.get('PATH', '').split(':'):
        os.environ['PATH'] = '/usr/local/bin:' + os.environ.get('PATH', '')


def get_ansible_config_path():
    return os.path.join(os.getcwd(), 'onecloud/ansible.cfg')


def run_cmd(cmds, env=None, no_strip=False, realtime_output=False):
    shell_cmd = cmds
    if isinstance(cmds, list):
        shell_cmd = ' '.join(cmds)
    # logging.debug('run cmd `%s` with env %s' % (shell_cmd, env))
    print('run cmd: `%s`' % shell_cmd)
    if env is None:
        env = os.environ.copy()
    proc = subprocess.Popen(
        shell_cmd,
        shell=True,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
    )
    output = ''
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        if not no_strip:
            line = line.rstrip()
        if realtime_output:
            print(line, end='')
        else:
            print(line)
        output += line
    proc.wait()
    if proc.returncode != 0:
        print(output)
        raise Exception('cmd `%s` return %s' % (shell_cmd, proc.returncode))
    return output


def _run_cmd(cmds):
    shell_cmd = ' '.join(cmds)
    print(shell_cmd)
    os.environ['ANSIBLE_FORCE_COLOR'] = '1'
    config_file = get_ansible_config_path()
    if not os.path.exists(config_file):
        raise Exception("Not found file %s" % config_file)
    os.environ['ANSIBLE_CONFIG'] = get_ansible_config_path()
    init_ansible_playbook_path()
    proc = subprocess.Popen(
        shell_cmd,
        shell=True,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,)
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        print(line.rstrip())
    proc.wait()
    return proc.returncode


def run_ansible_playbook(hosts_f, playbook_f, debug_level=0, vars=None):
    """
    debug level support example:
    ANSIBLE_VERBOSITY=4 /opt/yunionboot/run.py /opt/yunion/upgrade/config.yml
    """

    init_local_user_path()

    debug_flag = ''
    if debug_level == 0:
        debug_level = int(os.environ.get('ANSIBLE_VERBOSITY', 0))
    if debug_level > 0:
        if debug_level > 0:
            debug_flag = '-' + 'v' * debug_level

    cmd = ["ansible-playbook"]

    if vars:
        vars_f = "/tmp/oc_vars.yml"
        with open(vars_f, 'w') as f:
            f.write(utils.to_yaml(vars))
        cmd.extend(["-e", "@%s" % vars_f])

    cmd.extend(["-i", hosts_f, playbook_f])

    if len(debug_flag) > 0:
        cmd.append(debug_flag)
    skip_tags = os.environ.get('SKIP_TAGS', "")
    if len(skip_tags) > 0:
        cmd.extend(["--skip-tags", f"'{skip_tags}'"])
    return _run_cmd(cmd)


def run_bash_cmd(cmd):
    import os
    os.system(cmd)


def ensure_pv():
    if not os.path.isfile('/usr/bin/pv'):
        run_bash_cmd('yum install -y pv >/dev/null')
