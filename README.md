Overview
--------

Contrail Command is #TODO

In a Canonical OpenStack environment the operator will deploy the Command UI to manage an existing OpenStack cluster. The operator will use a JuJu Charm to deploy the Command containers, and import the existing cluster.
Only for Contrail 5.0 for now.
Juju 2.0 is required.

Usage
-----

Once ready, deploy and relate as follows:

    juju deploy contrail-command
