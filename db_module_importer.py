# coding=utf-8
import types


class DBModuleImporter(object):

   def __init__(self, modules):
       self._modules = dict(modules)


   def find_module(self, fullname, path):
      if fullname in self._modules.keys():
         return self
      return None

   def load_module(self, fullname):
      if not fullname in self._modules.keys():
         raise ImportError(fullname)

      new_module = types.ModuleType(fullname)
      exec(self._modules[fullname] in new_module.__dict__)
      return new_module
