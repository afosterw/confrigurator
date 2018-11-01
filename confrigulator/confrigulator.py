# -*- coding: utf-8 -*-
import logging
import dpath.util

logger = logging.getLogger(__name__)

class Interpolator(object):
    def __init__(self, config):
        pass

    def interpolate(self, value):
        return value

class Layer(object):
    def __init__(self, name):
        self.name = name
        self.dirty = False
        self.writable = False

    def exists(self, key):
        raise Exception('Not implimented')

    def get(self, key, default_value=None):
        raise Exception('Not implimented')

    def set(self, key, value):
        raise Exception('Not implimented')

    def has_key(self, key):
        raise Exception('Not implimented')

    def query(self, query_string):
        raise Exception('Not implimented')

    def write(self):
        raise Exception('Not implimented')

    def load(self, data):
        raise Exception('Not implimented')

class DictLayer(Layer):
    def __init__(self, name, data=None):
        super(DictLayer, self).__init__(name)
        self.data = dict()
        if data:
            self.load(data)
        self.query_engine = DPathQueryEngine()

    def exists(self, key):
        try:
            self.query(key)
        except KeyNotFoundException:
            return False
        except InvalidKeyException:
            return False
        return True

    def get(self, key, default_value=None):
        try:
            return self.query(key)
        except KeyNotFoundException:
            return default_value

    def set(self, key, value, create=True):
        try:
            self.query_engine.set(key, value, self.data, create=create)
        except KeyNotFoundException as e:
            logger.info(e)
            return False
    def remove(self, key):
        try:
            return bool(self.query_engine.remove(key, self.data))
        except KeyNotFoundException as e:
            logger.info(e)
            return False

    def has_key(self, key):
        return self.exists(key)

    def query(self, query_string):
        return self.query_engine.query(query_string, self.data)

    def write(self):
        raise Exception("Not a writable config layer.")

    def load(self, data):
        self.data = data

class ObjectLayer(Layer):
    pass

class YAMLLayer(Layer):
    pass

class KeyNotFoundException(Exception):
    pass

class InvalidKeyException(Exception):
    pass

class DPathQueryEngine:
    def __init__(self, delimiter='.'):
        self.delimiter = delimiter

    def query(self, key, data):
        try:
            return dpath.util.get(data, key, separator=self.delimiter)
        except KeyError as e:
            raise KeyNotFoundException(key)
        except IndexError as e:
            raise InvalidKeyException()

    def set(self, key, value, data, create=True):
        result = dpath.util.set(data, key, value, separator=self.delimiter)
        if result == 0:
            if create:
                logger.debug('Creating new key {}'.format(key))
                dpath.util.new(data, key, value, separator=self.delimiter)
                return 1
            else:
                raise KeyNotFoundException(key)
        return result

    def remove(self, key, data):
        try:
            return dpath.util.delete(data, key, separator=self.delimiter)
        except dpath.exceptions.PathNotFound as e:
            raise(KeyNotFoundException(key))

class ConfigQueryException(Exception):
    def __init__(self, message, query):
        self.message = message
        self.query = query

class LayerQuery(object):
    def __init__(self, query, layer):
        self.query = query
        self.layer = layer
        self.success = False
        self.result = None

    def execute(self):
        try:
            self.result = self.layer.query(query)
            self.success = True
        except KeyNotFoundException as e:
            self.success = False
            self.result = e
        return self.success

class ConfigQuery(object):
    def __init__(self, config, query_string, cast, return_default, default_value, return_first):
        self.config = config
        self.query_string = query_string
        self.cast = cast
        self.return_default = return_default
        self.default_value = default_value
        self.return_first = return_first
        self.executed = False
        self.success = False
        self.layer_queries = list()

    def execute(self, return_first=None):
        self.executed = True
        if return_first is None:
            return_first = self.return_first

        for layer in reversed(config.layers):
            layer_query = LayerQuery(query, layer)
            layer_query.execute()
            self.layer_queries.append(layer_query)
            if layer_query.success:
                self.success = True
                if return_first:
                    return self.success
        return self.success

    def result(self, cast=None, return_default=None, default_value=None, layer=None):
        if self.success:
            result = self.layer_queries[-1].result
            if cast is not None:
                result = cast(result)
            return result
        elif return_default:
            return default_value
        else:
            raise ConfigQueryException(self.query_string, self)


class Config(object):
    def __init__(self, layers=None, retain_queries=False):
        self.layers = list()
        self.queries = list()
        if layers:
            for layer in layers:
                self.layers.append(layer)

    def insert_layer(self, layer, location=None):
        if location is None:
            location = len(self.layers)
        self.layers.insert(location, layer)

    def remove_layer(self, location):
        self.layers.remove(location)

    def index(self):
        return [layer.name for layer in self.layers]

    def query(self, query_string, cast=None, return_default=False, default_value=None, return_first=False, layer_name=None):
        query = Query(
            query_string,
            cast,
            return_default,
            default_value
        )
