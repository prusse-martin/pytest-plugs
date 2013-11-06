from __future__ import print_function, with_statement, division
from distutils.version import LooseVersion

import os
import sys
import tarfile
from zipfile import ZipFile

#===================================================================================================
# py2x3 compatibility
#===================================================================================================
# tox.ini contents when downloaded package does not have a tox.ini file
# in this case we only display help information
PLACEHOLDER_TOX = '''\
[tox]

[testenv]
deps=pytest
commands=
    py.test --help
'''

#===================================================================================================
# py2x3 compatibility
#===================================================================================================

if sys.version_info[0] == 3:
    from xmlrpc.client import ServerProxy
    from urllib.request import urlretrieve
else:
    from xmlrpclib import ServerProxy
    from urllib import urlretrieve


#===================================================================================================
# iter_plugins
#===================================================================================================
def iter_plugins(client, search='pytest-'):
    '''
    Returns an iterator of (name, version) from PyPI.

    :param client: xmlrpclib.ServerProxy
    :param search: package names to search for
    '''
    for plug_data in client.search({'name': search}):
        yield plug_data['name'], plug_data['version']


#===================================================================================================
# run_devpi
#===================================================================================================
def run_devpi(name):
    tox_env = 'py%d%d' % sys.version_info[:2]

    fallback_tox = 'fallback-tox.ini'
    if not os.path.isfile(fallback_tox):
        f = open(fallback_tox, 'w')
        try:
            f.write(PLACEHOLDER_TOX)
        finally:
            f.close()

    result = os.system('devpi test --fallback-ini=%s %s --tox-args="-e %s"' % (fallback_tox, name, tox_env))
    return result


#===================================================================================================
# main
#===================================================================================================
def main():
    client = ServerProxy('https://pypi.python.org/pypi')

    plugins = iter_plugins(client)
    #plugins = list(get_latest_versions(plugins))
    plugins = [
        ('pytest-pep8', '1.0.5'),
    #    ('pytest-cache', '1.0'),
    #    ('pytest-xdist', '1.9'),
    #    ('pytest-bugzilla', '0.2'),
    ]

    result = os.system('devpi quickstart')
    if result != 0:
        sys.exit('failed to start devpi server')

    test_results = {}
    for name, version in plugins:
        print('=' * 60)
        print('%s-%s' % (name, version))
        result = run_devpi(name)
        test_results[(name, version)] = result


    print('\n\n')
    print('=' * 60)
    print('Summary')
    print('=' * 60)
    for (name, version) in sorted(test_results):
        result = test_results[(name, version)]
        if result == 0:
            status = 'OK'
        else:
            status = 'Failed'
        package = '%s-%s' % (name, version)
        spaces = (50 - len(package)) * ' '
        print('%s%s%s' % (package, spaces, status))


#===================================================================================================
# main
#===================================================================================================
if __name__ == '__main__':
    main()  
