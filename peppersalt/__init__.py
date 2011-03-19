import sys
import os
import pkg_resources
import functools
from argparse import ArgumentParser
import venusian
from zope.interface import Interface
from zope.component import registry

class ITask(Interface):
    """ peppersalt task marker """
    def __call__(*args, **kwargs):
        """ execute task """

parser = ArgumentParser()
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
        scanner.registry.registerUtility(ob, ITask, name)
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
    print "peppersalt"
    args = parser.parse_args()
    print args
    print parser

    registry = scan_custers()
    for name, task in registry.getUtilitiesFor(ITask):
        print name, task.__doc__
