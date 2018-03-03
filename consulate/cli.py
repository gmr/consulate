"""Consulate CLI commands"""
# pragma: no cover
import argparse
import base64
import json
import sys
import os
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from requests import exceptions

import consulate
from consulate import adapters
from consulate import utils

CONSUL_ENV_VAR = 'CONSUL_RPC_ADDR'
EPILOG = ('If the CONSUL_RPC_ADDR environment variable is set, it will be '
          'parsed and used for default values when connecting.')


def on_error(message, exit_code=2):
    """Write out the specified message to stderr and exit the specified
    exit code, defaulting to ``2``.

    :param str message: The exit message
    :param int exit_code: The numeric exit code

    """
    sys.stderr.write(message + '\n')
    sys.exit(exit_code)


def connection_error():
    """Common exit routine when consulate can't connect to Consul"""
    on_error('Could not connect to consul', 1)


ACL_PARSERS = [
    ('backup', 'Backup to stdout or a JSON file', [
        [['-f', '--file'], {'help': 'JSON file to write instead of stdout',
                            'nargs': '?'}],
        [['-p', '--pretty'], {'help': 'pretty-print JSON output',
                              'action': 'store_true'}]]),
    ('restore', 'Restore from stdin or a JSON file', [
        [['-f', '--file'],
         {'help': 'JSON file to read instead of stdin',
          'nargs': '?'}],
        [['-n', '--no-replace'],
         {'help': 'Do not replace existing entries',
          'action': 'store_true'}]])
    ]

KV_PARSERS = [
    ('backup', 'Backup to stdout or a JSON file', [
        [['key'], {'help': 'The key to use as target to backup a '
                           'specific key or folder.',
                   'nargs': '?'}],
        [['-b', '--base64'], {'help': 'Base64 encode values',
                              'action': 'store_true'}],
        [['-f', '--file'], {'help': 'JSON file to write instead of stdout',
                            'nargs': '?'}],
        [['-p', '--pretty'], {'help': 'pretty-print JSON output',
                              'action': 'store_true'}]]),
    ('restore', 'Restore from stdin or a JSON file', [
        [['key'], {'help': 'The key as target to restore to a specific key '
                           'or folder.',
                   'nargs': '?'}],
        [['-p', '--prune'], {'help': 'Remove entries from consul tree that '
                                     'are not in restore file.',
                             'action': 'store_true'}],
        [['-b', '--base64'], {'help': 'Restore from Base64 encode values',
                              'action': 'store_true'}],
        [['-f', '--file'],
         {'help': 'JSON file to read instead of stdin',
          'nargs': '?'}],
        [['-n', '--no-replace'],
         {'help': 'Do not replace existing entries',
          'action': 'store_true'}]]),
    ('ls', 'List all of the keys', [
        [['key'], {'help': 'The key to use as target to list contents of '
                           'specific key or folder',
                   'nargs': '?'}],
        [['-l', '--long'],
         {'help': 'Long format',
          'action': 'store_true'}]]),
    ('mkdir', 'Create a folder', [
        [['path'],
         {'help': 'The path to create'}]]),
    ('get', 'Get a key from the database', [
        [['key'], {'help': 'The key to get'}],
        [['-r', '--recurse'],
         {'help': 'Get all keys prefixed with the specified key',
          'action': 'store_true'}],
        [['-t', '--trim'],
         {'help': 'Number of levels of prefix to trim from returned key',
          'type': int,
          'default': 0}]]),
    ('set', 'Set a key in the database', [
        [['key'], {'help': 'The key to set'}],
        [['value'], {'help': 'The value of the key'}]]),
    ('rm', 'Remove a key from the database', [
        [['key'], {'help': 'The key to remove'}],
        [['-r', '--recurse'],
         {'help': 'Delete all keys prefixed with the specified key',
          'action': 'store_true'}]])]


