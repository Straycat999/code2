# flake8: noqa

import pytest
from os import environ
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import transaction


@pytest.fixture(scope="session")
@pytest.mark.django_db
def host():
    return environ.get("BS_HOST_URL")


@pytest.fixture(scope="module")
@pytest.mark.django_db(transaction=True)
def organization():
    organization, __ = apps.get_model('organization.Organization').objects.update_or_create(
        id='d16b224d-f2cf-4014-aebd-54d5d3a64aef',
        defaults=dict(
            name_full='Полное название тестовой организации',
            name_short='Краткое тестовое',
            tin='12345678',
        )
    )
    yield organization


@pytest.fixture(scope="module")
@pytest.mark.django_db
def user_test_role():
    with transaction.atomic():
        group_permissions, __ = apps.get_model('permit.GroupPermission').objects.update_or_create(
            slug='user_test_group_permissions',
            defaults=dict(
                name='Группа юзера user_test',
            )
        )
        group_permissions.permissions.set([
            apps.get_model('permit.Permission').objects.get_or_create(slug='place.place.item.add.all.all')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='place.place.item.view.org_owner.draft')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='place.place.item.change.org_owner.draft')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='place.place.item.delete.org_owner.draft')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='place.place.item.view.org_owner.test_1')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='place.place.item.change.org_owner.test_1')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='place.place.item.delete.org_owner.test_1')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='place.place.item.transit.org_owner.all.test_1')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='place.place.field.view.org_owner.draft.address.disable')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='place.place.field.add.all.all.address.notnull')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='place.place.field.change.all.all.address.notnull')[0],

            apps.get_model('permit.Permission').objects.get_or_create(slug='authing.user.item.view.all')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='permit.role.item.view.all')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='place.place_operation.item.add.all.all')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='place.place_operation.item.change.org_owner.draft')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='place.place_operation.item.view.org_owner.draft')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='place.place_operation.field.add.all.all.name.notnull')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='file_upload.file_upload.item.view.org_owner')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='file_upload.file_upload.item.add.org_owner')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='file_upload.file_upload.item.change.org_owner')[0],

            apps.get_model('permit.Permission').objects.get_or_create(slug='document.stencil.item.add.all.all')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='document.stencil.item.view.all')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='document.document.item.add.all.all')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='document.document.item.view.org_owner')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='document.document.item.change.org_owner')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='document.document.item.delete.org_owner')[0],

            apps.get_model('permit.Permission').objects.get_or_create(slug='organization.organization_info.item.add.all.all')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='organization.organization_info.item.view.org_owner.draft')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='organization.organization_info.item.change.org_owner.draft')[0],
            apps.get_model('permit.Permission').objects.get_or_create(slug='organization.organization_info.item.delete.org_owner.draft')[0],

            apps.get_model('permit.Permission').objects.get_or_create(slug='document.signature.item.view.org_owner.all')[0],
        ])

        role, __ = apps.get_model('permit.Role').objects.update_or_create(
            slug='user_test_role',
            defaults=dict(
                name='Роль юзера user_test',
            )
        )
        role.groups_permission.set([group_permissions])

    yield role


@pytest.fixture(scope="module")
@pytest.mark.django_db
def user_test(organization, user_test_role):
    with transaction.atomic():
        if not (user := get_user_model().objects.filter(username='user_test').first()):
            user = get_user_model().objects.create_user('user_test', password='qwer1234', organization=organization)
        user.roles.clear()
        user.roles.add(user_test_role)
    yield user


@pytest.fixture(scope="module")
@pytest.mark.django_db
def user_token(user_test):
    yield {'Authorization': f'Bearer {user_test.jwt_build()}'}


@pytest.fixture(scope="module")
@pytest.mark.django_db
def region():
    region, __ = apps.get_model('classifier.Region').objects.update_or_create(
        name='Регион 1',
        defaults=dict(
            oktmo='11111111111',
            code='MSK',
            code_letter='МСК',
        )
    )
    yield region
    # region.delete()


@pytest.fixture(scope="module")
@pytest.mark.django_db
def municipality(region):
    municipality, __ = apps.get_model('classifier.Municipality').objects.update_or_create(
        name='Муниципалитет 1',
        defaults=dict(
            oktmo='123456789',
            region=region,
        )
    )
    yield municipality
    # municipality.delete()


@pytest.fixture(scope="module")
@pytest.mark.django_db
def status_draft():
    yield apps.get_model('statusy.Status').get_status_initial()
