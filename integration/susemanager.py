from xmlrpc.client import ServerProxy


class SuseManager:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.client = None
        self.token = None

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.logout()

    def login(self):
        if self.client is None:
            self.client = ServerProxy('{}/rpc/api'.format(self.url), use_datetime=True)
            self.token = self.client.auth.login(self.username, self.password)

    def logout(self):
        if self.client is not None:
            self.client.auth.logout(self.token)
            self.client = None
            self.token = None

    def exec(self, class_name, function_name, args=None, retries=0):
        if self.client is None:
            return None
        args = [] if args is None else args
        function_obj = getattr(getattr(self.client, class_name), function_name)
        return function_obj(self.token, *args)

    def get_device_id(self, device_name):
        return self.exec('system', 'getId', (device_name,))[0]['id']

    def get_package_ids(self, package_name, package_version=None):
        packages = []
        if package_version is None:
            results = self.exec('packages.search', 'name', (package_name,))
        else:
            query = 'name:{0} AND version:{1}'.format(package_name, package_version)
            results = self.exec('packages.search', 'advanced', (query,))
        for package in results:
            if package['name'] == package_name and (package_version is None or package['version'] == package_version):
                packages.append(package['id'])
        return packages
