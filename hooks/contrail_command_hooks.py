#!/usr/bin/env python3
import json
import sys
import yaml

from charmhelpers.core.hookenv import (
    Hooks,
    UnregisteredHookError,
    config,
    log,
    status_set,
)
from charmhelpers.contrib.charmsupport import nrpe

import contrail_command_utils as utils
import common_utils
import docker_utils


hooks = Hooks()
config = config()


@hooks.hook("install.real")
def install():
    status_set('maintenance', 'Installing...')

    docker_utils.install()
    utils.update_charm_status()



@hooks.hook("config-changed")
def config_changed():
    docker_utils.config_changed()
    utils.update_charm_status()


@hooks.hook("update-status")
def update_status():
    utils.update_charm_status()
    utils.update_status()


@hooks.hook("upgrade-charm")
def upgrade_charm():
    utils.update_charm_status()


def main():
    try:
        hooks.execute(sys.argv)
    except UnregisteredHookError as e:
        log("Unknown hook {} - skipping.".format(e))


if __name__ == "__main__":
    main()
