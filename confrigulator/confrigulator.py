# -*- coding: utf-8 -*-
class Interpolator(object):
    def __init__(self, config):
        pass

    def interpolate(self, value):
        return value

class Layer(object):
    def __init__(self, name, data=None):
        self.name = name
        self.dirty = False
        self.writable = False
        self.data = dict()
        if data:
            self.load(data)

    def exists(self, key):
        pass

    def get(self, key):
        return self.data.get()

    def set(self, key, value):
        pass

    def write(self):
        pass

    def load(self, data):
        pass

class ObjectLayer(Layer):
    pass

class YAMLLayer(Layer):
    pass

class QueryParser(object):
    pass

class KeyNotFoundException(Exception):
    pass

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
            self.result = self.layer.get(query)
            self.success = True
        except KeyNotFoundException as e:
            self.success = False
            self.result = e
        return self.success

class ConfigQuery(object):
    def __init__(self, config, query_parser, query_string, cast, return_default, default_value, return_first):
        self.config = config
        self.query_string = query_string
        self.query = list()
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
    def __init__(self, layers=None, query_parser=QueryParser, retain_queries=False):
        self.layers = list()
        self.query_parser = query_parser()
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
            self.query_parser.parse(query_string),
            cast,
            return_default,
            default_value
        )