def add_acl_args(parser):
    """Add the acl command and arguments.

    :param argparse.Subparser parser: parser

    """
    kv_parser = parser.add_parser('acl', help='ACL Utilities')

    subparsers = kv_parser.add_subparsers(dest='action',
                                          title='ACL Database Utilities')

    for (name, help_text, arguments) in ACL_PARSERS:
        parser = subparsers.add_parser(name, help=help_text)
        for (args, kwargs) in arguments:
            parser.add_argument(*args, **kwargs)


def add_kv_args(parser):
    """Add the kv command and arguments.

    :param argparse.Subparser parser: parser

    """
    kv_parser = parser.add_parser('kv', help='Key/Value Database Utilities')

    subparsers = kv_parser.add_subparsers(dest='action',
                                          title='Key/Value Database Utilities')

    for (name, help_text, arguments) in KV_PARSERS:
        parser = subparsers.add_parser(name, help=help_text)
        for (args, kwargs) in arguments:
            parser.add_argument(*args, **kwargs)


def add_register_args(parser):
    """Add the register command and arguments.

    :param argparse.Subparser parser: parser

    """
    # Service registration
    registerp = parser.add_parser('register',
                                  help='Register a service for this node')
    registerp.add_argument('name', help='The service name')
    registerp.add_argument('-a', '--address', default=None,
                           help='Specify an address')
    registerp.add_argument('-p', '--port', default=None, type=int,
                           help='Specify a port')
    registerp.add_argument('-s', '--service-id', default=None,
                           help='Specify a service ID')
    registerp.add_argument('-t', '--tags', default=[],
                           help='Specify a comma delimited list of tags')
    rsparsers = registerp.add_subparsers(dest='ctype',
                                         title='Service Check Options')
    check = rsparsers.add_parser('check',
                                 help='Define an external script-based check')
    check.add_argument('interval', default=10, type=int,
                       help='How often to run the check script')
    check.add_argument('path', default=None,
                       help='Path to the script invoked by Consul')
    httpcheck = rsparsers.add_parser('httpcheck',
                                     help='Define an HTTP-based check')
    httpcheck.add_argument('interval', default=10, type=int,
                           help='How often to run the check script')
    httpcheck.add_argument('url', default=None,
                           help='HTTP URL to be polled by Consul')
    rsparsers.add_parser('no-check', help='Do not enable service monitoring')
    ttl = rsparsers.add_parser('ttl', help='Define a duration based TTL check')
    ttl.add_argument('duration', type=int, default=10,
                     help='TTL duration for a service with missing check data')


def add_run_once_args(parser):
    """Add the run_once command and arguments.

    :param argparse.Subparser parser: parser

    """
    run_oncep = parser.add_parser('run_once',
                                  help='Run a command locked to a single '
                                       'execution')
    run_oncep.add_argument('lock',
                           help='The name of the lock which will be '
                                'held in Consul.')
    run_oncep.add_argument('command_to_run', nargs=argparse.REMAINDER,
                           help='The command to lock')
    run_oncep.add_argument('-i', '--interval', default=None,
                           help='Hold the lock for X seconds')


def add_deregister_args(parser):
    """Add the deregister command and arguments.

    :param argparse.Subparser parser: parser

    """
    # Service registration
    registerp = parser.add_parser('deregister',
                                  help='Deregister a service for this node')
    registerp.add_argument('service_id', help='The service registration id')


def add_services_args(parser):
    """Add the services command and arguments.

    :param argparse.Subparser parser: parser

    """
    # Service registration
    registerp = parser.add_parser('services',
                                  help='List services for this node')

    registerp.add_argument('-i', '--indent', type=int, default=None, help='The indent level for output')

