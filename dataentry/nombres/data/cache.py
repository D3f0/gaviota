#! /usr/bin/env python
# -*- encoding: utf-8 -*-

class cache_by_params(object):
    def __init__(self, verbose = False):
        self.cache = {}
        self.verbose = verbose

    def __call__(self, f):

        def wrapped(*largs, **kwargs):
            pass
