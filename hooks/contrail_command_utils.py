import time
import os
import base64
from socket import inet_aton
import struct
import uuid

from distutils.dir_util import copy_tree
import shutil

from charmhelpers.core.hookenv import (
    config,
    log,
    status_set
)
from charmhelpers.core.templating import render

import common_utils
import docker_utils
from subprocess import (
    check_call,
    check_output
)


config = config()

MODULE = "command"
BASE_CONFIGS_PATH = "/etc/contrail"

CONFIGS_PATH = BASE_CONFIGS_PATH + "/contrail-command"
IMAGES = [
    "contrail-command-deployer"
]
SERVICES = {}


def get_context():
    ctx = {}
    ctx["module"] = MODULE
    ctx["log_level"] = config.get("log-level", "SYS_NOTICE")
    ctx["container_registry"] = config.get("docker-registry")
    ctx["container_tag"] = config.get("image-tag")

    ctx["command_ip"] = config.get("command-ip")
    ctx["vrouter_gateway"] = config.get("vrouter-gateway")
    ctx["contrail_container_tag"] = config.get("contrail-container-tag")
    ctx["install_docker"] = config.get("install-docker")

    log("CTX: {}".format(ctx))
    return ctx


def deploy_ccd_code(image, tag):
    docker_utils.pull(image, tag)
    docker_utils.remove_container_by_image(image)

    name = docker_utils.create(image, tag)
    try:
        src = '/' + image
        tmp_folder = os.path.join('/tmp', str(uuid.uuid4()))
        docker_utils.cp(name, src, tmp_folder)
        try:
            os.mkdir(tmp_folder + '/docker')
            os.mkdir('/etc/ansible')
        except Exception:
            pass

        docker_utils.cp(name, '/bin/deploy_contrail_command', tmp_folder + '/docker/')
        docker_utils.cp(name, '/etc/ansible/ansible.cfg', '/etc/ansible/') 

        dst='/' + image
        copy_tree(tmp_folder, dst)

        shutil.rmtree(tmp_folder, ignore_errors=True)
        check_call(['sed', '-i', 's/connection: ssh/connection: local/g', '/' + image + '/playbooks/roles/generate_configs/templates/command_servers.yml.j2'])
    finally:
        docker_utils.remove_container_by_image(image)


def update_charm_status():
    tag = config.get('image-tag')

    ctx = get_context()
    changed = common_utils.render_and_log("min_config.yaml",
        '/cluster_config.yml', ctx)
    if changed:
        for image in IMAGES:
            deploy_ccd_code(image, tag)

        dst='/' + image
        check_call('export HOME=/root; ' + dst + '/docker/deploy_contrail_command', shell=True)

def update_status():
    command_ip = config.get("command-ip")

    try:
        output = check_output("curl -k https://{}:8079 | grep '<title>'".format(command_ip), shell=True).decode('UTF-8')
    except Exception as e:
        return False
    if 'Contrail Command' not in output:
        status_set("waiting", "Cannot curl to " + command_ip + ":8079")
        return False

    status_set("active", "Unit is ready")
    return True

