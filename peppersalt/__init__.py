import sys
import os
import pkg_resources
import functools
from argparse import ArgumentParser
import venusian
import inspect
from zope.interface import Interface, Attribute, implements
from zope.component import registry, adapts

class MyNamespace(dict):
    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, key):
        return self[key]

class IFuncTask(Interface):
    """ function task marker """

class ITask(Interface):
    """ peppersalt task marker """
    args = Attribute(u"argments")

    def __call__(*args, **kwargs):
        """ execute task """

class FuncTask(object):
    adapts = (IFuncTask,)
    implements(ITask)
    def __init__(self, func):
        self.func = func
        self.args, self.varargs, self.varkw, self.defaults = inspect.getargspec(self.func)
        if self.defaults is None:
            self.defaults = {}
        else:
            self.defaults = dict(zip(self.args, self.defaults))

    def __call__(self, *args, **kwargs):
        kwargs = dict([(k, v) for k, v in kwargs.iteritems() if k in self.args])
        return self.func(*args, **kwargs)

    def __repr__(self):
        return "<FuncTask %s>" % self.func.__name__

    def help(self):
        return self.func.__doc__.split('\n')[0] if self.func.__doc__ else 'no help'
    def description(self):
        return self.func.__doc__ or 'no help'

    def has_default(self, argname):
        return argname in self.defaults

    def get_default(self, argname):
        return self.defaults.get(argname)

        

ENTRY_POINT_NAME = 'peppersalt.tasks'

def get_project_custer():
    here = os.getcwd()
    custer_file = os.path.join(here, 'custer.py')
    if os.path.exists(custer_file):
        return __import__('custer')

def get_plugins():
    return (p.load() for p in pkg_resources.iter_entry_points(ENTRY_POINT_NAME))

def task(func):
    """ task registry """
    def callback(scanner, name, ob):
        scanner.registry.registerUtility(FuncTask(ob), ITask, name)
    venusian.attach(func, callback)
    return func

def scan_custers():
    task_registry = registry.Components()
    project_custer = get_project_custer()
    scanner = venusian.Scanner(registry=task_registry)
    for plugin in get_plugins():
        scanner.scan(plugin)
    scanner.scan(project_custer)
    return task_registry

def main():
    parser = ArgumentParser()
    registry = scan_custers()
    subparsers = parser.add_subparsers()
    for name, task in registry.getUtilitiesFor(ITask):
        subparser = subparsers.add_parser(name, help=task.help())
        for arg in task.args:
            if task.has_default(arg):
                subparser.add_argument('--' + arg, default=task.get_default(arg))
            else:
                subparser.add_argument(arg)
        subparser.set_defaults(task=task)
    args = parser.parse_args(namespace=MyNamespace())
    if args.task:
        args.task(**args)
