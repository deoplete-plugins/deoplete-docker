# Copyright 2016 Koichi Shiraishi. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import json
import urllib3


class DockerHub(object):

    def __init__(self, url=None, version=None):
        self.version = version or 'v2'
        self.url = url or '{0}/{1}'.format(
            'https://hub.docker.com', self.version
        )
        self.http = urllib3.PoolManager()

    def _request(self, path):
        return self.http.request('GET', '{0}/{1}/'.format(self.url, path))

    def search(self, user):
        next = None
        resp = self._request('repositories/{0}'.format(user)).data.decode('utf8')

        while True:
            if next:
                resp = self.http.request('GET', next).data.decode('utf8')

            resp = json.loads(resp)

            for i in resp['results']:
                yield i

            if resp['next']:
                next = resp['next']
                continue

            return

    def tags(self, image):
        user = 'library'
        if '/' in image:
            user, image = image.split('/', 1)

        r = self._request('repositories/{0}/{1}/tags'.format(user, image))
        status = r.status
        if status == 200:
            return json.loads(r.data.decode('utf8'))['results']
        elif status == 404:
            raise ValueError(
                '{0}{1} repository does not exist'.format(user, image)
            )
        else:
            raise ConnectionError(
                '{0} download failed with status {1}'.format(image, status)
            )
