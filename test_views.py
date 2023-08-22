# flake8: noqa

import uuid

import pytest
import requests
from constance.test import override_config  # noqa
from django.apps import apps
import json
import pprint

from django.apps import apps
from django.test import override_settings

import pytest
from constance.test import override_config   # noqa

from promotion.models import Promotion
from tests.test_authing.factories import UserFactory
from tests.test_classifier.factories import MunicipalityFactory
from tests.test_promotion.factories import PromotionFactory

from fastapi.testclient import TestClient

from bazis.core.app import app

# api_client = TestClient(app)

@pytest.fixture
@pytest.mark.django_db
def place_200(municipality, organization, user_test, status_draft):
    place, __ = apps.get_model('place.Place').objects.update_or_create(
        id='d16b224d-f2cf-4014-aebd-53d5d3a64aef',
        defaults=dict(
            address='ул. Тестовая д.1',
            name='ОИ 2',
            municipality=municipality,
            org_owner=organization,
            author=user_test,
            status=status_draft,
        )
    )
    yield place


@pytest.fixture
@pytest.mark.django_db
def place_403(municipality, status_draft):
    place, __ = apps.get_model('place.Place').objects.update_or_create(
        id='d16b224d-f2cf-4015-aebd-55d5d3a64aef',
        defaults=dict(
            name='ОИ 3',
            municipality=municipality,
            status=status_draft,
        )
    )
    yield place

@override_settings(DEBUG=True)
@pytest.mark.django_db
def test_user_list_forbidden(api_client):
    response = api_client.get(f'/api/web/v1/authing/user/')
    assert response.status_code == 401

# @override_settings(DEBUG=False)
# @pytest.mark.django_db(transaction=True)
# def test_place_403(api_client):
#     response = api_client.get(f'/api/web/v1/negotiation/waste_position/')
#     assert response.status_code == 403

@override_settings(DEBUG=True)
@pytest.mark.transactional_db
def test_place_200(api_client, user_token, place_200):
    response = api_client.get(f'/api/web/v1/place/place/{place_200.id}/', headers=user_token)
    data_json = response.json()
    assert response.status_code == 200
    assert data_json['data']['attributes'].get('address') is None

@override_settings(DEBUG=True)
@pytest.mark.transactional_db
def test_place_create_required_name(api_client, user_token):
    response = api_client.post('/api/web/v1/place/place/', json={
        "data": {
            "type": "place.place",
            "attributes": {
                "oktmo": "тестовый oktmo",
                "fias": "тестовый fias"
            },
            "relationships": {}
        }
    }, headers=user_token)
    data_json = response.json()
    assert response.status_code == 422
    assert data_json['detail'][0]['loc'][-1] == 'name' and data_json['detail'][0]['type'] == 'value_error.missing'

@override_settings(DEBUG=True)
@pytest.mark.django_db(transaction=True)
def test_place_create_address_null(api_client, user_token):
    response = api_client.post('/api/web/v1/place/place/', json={
        "data": {
            "type": "place.place",
            "attributes": {
                "address": None,
                "name": "Тестовое имя",
                "oktmo": "тестовый oktmo",
                "fias": "тестовый fias"
            },
            "relationships": {}
        }
    }, headers=user_token)
    data_json = response.json()

    assert response.status_code == 422

    error = data_json['errors'][0]

    assert error['source']['pointer'] == 'data/attributes/address' and error['code'] == 'ERR_VALIDATE'

@override_settings(DEBUG=True)
@pytest.mark.django_db(transaction=True)
def test_place_create_with_nested_place_null(api_client, user_token):
    place_id = 'aaa11111-f2cf-4014-aebd-53d5d3a64aef'

    apps.get_model('place.place').objects.filter(id=place_id).delete()

    response = api_client.post('/api/web/v1/place/place/?include=operations', json={
        "data": {
            "id": place_id,
            "type": "place.place",
            "action": "add",
            "attributes": {
                "address": "Тестовый адрес aaa11111",
                "name": "Тестовое имя aaa11111",
                "oktmo": "тестовый oktmo",
                "fias": "тестовый fias"
            },
            "relationships": {}
        },
        "included": [
            {
                "type": "place.place_operation",
                "action": "add",
                "attributes": {
                    "name": None,
                    "type": "disinfection",
                },
                "relationships": {
                    "place": {
                        "data": {
                            "id": place_id,
                            "type": "place.place"
                        },
                    },
                }
            },
        ]
    }, headers=user_token)
    data_json = response.json()
    assert response.status_code == 422

