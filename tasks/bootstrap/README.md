
Bootstrap directory
============

Ansible requires a number of dependencies to use its common modules. Many 
`minimal` server images can be missing necessary commands and libraries, 
depending how aggresive they were in culling packages to obtain a slim image. To 
avoid creating dependencies on a full-fat `"common"` role, this directory 
contains a minimal package set to run ansible, and facilites testing this role 
standalone.

## Usage
-----

The entry point for these tasks is as follows. 

```yaml
---
  - name: bootstrap enough packages that ansible can run most modules
    include_tasks: "bootstrap/main.yml"
    when: bootstrap_done is not defined
    tags: [ bootstrap ]
```

The main task sets a flag to prevent it being included many times over, when 
multiple roles with bootstrap are used.

```yaml
---
  - name: only run this bootstrap once
    set_fact:
      bootstrap_done: true
```
These tasks are sync'ed across the limepepper roles and its generally not a 
good idea to change these files unless you know what you are doing!

Checkout https://github.com/limepepper for other roles by limepepper

* https://github.com/limepepper/ansible-role-mysql

    > The [limepepper.mysql](https://github.com/limepepper/ansible-role-mysql) role provides a common base for apps requiring a mysql service  
    > 

* https://github.com/limepepper/ansible-role-syncusers

    > The [limepepper.syncusers](https://github.com/limepepper/ansible-role-syncusers)
    > role provides the base for deploying and managing users, keys, groups from
    > various backends. (It's a work in progress, being ported from chef)

* https://github.com/limepepper/ansible-role-raspberrypi

    > The [limepepper.raspberrypi](https://github.com/limepepper/ansible-role-raspberrypi)
    > role provides tasks for bootstrapping and creating a recovery partition
    > on (recent) raspberrypi raspbian installations.

* https://github.com/limepepper/ansible-role-wordpress
* https://github.com/limepepper/ansible-role-zabbix
* https://github.com/limepepper/ansible-role-apache




