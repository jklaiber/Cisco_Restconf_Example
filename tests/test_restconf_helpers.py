import base64

import pytest
import requests_mock
from requests import HTTPError

from restconf_helpers import RestconfRequestHelper, RestconfFormat


def test_get_xml_headers_without_additional_headers():
    composite_headers = RestconfRequestHelper().get_headers(format=RestconfFormat.XML, headers=None)
    assert composite_headers == {'Content-Type': 'application/yang-data+xml',
                                 'Accept': 'application/yang-data+xml, application/yang-data.errors+xml'}


def test_get_json_headers_without_additional_headers():
    composite_headers = RestconfRequestHelper().get_headers(format=RestconfFormat.JSON, headers=None)
    assert composite_headers == {'Content-Type': 'application/yang-data+json',
                                 'Accept': 'application/yang-data+json, application/yang-data.errors+json'}


def test_get_headers_with_additional_headers_contains_additional_header():
    composite_headers = RestconfRequestHelper().get_headers(format=RestconfFormat.XML,
                                                            headers={'some_header': 'test_value'})
    assert composite_headers['some_header'] == 'test_value'


def test_get_xml_headers_with_additional_headers_contains_base_header():
    composite_headers = RestconfRequestHelper().get_headers(format=RestconfFormat.XML,
                                                            headers={'some_header': 'test_value'})
    assert composite_headers['Content-Type'] == 'application/yang-data+xml'
    assert composite_headers['Accept'] == 'application/yang-data+xml, application/yang-data.errors+xml'


def test_get_json_headers_with_additional_headers_contains_base_header():
    composite_headers = RestconfRequestHelper().get_headers(format=RestconfFormat.JSON,
                                                            headers={'some_header': 'test_value'})
    assert composite_headers['Content-Type'] == 'application/yang-data+json'
    assert composite_headers['Accept'] == 'application/yang-data+json, application/yang-data.errors+json'


def test_get_dispatches_request():
    with requests_mock.Mocker() as m:
        m.get('http://test.com', text='test_response')
        response = RestconfRequestHelper().get(url='http://test.com', username='test', password='test')
        assert response == 'test_response'


def test_get_sets_headers():
    with requests_mock.Mocker() as m:
        m.get('http://test.com', text='test_response', request_headers=RestconfRequestHelper.headers_xml)
        response = RestconfRequestHelper().get(url='http://test.com', username='test_user', password='test_password',
                                               restconf_format=RestconfFormat.XML)
        assert response == 'test_response'


def test_get_raises_exception():
    with pytest.raises(HTTPError):
        with requests_mock.Mocker() as m:
            m.get('http://test.com', status_code=400, text='test_response',
                  request_headers=RestconfRequestHelper.headers_xml)
            response = RestconfRequestHelper().get(url='http://test.com', username='test_user',
                                                   password='test_password',
                                                   restconf_format=RestconfFormat.XML)
