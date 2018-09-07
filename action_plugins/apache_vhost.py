
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action import ActionBase
from ansible.utils.vars import merge_hash
from ansible.module_utils._text import to_text
from ansible import constants as C
from ansible.module_utils._text import to_bytes, to_native, to_text
# from ansible.plugins.action.ce import ActionModule as _ActionModule
# from ansible.plugins.action.template import ActionModule as _ActionModule
# from ansible.plugins.action.copy import _create_remote_file_args
# from ansible.plugins.action.copy import REAL_FILE_ARGS
from ansible.module_utils.basic import FILE_COMMON_ARGUMENTS

import inspect
import pprint
import os
import os.path
import tempfile
import shutil


def _create_remote_file_args(module_args):
    """remove keys that are not relevant to file"""
    return dict((k, v) for k, v in module_args.items() if k in REAL_FILE_ARGS)


REAL_FILE_ARGS = frozenset(FILE_COMMON_ARGUMENTS.keys()).union(
                          ('state', 'path', '_original_basename', 'recurse', 'force',
                           '_diff_peek', 'src')).difference(
                          ('content', 'decrypt', 'backup', 'remote_src', 'regexp', 'delimiter',
                           'directory_mode', 'unsafe_writes'))


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):

        # pp = pprint.PrettyPrinter(indent=4)

        # for name in globals():
        #     pp.pprint(name)

        changed = False

        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)
        result['results'] = []

        server_name = self._task.args.get('ServerName', None)
        # server_aliases = self._task.args.get('ServerAliases', None)
        # document_root = self._task.args.get('DocumentRoot', None)
        # state = self._task.args.get('state', None)
        # # force = boolean(self._task.args.get('force', True), strict=False)

        task_vars['vhost'] = {}
        task_vars['vhost']['Listen'] = self._task.args.get('Listen', None)
        task_vars['vhost']['ServerName'] = self._task.args.get(
            'ServerName', None)
        task_vars['vhost']['ServerAliases'] = self._task.args.get(
            'ServerAliases', None)
        task_vars['vhost']['DocumentRoot'] = self._task.args.get(
            'DocumentRoot', None)
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
            'httpd-conf.j2')

        #
        tmpl_args = dict(
            src=src,
            dest="{0}/{1}.conf".format(dest_path, server_name)
        )
        # self._task.args.copy()

        # call the template action on our params
        ret1 = WrapTemplate(
            self, tmpl_args).run(task_vars=task_vars)

        changed=changed or ret1['changed']

        result['results'].append(ret1)

        print("result")
        print(result)
        print("")

        src_path = task_vars['apache_sites_available']
        dest_path = task_vars['apache_site_enabled_conf_path']

        tmpl_args = dict(
            src='{0}/{1}.conf'.format(src_path, server_name),
            path="{0}/{1}.conf".format(dest_path, server_name),
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

        # changed = changed or module_return['changed']

        result['results'].append(module_return)
        print("module_return changed")
        print(module_return['changed'])

        print("result")
        print(result)

        result['changed'] = changed

        return result

#
# BOILERPLATE STUFF THAT WOULD NORMALLY BE IN A module
#


class BaseWrap:
    def __init__(self, action):

        self.action = action

    def get_template_path(self):

        # print("apache_vhost original path is :")
        # print(self.action._original_path)

        mypath = os.path.abspath(
            os.path.join(
                os.path.join(self.action._original_path, os.pardir),
                os.pardir)
        )

        source = os.path.join(
            mypath,
            'templates'
        )

        return source


class WrapSymlink(BaseWrap):

    def __init__(self, action, args):

        BaseWrap.__init__(self, action)

        self.task = action._task
        self.args = args

        # print(self.args)

    def run(self, task_vars):

        new_task = self.task.copy()
        new_task.args = self.args

        # Use file module to create these
        # print(self.args)
        new_module_args = _create_remote_file_args(self.args)
        print(new_module_args)
        # new_module_args['path'] = os.path.join(dest, dest_path)
        # new_module_args['src'] = '/etc/apache2/sites-available/mywordpresssite2.com-ssl.conf'
        # new_module_args['state'] = 'link'
        new_module_args['force'] = True

        module_return = self.action._execute_module(
            module_name='file', module_args=new_module_args, task_vars=task_vars)

        return module_return


class WrapTemplate(BaseWrap):

    ARGS = ['src',
            'dest',
            'state',
            'newline_sequence',
            'variable_start_string',
            'variable_end_string',
            'block_start_string',
            'block_end_string']

    def __init__(self, action, args):

        BaseWrap.__init__(self, action)

        self.task = action._task
        self.args = args

    def run(self, task_vars):
        new_task = self.task.copy()

        new_task.args = self.args

        # print("templar loader environment search path")
        # print(self.action._templar.environment.loader.searchpath)

        new_basedir = self.get_template_path()

        self.action._templar.environment.loader.searchpath = [new_basedir]

        # print("templar loader environment search path - updated")
        # print(self.action._templar.environment.loader.searchpath)

        loader = self.action._shared_loader_obj.action_loader
        action = loader.get('template',
                            task=new_task,
                            connection=self.action._connection,
                            play_context=self.action._play_context,
                            loader=self.action._loader,
                            templar=self.action._templar,
                            shared_loader_obj=self.action._shared_loader_obj)

        action._loader._basedir = new_basedir

        # print("got vhost from task_vars")
        # print(task_vars.get('vhost', []))

        return action.run(task_vars=task_vars)


class WrapCopy():

    def __init__(self, module):

        self.module = module
        self._p = self.module.params