def parse_cli_args():
    """Create the argument parser and add the arguments"""
    parser = argparse.ArgumentParser(description='CLI utilities for Consul',
                                     epilog=EPILOG)

    env_var = os.environ.get(CONSUL_ENV_VAR, '')
    parsed_defaults = urlparse.urlparse(env_var)

    parser.add_argument('--api-scheme',
                        default=parsed_defaults.scheme or 'http',
                        help='The scheme to use for connecting to Consul with')
    parser.add_argument('--api-host',
                        default=parsed_defaults.hostname or 'localhost',
                        help='The consul host to connect on')
    parser.add_argument('--api-port',
                        default=parsed_defaults.port or 8500,
                        help='The consul API port to connect to')
    parser.add_argument('--datacenter',
                        dest='dc',
                        default=None,
                        help='The datacenter to specify for the connection')
    parser.add_argument('--token', default=None, help='ACL token')
    parser.add_argument('--version', action='version',
                        version=consulate.__version__,
                        help='Current consulate version')

    sparser = parser.add_subparsers(title='Commands', dest='command')
    add_acl_args(sparser)
    add_kv_args(sparser)
    add_register_args(sparser)
    add_deregister_args(sparser)
    add_run_once_args(sparser)
    add_services_args(sparser)
    return parser.parse_args()


def acl_backup(consul, args):
    """Dump the ACLs from Consul to JSON

    :param consulate.api_old.Consul consul: The Consul instance
    :param argparser.namespace args: The cli args

    """
    handle = open(args.file, 'w') if args.file else sys.stdout
    acls = consul.acl.list()
    try:
        if args.pretty:
            handle.write(json.dumps(acls, sort_keys=True, indent=2,
                                    separators=(',', ': ')) + '\n')
        else:
            handle.write(json.dumps(acls, sort_keys=True) + '\n')
    except exceptions.ConnectionError:
        connection_error()


def acl_restore(consul, args):
    """Restore the Consul KV store

    :param consulate.api_old.Consul consul: The Consul instance
    :param argparser.namespace args: The cli args

    """
    handle = open(args.file, 'r') if args.file else sys.stdin
    data = json.load(handle)
    for row in data:
        consul.acl.update(row['ID'], row['Name'], row['Type'], row['Rules'])
    print('{0} ACLs written'.format(len(data)))


ACL_ACTIONS = {
    'backup': acl_backup,
    'restore': acl_restore
}


def kv_backup(consul, args):
    """Backup the Consul KV database

    :param consulate.api_old.Consul consul: The Consul instance
    :param argparser.namespace args: The cli args

    """
    handle = open(args.file, 'w') if args.file else sys.stdout
    if args.key:
        args.key = args.key.strip('/')
        prefixlen = len(args.key.split('/'))
        records = [('/'.join(k.split('/')[prefixlen:]), f, v)
                   for k, f, v in consul.kv.records(args.key)]
    else:
        records = consul.kv.records()
    if args.base64:
        if utils.PYTHON3:
            records = [(k, f, str(base64.b64encode(utils.maybe_encode(v)),
                                  'ascii') if v else v)
                       for k, f, v in records]
        else:
            records = [(k, f, base64.b64encode(v) if v else v)
                       for k, f, v in records]
    try:
        if args.pretty:
            handle.write(json.dumps(records, sort_keys=True, indent=2,
                                    separators=(',', ': ')) + '\n')
        else:
            handle.write(json.dumps(records) + '\n')
    except exceptions.ConnectionError:
        connection_error()


def kv_delete(consul, args):
    """Remove a key from the Consulate database

    :param consulate.api_old.Consul consul: The Consul instance
    :param argparser.namespace args: The cli args

    """
    try:
        del consul.kv[args.key]
    except exceptions.ConnectionError:
        connection_error()


def kv_get(consul, args):
    """Get the value of a key from the Consul database

    :param consulate.api_old.Consul consul: The Consul instance
    :param argparser.namespace args: The cli args

    """
    try:
        if args.recurse:
            for key in sorted(consul.kv.find(args.key)):
                displaykey = key
                if args.trim:
                    keyparts = displaykey.split('/')
                    if (args.trim >= len(keyparts)):
                        displaykey = keyparts[-1]
                    else:
                        displaykey = '/'.join(keyparts[args.trim:])
                sys.stdout.write('%s\t%s\n' % (displaykey, consul.kv.get(key)))
        else:
            sys.stdout.write('%s\n' % consul.kv.get(args.key))
    except exceptions.ConnectionError:
        connection_error()


