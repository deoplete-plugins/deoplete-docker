# Copyright 2016 Koichi Shiraishi. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import re
import threading

from .base import Base
from deoplete.util import load_external_module
load_external_module(__file__, 'urllib3')
load_external_module(__file__, 'dockerhub')
load_external_module(__file__, 'certifi')
from dockerhub.dockerhub import DockerHub

KEYWORD = [
    'ADD', 'ARG', 'CMD', 'COPY', 'ENTRYPOINT', 'ENV', 'EXPOSE', 'FROM',
    'HEALTHCHECK', 'LABEL', 'MAINTAINER', 'RUN', 'SHELL', 'STOPSIGNAL', 'USER',
    'VOLUME', 'WORKDIR'
]


class Source(Base):

    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'docker'
        self.mark = '[Docker]'
        self.filetypes = ['dockerfile']
        self.input_pattern = r'[a-zA-Z_]\w*[:/]\w*|' + \
            r'^\s*[' + '|'.join(KEYWORD) + ']\s+(?:[\w\.]*(?:,\s*)?)*'
        self.rank = 500
        self.debug_enabled = 1

        self.hub = DockerHub()
        self.cache_images = dict()
        self.cache_tags = dict()

        self.keyword_result = [{'word': x} for x in KEYWORD]

    def init(self, context):
        try:
            images = self.hub.search('library')
        except Exception:
            pass
        else:
            self.cache_images['library'] = []
            for i in images:
                self.cache_images['library'].append({
                    'word': i['name'],
                    'kind': i['description'],
                    'dup': 1,
                })

    def on_init(self, context):
        th = threading.Thread(target=self.init, name='init', args=(context, ))
        th.start()

    def get_complete_position(self, context):
        m = re.search(r'\w*$', context['input'])
        return m.start() if m else -1

    def gather_candidates(self, context):
        input_text = context['input']
        if 'FROM' in input_text:
            return self.result_from(context['input'])

        elif 'ONBUILD' in input_text:
            return self.keyword_result

        else:
            return self.keyword_result + [{'word': 'ONBUILD'}]

    def result_from(self, input_text):
        t = input_text.strip('FROM ')
        if t:
            if t.find(':') != -1:
                name = t.split(':')[0]
                if self.cache_tags.get(name):
                    return self.cache_tags[name]
                else:
                    tags = self.hub.tags(name)
                    out = []
                    for i in tags:
                        out.append({
                            'word': i['name'],
                            'dup': 1,
                        })
                    self.cache_tags[name] = out
                    return out

            elif t.find('/') != -1:
                user = t.split('/')[0]
                if self.cache_images.get(user):
                    return self.cache_images[user]
                else:
                    images = self.hub.search(user)
                    out = []
                    for i in images:
                        out.append({
                            'word': i['name'],
                            'kind': i['description'],
                            'dup': 1,
                        })
                    self.cache_images[user] = out
                    return self.cache_images[user]

            else:
                return self.cache_images['library']
