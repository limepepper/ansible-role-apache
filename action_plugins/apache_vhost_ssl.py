
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action import ActionBase
from ansible.utils.vars import merge_hash
from ansible.module_utils._text import to_text
from ansible import constants as C
from ansible.module_utils._text import to_bytes, to_native, to_text
# from ansible.plugins.action.ce import ActionModule as _ActionModule
# from ansible.plugins.action.template import ActionModule as _ActionModule
from ansible.plugins.action.copy import _create_remote_file_args

import inspect
import pprint
import os
import os.path
import tempfile
import shutil
import sys

#from action_plugins.common import ensure_dcos, run_command, _dcos_path
sys.path.append(os.getcwd())
from action_plugins.apache_vhost import ActionModule as _ActionModule
from action_plugins.apache_vhost import BaseWrap, WrapCopy, WrapTemplate, WrapSymlink


class ActionModule(_ActionModule):
    def run(self, tmp=None, task_vars=None):

        pp = pprint.PrettyPrinter(indent=4)
        results = []

        changed = True

        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)

        server_name = self._task.args.get('ServerName', None)
        server_aliases = self._task.args.get('ServerAliases', None)
        document_root = self._task.args.get('DocumentRoot', None)
        state = self._task.args.get('state', 'present')
        # force = boolean(self._task.args.get('force', True), strict=False)

        task_vars['vhost'] = {}
        task_vars['vhost']['Listen'] = self._task.args.get('Listen', None)
        task_vars['vhost']['DocumentRoot'] = self._task.args.get(
            'DocumentRoot', None)
        task_vars['vhost']['ServerName'] = self._task.args.get(
            'ServerName', None)
        task_vars['vhost']['ServerAliases'] = self._task.args.get(
            'ServerAliases', None)
        task_vars['vhost']['SSLCertificateFile'] = self._task.args.get(
            'SSLCertificateFile', None)
        task_vars['vhost']['SSLCertificateKeyFile'] = self._task.args.get(
            'SSLCertificateKeyFile', None)
        task_vars['vhost']['SSLCertificateChainFile'] = self._task.args.get(
            'SSLCertificateChainFile', None)

        dest_path = task_vars['apache_sites_available']

        #
        tmpl_args = dict(
            src='/home/tomhodder/Dropbox/bin/ansible/roles/limepepper.apache/templates/conf/httpd-ssl-conf.j2',
            dest="{0}/{1}-ssl.conf".format(dest_path, server_name)
        )
        # self._task.args.copy()

        # call the template action on our params
        results.append(WrapTemplate(self, tmpl_args).run(task_vars=task_vars))

        # dest = self._remote_expand_user(dest)

        src_path = task_vars['apache_sites_available']
        dest_path = task_vars['apache_sites_enabled']

        tmpl_args = dict(
            src='{0}/{1}-ssl.conf'.format(src_path, server_name),
            path="{0}/{1}-ssl.conf".format(dest_path, server_name),
            state='link'
        )

        module_return = WrapSymlink(self, tmpl_args).run(task_vars=task_vars)

        if module_return.get('failed'):
            # result.update(module_return)
            # return self._ensure_invocation(result)
            raise ValueError("boorked '%s' is not valid."
                             "mod failed failed." % module_return)

        module_executed = True
        changed = changed or module_return.get('changed', False)

        results.append(module_return)

        return dict(results=results, changed=True)
