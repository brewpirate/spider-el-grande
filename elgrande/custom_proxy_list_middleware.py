import settings
import requests
import json


class BuildProxyList(object):
    def __init__(self):
        self.build_proxy_list()

    def build_proxy_list(self):
        """
        Generates a Proxy list where the server load is under 60% utilization
        """
        source_url = 'https://nordvpn.com/wp-admin/admin-ajax.php?group=Standard+VPN+servers&country=United+States&action=getGroupRows'
        proxy_response = requests.get(source_url)
        proxy_source = json.loads(proxy_response.content)
        proxy_list = []

        for proxy in proxy_source:
            # If load is under 60% add to the pool
            if proxy.get('load') < 60 and proxy['feature'].get('proxy') and proxy['feature'].get('pptp') and proxy['feature'].get('proxy_ssl') and proxy['feature'].get('socks') and proxy['feature'].get('l2tp'):
                the_proxy = {
                    'domain': proxy.get('domain'),
                    'features': proxy.get('feature'),
                    'load': proxy.get('load'),
                    'exists': proxy.get('exists')
                }
                proxy_list.append(the_proxy)

        if len(proxy_list):
            file = open(settings.PROXY_LIST, 'w')
            for proxy in proxy_list:
                file.write(
                    u' https://{}:{}@{}:80\n'.format(settings.PROXY_USERNAME, settings.PROXY_PASSWORD, proxy['domain']))
            file.close()