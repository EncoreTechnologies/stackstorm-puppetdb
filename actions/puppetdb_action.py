from st2common.runners.base_action import Action
import json
import pypuppetdb
import os
import six
import socket

PUPPET_CERTNAME = socket.gethostname()
PUPPET_SSLDIR = '/etc/puppetlabs/puppet/ssl'


class PuppetDBAction(Action):

    def run(self,
            connection='',
            server='',
            port=8081,
            transport='https',
            ssldir=PUPPET_SSLDIR,
            certname=PUPPET_CERTNAME,
            ssl_verify=True,
            # query options
            query=None,
            order_by=None,
            limit=None,
            offset=None,
            include_total=None,
            # invocation
            endpoint='',
            function='',
            method='GET'):

        if not ssl_verify:
            ssl_verify = False
            import requests
            requests.packages.urllib3.disable_warnings()

        # get proper SSL cert paths
        ssl_key = '{}/private_keys/{}.pem'.format(ssldir, certname)
        ssl_cert = '{}/certs/{}.pem'.format(ssldir, certname)
        ssl_ca = '{}/certs/ca.pem'.format(ssldir)
        os.environ['REQUESTS_CA_BUNDLE'] = ssl_ca

        # create our client
        client = pypuppetdb.connect(host=server,
                                    port=port,
                                    ssl_verify=ssl_verify,
                                    ssl_key=ssl_key,
                                    ssl_cert=ssl_cert,
                                    protocol=transport)

        if function:
            raw_data = getattr(client, function)()
            data = [d.__dict__ for d in raw_data]
        else:
            if not isinstance(query, six.string_types):
                query = json.dumps(query)
            data = client._query(endpoint, query=query)
        return data
