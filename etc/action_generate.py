#!/usr/bin/env python
#
# usage:
#   virtualenv venv
#   source ./venv/bin/activate
#   pip install -r ../requirements.txt
#   ./generate_actions.py
import inspect
import jinja2
import os
import pypuppetdb
import pypuppetdb.api
import six

ACTION_TEMPLATE_PATH = "./action_template.j2.yaml"
ACTION_DIRECTORY = "../actions"

# Copied from https://github.com/voxpupuli/pypuppetdb/blob/master/pypuppetdb/api.py
# Ones that are in the documentation but missing in pypuppetdb were added with a MISSING value
# PuppetDB API:
#   https://puppet.com/docs/puppetdb/latest/api/index.html
#
# ENDPOINTS = {
#     'pql': 'pdb/query/v4',
#     'nodes': 'pdb/query/v4/nodes',
#     'environments': 'pdb/query/v4/environments',
#     'producers': 'MISSING',
#     'factsets': 'pdb/query/v4/factsets',
#     'facts': 'pdb/query/v4/facts',
#     'fact-names': 'pdb/query/v4/fact-names',
#     'fact-paths': 'pdb/query/v4/fact-paths',
#     'fact-contents': 'pdb/query/v4/fact-contents',
#     'inventory': 'pdb/query/v4/inventory',
#     'catalogs': 'pdb/query/v4/catalogs',
#     'resources': 'pdb/query/v4/resources',
#     'edges': 'pdb/query/v4/edges',
#     'reports': 'pdb/query/v4/reports',
#     'events': 'pdb/query/v4/events',
#     'event-counts': 'pdb/query/v4/event-counts',
#     'aggregate-event-counts': 'pdb/query/v4/aggregate-event-counts',
#     'package': 'MISSING',
#     'archive': 'MISSING',
#     'cmd': 'MISSING',
#     'summary-stats': 'MISSING',
#     'status': 'status/v1/services/puppetdb-status',
#     'version': 'pdb/meta/v1/version',
#     'server-time': 'pdb/meta/v1/server-time',
#     'mbean': 'metrics/v1/mbeans',
# }


class ActionGenerator(object):

    def jinja_render_file(self, filename, context):
        path, filename = os.path.split(filename)
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader(path or './')
        ).get_template(filename).render(context)

    def render_action(self, action):
        action_data = self.jinja_render_file(ACTION_TEMPLATE_PATH, action)
        action_filename = "{}/{}.yaml".format(ACTION_DIRECTORY, action['name'])
        with open(action_filename, "w") as f:
            f.write(action_data)

    def run(self):
        api = pypuppetdb.api.BaseAPI()

        for name, func in inspect.getmembers(api, lambda x: inspect.ismethod(x)):
            if name.startswith('_'):
                continue

            action = {}
            action['description'] = "TODO"
            action['entry_point'] = "puppetdb_action.py"
            action['name'] = name
            action['method'] = 'GET'
            action['function'] = name
            action['parameters'] = []

            sig = inspect.signature(func)
            #print('{} = {}'.format(name, sig))

            for p_name, param in six.iteritems(sig.parameters):
                if param.kind not in [inspect.Parameter.POSITIONAL_ONLY,
                                      inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                      inspect.Parameter.KEYWORD_ONLY]:
                    continue

                p_type = None
                required = False
                default = None
                # print('param = {}'.format(p_name))
                # print('default = {}'.format(param.default))
                if param.default == param.empty:
                    p_type = 'string'
                    required = True
                elif param.default is None:
                    p_type = 'string'
                elif isinstance(param.default, int):
                    p_type = 'integer'
                    default = str(param.default).lower()
                elif isinstance(param.default, float):
                    p_type = 'number'
                    default = str(param.default).lower()
                elif isinstance(param.default, six.string_types):
                    p_type = 'string'
                    default = str(param.default).lower()

                action['parameters'].append({'name': p_name.strip('_'),
                                             'type': p_type,
                                             'required': required,
                                             'description': '',
                                             'default': default})

            self.render_action(action)

        ###############
        # for name, endpoint in six.iteritems(pypuppetdb.api.ENDPOINTS):
        #     name_underscores = name.replace('-', '_')
        #     action = {}
        #     action['description'] = "TODO"
        #     action['entry_point'] = "puppetdb_action.py"
        #     action['name'] = name_underscores
        #     action['method'] = 'GET'
        #     try:
        #         # this throws AttributeError if it can't find the name
        #         getattr(api, name_underscores)
        #         action['function'] = name_underscores
        #     except AttributeError:
        #         action['endpoint'] = name

        #     self.render_action(action)


if __name__ == "__main__":
    gen = ActionGenerator()
    gen.run()
