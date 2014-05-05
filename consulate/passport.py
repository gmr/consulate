"""
Passport uses the Tornado template engine to render files, injecting values
from Consul services and kv pairs.

"""
import argparse
from os import path

from tornado import template

from consulate import api


class Loader(template.Loader):

    def __init__(self, root_directory='/', session=None, **kwargs):
        super(Loader, self).__init__(root_directory, **kwargs)
        self.root = root_directory
        self.session = session

    def _create_template(self, name):
        value = self.session.kv.get(path.join(self.root, name), None)
        if value:
            return template.Template(value, name=name, loader=self)
        else:
            raise KeyError


class Passport(object):

    def __init__(self, host=api.DEFAULT_HOST, port=api.DEFAULT_PORT, dc=None):
        self.session = api.Consulate(host, port, dc)
        self.loader = Loader(session=self.session)

    def render(self, key):
        t = self.loader.load(key)
        namespace = {'consul': self.session}
        return t.generate(**namespace)

    def process(self, key, path):
        value = self.render(key)
        with open(path, 'wb') as handle:
            handle.write(value)


def main():
    parser = argparse.ArgumentParser(description=
                                         'Render templates from Consul')

    parser.add_argument('-t', '--template', help='The path to the template')
    parser.add_argument('-d', '--destination',
                        help='The path to write the rendered template to')
    args = parser.parse_args()
    passport = Passport()
    if passport.process(args.template, args.destination):
        print('Generated %s' % args.destination)


if __name__ == '__main__':
    main()
