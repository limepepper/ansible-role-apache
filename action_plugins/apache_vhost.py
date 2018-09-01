
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action import ActionBase
from ansible.utils.vars import merge_hash
from ansible.module_utils._text import to_text
from ansible import constants as C
from ansible.module_utils._text import to_bytes, to_native, to_text
# from ansible.plugins.action.ce import ActionModule as _ActionModule
# from ansible.plugins.action.template import ActionModule as _ActionModule

import inspect
import pprint
import os
import os.path
import tempfile
import shutil

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):

      pp = pprint.PrettyPrinter(indent=4)
      results = []

      if task_vars is None:
          task_vars = dict()

      result = super(ActionModule, self).run(tmp, task_vars)

      server_name = self._task.args.get('ServerName', None)
      server_aliases = self._task.args.get('ServerAliases', None)
      document_root = self._task.args.get('DocumentRoot', None)
      state = self._task.args.get('state', None)
      # force = boolean(self._task.args.get('force', True), strict=False)

      task_vars['vhost'] = {}
      task_vars['vhost']['Listen'] = self._task.args.get('Listen', None)
      task_vars['vhost']['ServerName'] = self._task.args.get('ServerName', None)
      task_vars['vhost']['ServerAliases'] = self._task.args.get('ServerAliases', None)
      task_vars['vhost']['DocumentRoot'] = self._task.args.get('DocumentRoot', None)
      dest_path = task_vars['apache_sites_available_dir']

      #
      tmpl_args = dict(
        src='httpd-conf.j2',
        dest="{0}/{1}.conf".format(dest_path,server_name)
      )
      # self._task.args.copy()

      # call the template action on our params
      results.append(WrapTemplate(self, tmpl_args).run(task_vars=task_vars))


      return dict(results=results)

#
# BOILERPLATE STUFF THAT WOULD NORMALLY BE IN A module
#

class BaseWrap:
  def __init__(self, action):

      self.action = action

  def get_template_path(self):

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

      print(self.action._templar.environment.loader.searchpath)

      new_basedir = self.get_template_path()

      self.action._templar.environment.loader.searchpath = [new_basedir]

      print(self.action._templar.environment.loader.searchpath)

      loader = self.action._shared_loader_obj.action_loader
      action = loader.get('template',
                            task=new_task,
                            connection=self.action._connection,
                            play_context=self.action._play_context,
                            loader=self.action._loader,
                            templar=self.action._templar,
                            shared_loader_obj=self.action._shared_loader_obj)

      action._loader._basedir = new_basedir

      print(task_vars.get('vhost', []))


      return action.run(task_vars=task_vars)

class WrapCopy():

  def __init__(self, module):

      self.module = module
      self._p = self.module.params

      return result