def kv_ls(consul, args):
    """List out the keys from the Consul KV database

    :param consulate.api_old.Consul consul: The Consul instance
    :param argparser.namespace args: The cli args

    """
    try:
        if args.key:
            args.key = args.key.lstrip('/')
            keylist = sorted(consul.kv.find(args.key))
        else:
            keylist = consul.kv.keys()
        for key in keylist:
            if args.long:
                keylen = 0
                if consul.kv[key]:
                    keylen = len(consul.kv[key])
                print('{0:>14} {1}'.format(keylen, key))
            else:
                print(key)
    except exceptions.ConnectionError:
        connection_error()


def kv_mkdir(consul, args):
    """Make a key based path/directory in the KV database

    :param consulate.api_old.Consul consul: The Consul instance
    :param argparser.namespace args: The cli args

    """
    if not args.path[:-1] == '/':
        args.path += '/'
    try:
        consul.kv.set(args.path, None)
    except exceptions.ConnectionError:
        connection_error()


def kv_restore(consul, args):
    """Restore the Consul KV store

    :param consulate.api_old.Consul consul: The Consul instance
    :param argparser.namespace args: The cli args

    """
    if args.prune:
        if args.key:
            args.key = args.key.strip('/')
            keylist = consul.kv.find(args.key)
        else:
            keylist = consul.kv.find('')
    handle = open(args.file, 'r') if args.file else sys.stdin
    data = json.load(handle)
    for row in data:
        if isinstance(row, dict):
            # translate raw api export to internal representation
            if row['Value'] is not None:
                row['Value'] = base64.b64decode(row['Value'])
            row = [row['Key'], row['Flags'], row['Value']]

        if args.base64 and row[2] is not None:
            row[2] = base64.b64decode(row[2])

        # Here's an awesome thing to make things work
        if not utils.PYTHON3 and isinstance(row[2], unicode):
            row[2] = row[2].encode('utf-8')
        if args.key:
            if row[0] == "":
                rowkey = args.key
            else:
                rowkey = args.key + '/' + row[0]
        else:
            rowkey = row[0]
        if args.prune:
            if rowkey in keylist:
                del keylist[rowkey]
        try:
            consul.kv.set_record(rowkey, row[1], row[2], not args.no_replace)
        except exceptions.ConnectionError:
            connection_error()
    if args.prune:
        for key in keylist:
            print("Pruning {0}".format(key))
            try:
                consul.kv.delete(key)
            except exceptions.ConnectionError:
                connection_error()


def kv_rm(consul, args):
    """Remove a key from the Consulate database

    :param consulate.api_old.Consul consul: The Consul instance
    :param argparser.namespace args: The cli args

    """
    try:
        consul.kv.delete(args.key, args.recurse)
    except exceptions.ConnectionError:
        connection_error()


def kv_set(consul, args):
    """Set a value of a key int the Consul database

    :param consulate.api_old.Consul consul: The Consul instance
    :param argparser.namespace args: The cli args

    """
    try:
        consul.kv[args.key] = args.value
    except exceptions.ConnectionError:
        connection_error()


# Mapping dict to simplify the code in main()
KV_ACTIONS = {
    'backup': kv_backup,
    'del': kv_delete,
    'get': kv_get,
    'ls': kv_ls,
    'mkdir': kv_mkdir,
    'restore': kv_restore,
    'rm': kv_rm,
    'set': kv_set}


