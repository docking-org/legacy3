#!/usr/bin/env python
'''connects to ZINC database for smiles, vendors, etc.

Michael Mysinger 200801 Created
Ryan Coleman 201204 Edited down to just SQL queries. See getposes.py for more.
'''

import os
import sys

import requests

REMARK_PREFIX = "#    "

# MySQL server
ZINC_URL = os.environ.get('ZINC_URL', 'http://zinc15.docking.org/')
SUBSTANCE_FIELDS = os.environ.get('ZINC_SUBSTANCE_FIELDS', 'Substance Smiles=smiles+Vendor=vendor_catalogs')


class ZINCAPIResource(object):
    _having = {}
    _subsets = set()

    def __init__(self, api, name, fields=()):
        self._api = api
        self.name = name
        self._fields = []
        self._add_fields(fields)

    @property
    def _resource(self):
        return self

    def output_fields(self, *fields):
       new = self.copy()
       new._add_fields(fields)
       return new

    def _add_fields(self, fields, only_new=True):
        if only_new:
            for field in fields:
                if field not in self._fields:
                    self._fields.append(field)
        else:
            self._fields.extend(fields)

    def subsets(self, subsets):
        return ZINCAPIConstrainedResource(self, subsets=subsets)

    def having(self, having):
        return ZINCAPIConstrainedResource(self, having=having)

    def list(self, *args, **kwargs):
        return self._api.list_resource(self, *args, **kwargs)

    def get(self, key, *args, **kwargs):
        return self._api.get_resource(self, key, *args, **kwargs)


class ZINCAPIConstrainedResource(object):
    def __init__(self, resource, subsets=(), having=()):
        # TODO Relations (as a subclass?)
        # TODO Add computed types
        self._resource = resource
        self._subsets = set()
        self._having = {}
        self._add_subsets(subset)
        self._add_having(having)

    @property
    def _api(self):
        return self._resource._api

    @property
    def _fields(self):
        return self.resource._fields

    def copy(self):
        cls = type(self)
        new = cls(
            resource=resource,
            subsets=self._subsets,
            having=self._having)
        return new

    def subsets(self, *subsets):
       new = self.copy()
       new._add_subsets(subsets)
       return new

    def having(self, *args, **kwargs):
        new = self.copy()
        new._add_having(args)
        new._add_having(kwargs)
        return new

    def _add_subsets(self, subsets):
        self._subsets.update(subsets)

    def _add_having(self, having):
        if isinstance(having, dict):
            for key, value in list(having.items()):
                if not isinstance(value, (tuple, list)):
                    self._having.setdefault(key, set).add(value)
                else:
                    self._having.setdefault(key, set).update(value)
        else:
            for key in having:
                self._having.setdefault(key, set)

    def filter(self, **kwargs):
        # TODO
        raise NotImplemented("Query api under development")

    def list(self, *args, **kwargs):
        return self._api.list_resource(self, *args, **kwargs)


class ZINCEntityInstance(object):
    def __init__(self, resource, key, data=None):
        # TODO actual field allocations
        self._resource = resource
        self._key = key
        self._data = {}
        self._populate(data)

    @property
    def _api(self):
        return self._resouce._api

    def _populate(self, data, overwrite=True):
        if data:
            data = dict(data)
            for key, value in list(data.items()):
                if overwrite and key not in self._data:
                    self._data[key] = value

    def _getdata(self, name):   
        if name not in self._data:
            self._populate(self._api.populate_entity(self, fields=[name]))
        return self._data[name]

    def __getitem__(self, name):
        return self._getdata(name)

    def __getattr__(self, name):
        return self._getdata(name)


class ZINCAPI(object):
    DEFAULT_OUTPUT_FORMAT = 'json'

    def __init__(self, base=ZINC_URL, output_format=DEFAULT_OUTPUT_FORMAT):
        self.base = base
        self.format = output_format
        self._resources = {}

    def _get_resource_object(self, name):
        if name not in self._resources:
            self._resources[name] = ZINCAPIResource(self, name)
        return self._resources[name]

    def make_url_for_resource(self, entity, params=None):
        params = params or {}
        resource = entity._resource
        key = getattr(entity, '_key', getattr(resource, '_key', None))
        parts = [resource.name]
        paged = True
        if key:
            parts.append(str(key))
            paged = False
            if getattr(resource, '_relation', None):
                parts.append(str(resource._relation))
                paged=True
        if getattr(resource, '_subsets', None):
            parts.append('subsets')
            parts.append('+'.join(map(str, sorted(resource.subsets))))
        if getattr(resource, '_having', None):
            parts.append('having')
            hss = []
            items = list(map(str, sorted(resource._having.keys())))
            parts.append('+'.join(map(str, items)))
            for key in items:
                for ss in (items.get(key, None) or ()):
                    hss.append('{!s}.{!s}'.format(key, items[key]))
            if hss:
                parts.append('subsets')
                parts.append('+'.join(hss))

        path = '/'.join(parts)
        
        ext = params.pop('format', params.pop('output_format', self.format))
        fields = params.pop('fields', params.pop('output_fields', resource._fields))

        if ext:
            if fields:
                path = '{}.{}:{}'.format(path, ext, '+'.join(fields))
            else:
                path = '{}.{}'.format(path, ext)
        elif fields:
            params.setdefault('output_fields', fields)

        if paged:
            get_all = params.pop('all', False)
            if get_all:
                params['count'] = 'all'

        real_params = {}
        for key, value in list(params.items()):
            if isinstance(key, str):
                real_params[key] = value
            else:
                pass
                #TODO Query params etc

        url = self.base + path

        return url, params

    def list_resource(self, resource):
        pass

    def get_resource(self, resource, key, **kwargs):
        entity = ZINCEntityInstance(resource, key)
        entity._populate(self.fetch_entity_data(entity, **kwargs))
        return entity
 
    def fetch_entity_data(self, entity, **kwargs):
        url, params = self.make_url_for_resource(entity, kwargs)
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise KeyError("{} not found at {}".format(entity._key, url))
	

    def __getattr__(self, name):
        if name[0].isupper():
            pass
        else:
            return self._get_resource_object(name)


if __name__ == "__main__":
  pass  # no way to run from commandline
