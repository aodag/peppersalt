from peppersalt import task

@task
def test(suite=None):
    """ run test """
    print "run test %s" % suite
