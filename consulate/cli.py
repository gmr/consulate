"""Consulate CLI commands"""
import argparse
import json
import sys

from requests import exceptions

from consulate import api


def connection_error():
    sys.stderr.write('ERROR: Could not connect to consul\n')
    sys.exit(1)


def parse_cli_args():
    parser = argparse.ArgumentParser(description='CLI utilities for Consul')

    parser.add_argument('--api-host',  default='localhost',
                        help='The consul host to connect on')
    parser.add_argument('--api-port', default=8500,
                        help='The consul API port to connect to')
    parser.add_argument('--datacenter', default=None,
                        help='The datacenter to specify for the connection')
    parser.add_argument('--token', default=None,
                        help='ACL token')

    sparsers = parser.add_subparsers(title='Commands', dest='command')

    # Service registration
    register = sparsers.add_parser('register',
                                   help='Register a service for this node')

    register.add_argument('-s', '--service-id', default=None,
                          help='Specify a service ID')
    register.add_argument('-t', '--tags', default=[],
                          help='Specify a comma delimited list of tags')

    rsparsers = register.add_subparsers(dest='ctype',
                                        title='Service Check Options')
    check = rsparsers.add_parser('check',
                                 help='Define an external script-based check')

    check.add_argument('interval', default=10, type=int,
                       help='How often to run the check script')
    check.add_argument('path', default=None,
                       help='Path to the script invoked by Consul')
    rsparsers.add_parser('no-check', help='Do not enable service monitoring')

    ttl = rsparsers.add_parser('ttl', help='Define a duration based TTL check')
    ttl.add_argument('duration', type=int, default=10,
                     help='TTL duration for a service with missing check data')

    register.add_argument('name', help='The service name')
    register.add_argument('port', type=int,
                          help='The port the service runs on')

    # K/V database info
    kv = sparsers.add_parser('kv', help='Key/Value Database Utilities')

    kvsparsers = kv.add_subparsers(dest='action',
                                   title='Key/Value Database Utilities')

    backup = kvsparsers.add_parser('backup',
                                   help='Backup to a JSON file')
    backup.add_argument('backup_file', help='Path to backup the content to')
    restore = kvsparsers.add_parser('restore', help='Restore from a JSON file')
    restore.add_argument('restore_file', help='Path to backup the content to')
    kvget = kvsparsers.add_parser('get', help='Get a key from the database')
    kvget.add_argument('key', help='The key to get')
    kvset = kvsparsers.add_parser('set', help='Set a key in the database')
    kvset.add_argument('key', help='The key to set')
    kvset.add_argument('value', help='The value of the key')
    kvdel = kvsparsers.add_parser('del', help='Delete a key from the database')
    kvdel.add_argument('key', help='The key to delete')

    return parser.parse_args()


def main():
    args = parse_cli_args()
    session = api.Session(args.api_host, args.api_port, args.datacenter,
                          args.token)

    if args.command == 'register':
        check = args.path if args.ctype == 'check' else None
        interval = '%ss' % args.interval if args.ctype == 'check' else None
        ttl = '%ss' % args.duration if args.ctype == 'ttl' else None
        tags = args.tags.split(',') if args.tags else None
        try:
            session.agent.service.register(args.name,
                                           args.service_id,
                                           args.port,
                                           tags, check, interval, ttl)
        except exceptions.ConnectionError:
                    connection_error()

    elif args.command == 'kv':

        if args.action == 'backup':
            with open(args.backup_file, 'wb') as handle:
                try:
                    handle.write(json.dumps(session.kv.records(),
                                            ensure_ascii=False,
                                            indent=2))
                except exceptions.ConnectionError:
                            connection_error()

        elif args.action == 'restore':
            with open(args.restore_file, 'rb') as handle:
                data = json.load(handle)
                for row in data:
                    try:
                        session.kv.set_record(row[0], row[1], row[2])
                    except exceptions.ConnectionError:
                        connection_error()

        elif args.action == 'del':
            try:
                del session.kv[args.key]
            except exceptions.ConnectionError:
                connection_error()

        elif args.action == 'get':
            try:
                sys.stdout.write("%s\n" % session.kv.get(args.key))
            except exceptions.ConnectionError:
                connection_error()

        elif args.action == 'set':
            try:
                session.kv[args.key] = args.value
            except exceptions.ConnectionError:
                connection_error()


if __name__ == '__main__':
    main()