@override_settings(DEBUG=True)
@pytest.mark.django_db(transaction=True)
def test_place_create_with_nested(api_client, user_token):
    place_id = 'aaa11111-f2cf-4014-aebd-53d5d3a64aef'

    apps.get_model('place.place').objects.filter(id=place_id).delete()

    response = api_client.post('/api/web/v1/place/place/?include=operations', json={
        "data": {
            "id": place_id,
            "type": "place.place",
            "action": "add",
            "attributes": {
                "address": "Тестовый адрес aaa11111",
                "name": "Тестовое имя aaa11111",
                "oktmo": "тестовый oktmo",
                "fias": "тестовый fias"
            },
            "relationships": {}
        },
        "included": [
            {
                "type": "place.place_operation",
                "action": "add",
                "attributes": {
                    "name": "Тестовая технология для aaa11111",
                    "type": "disinfection",
                },
                "relationships": {
                    "place": {
                        "data": {
                            "id": place_id,
                            "type": "place.place"
                        },
                    },
                }
            },
        ]
    }, headers=user_token)
    data_json = response.json()

    assert response.status_code == 201

@override_settings(DEBUG=True)
@pytest.mark.django_db(transaction=True)
def test_place_update_with_nested(api_client, user_token):
    place_id = 'aaa11111-f2cf-4014-aebd-53d5d3a64aef'

    # apps.get_model('place.place').objects.filter(id=place_id).delete()

    response = api_client.patch(f'/api/web/v1/place/place/{place_id}/?include=operations', json={
        "data": {
            "id": place_id,
            "type": "place.place",
            "action": "change",
            "attributes": {
                "address": "Тестовый адрес aaa11111",
                "name": str(uuid.uuid4()),
                "oktmo": "тестовый oktmo",
                "fias": "тестовый fias"
            },
            "relationships": {}
        },
        "included": [
            {
                "id": '5e0a842d-79d1-4927-a9bb-89dc2082d41d',
                "type": "place.place_operation",
                "action": "change",
                "attributes": {
                    "name": str(uuid.uuid4()),
                    "type": "disinfection",
                },
                "relationships": {
                    "place": {
                        "data": {
                            "id": place_id,
                            "type": "place.place"
                        },
                    },
                }
            },
            {
                "type": "place.place_operation",
                "action": "add",
                "attributes": {
                    "name": str(uuid.uuid4()),
                    "type": "disinfection",
                },
                "relationships": {
                    "place": {
                        "data": {
                            "id": place_id,
                            "type": "place.place"
                        },
                    },
                }
            },
        ]
    }, headers=user_token)
    data_json = response.json()

    assert response.status_code == 200

@override_settings(DEBUG=True)
@pytest.mark.django_db(transaction=True)
def test_place_list_success(api_client, user_token):
    response = api_client.get('/api/web/v1/place/place/', headers=user_token)
    data_json = response.json()
    assert response.status_code == 200
    assert len(data_json['data']) > 0

@override_settings(DEBUG=True)
@pytest.mark.django_db(transaction=True)
def test_place_update_geo(api_client, user_token):
    place_id = 'aaa11111-f2cf-4014-aebd-53d5d3a64aef'

    response = api_client.patch(f'/api/web/v1/place/place/{place_id}/', json={
        "data": {
            "id": place_id,
            "type": "place.place",
            "action": "change",
            "attributes": {
                "point": {
                    "type": "Point",
                    "coordinates": [
                        34.949,
                        51.28
                    ]
                },
            },
            "relationships": {}
        }
    }, headers=user_token)
    data_json = response.json()

    print('data_json:', data_json)

    assert response.status_code == 200
