#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `confrigulator` package."""

import pytest

from click.testing import CliRunner

from confrigulator import confrigulator
from confrigulator import cli

@pytest.fixture
def root_layer_data():
    data = {
        'root': {
            'root_branch_dict': {
                    'root_branch_list': [1,2,3,4,5],
                    'root_branch_value': 'original_value'
            },
            'root_list': [1,2,3,4,5],
            'root_value': 'original_value'
        }
    }
    return data

@pytest.fixture
def root_layer_name():
    return 'root'

@pytest.fixture
def root_layer(root_layer_name, root_layer_data):
    return confrigulator.DictLayer(root_layer_name, data=root_layer_data)

@pytest.fixture
def root_config(root_layer):
    return confrigulator.Config(layers=[root_layer])

@pytest.fixture
def dpath_query_engine():
    return confrigulator.DPathQueryEngine()

@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'confrigulator.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output

def test_config(root_config, root_layer_name):
    assert root_config.index() == [root_layer_name]


class TestDPathQueryEngine:
    def test_create(self, dpath_query_engine):
        assert dpath_query_engine.delimiter == '.'

    def test_query(self, dpath_query_engine, root_layer_data):
        assert dpath_query_engine.query('root.root_branch_dict.root_branch_value', root_layer_data) == 'original_value'

    def test_invalid_key(self, dpath_query_engine, root_layer_data):
        with pytest.raises(confrigulator.InvalidKeyException):
            dpath_query_engine.query('', root_layer_data)

    def test_key_not_found(self, dpath_query_engine, root_layer_data):
        with pytest.raises(confrigulator.KeyNotFoundException):
            dpath_query_engine.query('root.something', root_layer_data)


class TestDictLayer:

    def test_create(self, root_layer_data):
        layer = confrigulator.DictLayer('dict_layer', data=root_layer_data)
        assert layer.data == root_layer_data
        assert layer.name == 'dict_layer'
        assert layer.dirty == False
        assert layer.writable == False
        assert isinstance(layer.query_engine, confrigulator.DPathQueryEngine)

    def test_exists(self, root_layer):
        assert root_layer.exists('root')
        assert root_layer.exists('other') == False
        assert root_layer.exists('') == False

    def test_get(self, root_layer):
        assert root_layer.get('root.root_branch_dict.root_branch_value') == 'original_value'