def register(consul, args):
    """Handle service registration.

    :param consulate.api_old.Consul consul: The Consul instance
    :param argparser.namespace args: The cli args

    """
    check = args.path if args.ctype == 'check' else None
    httpcheck = args.url if args.ctype == 'httpcheck' else None
    interval = '%ss' % args.interval if args.ctype in ['check',
                                                       'httpcheck'] else None
    ttl = '%ss' % args.duration if args.ctype == 'ttl' else None
    tags = args.tags.split(',') if args.tags else None
    try:
        consul.agent.service.register(args.name, args.service_id, args.address,
                                      int(args.port), tags, check, interval,
                                      ttl, httpcheck)
    except exceptions.ConnectionError:
        connection_error()


def deregister(consul, args):
    """Handle service deregistration.

    :param consulate.api_old.Consul consul: The Consul instance
    :param argparser.namespace args: The cli args

    """
    try:
        consul.agent.service.deregister(args.service_id)
    except exceptions.ConnectionError:
        connection_error()


def run_once(consul, args):
    """Ensure only one process can run a command at a time

    :param consulate.api_old.Consul consul: The Consul instance
    :param argparser.namespace args: The cli args

    """
    import time
    import subprocess

    error_msg, error_code = None, None
    try:
        consul.lock.prefix('')
        with consul.lock.acquire(args.lock):
            if args.interval:
                now = int(time.time())
                last_run = consul.kv.get("{0}_last_run".format(args.lock))
                if str(last_run) not in ['null', 'None'] and \
                        int(last_run) + int(args.interval) > now:
                    sys.stdout.write(
                        'Last run happened fewer than {0} seconds ago. '
                        'Exiting\n'.format(args.interval))
                    return
                consul.kv["{0}_last_run".format(args.lock)] = now

            # Should the subprocess return an error code, release the lock
            try:
                print(subprocess.check_output(args.command_to_run[0].strip(),
                                              stderr=subprocess.STDOUT,
                                              shell=True))
            # If the subprocess fails
            except subprocess.CalledProcessError as err:
                error_code = 1
                error_msg = ('"{0}" exited with return code "{1}" and '
                             'output {2}'.format(args.command_to_run,
                                                 err.returncode,
                                                 err.output))
            except OSError as err:
                error_code = 1
                error_msg = '"{0}" command does not exist'.format(
                    args.command_to_run, err)
            except Exception as err:
                error_code = 1
                error_msg = '"{0}" exited with error "{1}"'.format(
                    args.command_to_run, err)

    except consulate.LockFailure:
        on_error('Cannot obtain the required lock. Exiting')

    except exceptions.ConnectionError:
        connection_error()

    if error_msg:
        on_error(error_msg, error_code)


def services(consul, args):
    """Dump the list of services registered with Consul

    :param consulate.api.Consul consul: The Consul instance
    :param argparser.namespace args: The cli args

    """

    svcs = consul.agent.services()
    print(json.dumps(svcs,
                     sort_keys=True,
                     indent=args.indent,
                     separators=(',', ': ')) + '\n')


def main():
    """Entrypoint for the consulate cli application"""
    args = parse_cli_args()

    if args.api_scheme == 'http+unix':
        adapter = adapters.UnixSocketRequest
        port = None

        api_host = os.environ.get('CONSUL_HTTP_ADDR').replace('unix://', '')
        if args.api_host:
            api_host = args.api_host
    else:
        adapter = None
        port = args.api_port

        api_host = 'localhost'
        if args.api_host:
            api_host = args.api_host

    consul = consulate.Consul(api_host, port, args.dc,
                              args.token, args.api_scheme, adapter)

    if args.command == 'acl':
        ACL_ACTIONS[args.action](consul, args)
    elif args.command == 'kv':
        KV_ACTIONS[args.action](consul, args)
    elif args.command == 'register':
        register(consul, args)
    elif args.command == 'deregister':
        deregister(consul, args)
    elif args.command == 'services':
        services(consul, args)
    elif args.command == 'run_once':
        run_once(consul, args)
