
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

        changed = False

        if task_vars is None:
            task_vars = dict()

        # result = super(ActionModule, self).run(tmp, task_vars)
        result = {}

        result['results'] = []

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

        path_stack = self._task.get_search_path()

        path_stack = path_stack + \
            [os.path.join(x, 'limepepper.apache')
             for x in getattr(C, 'DEFAULT_ROLES_PATH')]

        # if the task is in a role, add that to the search path
        if self._task._role:
            path_stack = path_stack + self._task._role._role_path

        task_dir_parent = os.path.join(
            os.path.dirname(self._task.get_path()), os.pardir)

        if os.path.exists(
                os.path.join(
                    task_dir_parent, 'tasks')) and task_dir_parent not in path_stack:
            path_stack.append(task_dir_parent)

        src = self._loader.path_dwim_relative_stack(
            path_stack,
            'templates/conf',
            'httpd-ssl-conf.j2')

        tmpl_args = dict(
            src=src,
            dest="{0}/{1}-ssl.conf".format(dest_path, server_name)
        )

        ret1 = WrapTemplate(self, tmpl_args).run(task_vars=task_vars)

        changed = changed or ret1['changed']

        results.append(ret1)

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
        result['changed'] = changed

        return result
