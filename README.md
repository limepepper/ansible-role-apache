
Devel branch: [![Build Status](https://travis-ci.org/limepepper/ansible-role-apache.svg?branch=devel)](https://travis-ci.org/limepepper/ansible-role-apache) Master branch: [![Build Status](https://travis-ci.org/limepepper/ansible-role-apache.svg?branch=master)](https://travis-ci.org/limepepper/ansible-role-apache)

LimePepper apache role for ansible
==================

This role handles installing the apache packages, and configuring the service

It is tested against the current versions of Ubuntu, CentOS, Fedora and Debian,
and some legacy systems. You can checkout the current statuses on our [Travis](https://travis-ci.org/limepepper/ansible-role-apache) status page.

To install to your roles directory, use the ansible-galaxy cli:
```shell
$ ansible-galaxy install limepepper.apache
```

## Installing

The apache service is installed to ansible hosts by importing the role into
a play like so:

```yaml
- hosts: webservers

  tasks:
    - import_role:
        name: limepepper.apache
```

 Or using classic role dependency syntax:

```yml
- hosts: webservers
  roles:
    - limepepper.apache

  tasks:
    <...>
```

## configuring

You can then use the modules to create sites like so
```
    - name: add a https vhost for testing
      apache_vhost_ssl:
        ServerName: mywordpresssite2.com
        ServerAliases:
          - www.mywordpresssite2.com
        DocumentRoot: /var/www/mywordpresssite2.com
        SSLCertificateKeyFile: /etc/ssl/private/ansible.com.pem
        SSLCertificateFile: /etc/ssl/crt/ansible.com.crt
        # SSLCertificateChainFile:
      notify:
        - reload apache

```

or

```
    - name: the http vhost to stage the http challenge response
      apache_vhost:
        ServerName: mywordpresssite2.com
        ServerAliases:
          - www.mywordpresssite2.com
        DocumentRoot: /var/www/mywordpresssite2.com
      register: mywordpresssite2_com_vhost
      notify:
        - reload apache
```