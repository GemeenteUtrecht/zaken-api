import datetime

from django.test import override_settings
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.constants import Archiefnominatie
from vng_api_common.tests import JWTAuthMixin, get_operation_url, reverse

from zrc.api.scopes import (
    SCOPE_STATUSSEN_TOEVOEGEN, SCOPE_ZAKEN_BIJWERKEN,
    SCOPE_ZAKEN_GEFORCEERD_BIJWERKEN, SCOPEN_ZAKEN_HEROPENEN
)
from zrc.datamodel.constants import BetalingsIndicatie
from zrc.datamodel.tests.factories import ZaakFactory
from zrc.tests.utils import ZAAK_WRITE_KWARGS

CATALOGUS = 'https://example.com/ztc/api/v1/catalogus/878a3318-5950-4642-8715-189745f91b04'
ZAAKTYPE = f'{CATALOGUS}/zaaktypen/283ffaf5-8470-457b-8064-90e5728f413f'
STATUS_TYPE = f'{ZAAKTYPE}/statustypen/1'


@override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
class ZaakClosedTests(JWTAuthMixin, APITestCase):
    scopes = [SCOPE_ZAKEN_BIJWERKEN]
    zaaktype = ZAAKTYPE

    def test_update_zaak_open(self):
        zaak = ZaakFactory.create(
            betalingsindicatie=BetalingsIndicatie.geheel,
            zaaktype=ZAAKTYPE
        )
        url = reverse(zaak)

        response = self.client.patch(url, {
            'betalingsindicatie': BetalingsIndicatie.nvt,
        }, **ZAAK_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        self.assertEqual(response.json()['betalingsindicatie'], BetalingsIndicatie.nvt)
        zaak.refresh_from_db()
        self.assertEqual(zaak.betalingsindicatie, BetalingsIndicatie.nvt)

    def test_update_zaak_closed_not_allowed(self):
        zaak = ZaakFactory.create(
            einddatum=timezone.now(),
            zaaktype=ZAAKTYPE
        )
        url = reverse(zaak)

        response = self.client.patch(url, {
            'betalingsindicatie': BetalingsIndicatie.nvt,
        }, **ZAAK_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_zaak_closed_allowed(self):
        zaak = ZaakFactory.create(
            einddatum=timezone.now(),
            zaaktype=ZAAKTYPE
        )
        url = reverse(zaak)

        self.autorisatie.scopes = [SCOPE_ZAKEN_GEFORCEERD_BIJWERKEN]
        self.autorisatie.save()

        response = self.client.patch(url, {
            'betalingsindicatie': BetalingsIndicatie.nvt,
        }, **ZAAK_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

    @override_settings(
        ZDS_CLIENT_CLASS='vng_api_common.mocks.MockClient'
    )
    def test_reopen_zaak_allowed(self):
        zaak = ZaakFactory.create(
            einddatum=timezone.now(),
            archiefactiedatum='2020-01-01',
            archiefnominatie=Archiefnominatie.blijvend_bewaren,
            zaaktype=ZAAKTYPE
        )
        status_create_url = get_operation_url('status_create')
        self.autorisatie.scopes = [SCOPEN_ZAKEN_HEROPENEN]
        self.autorisatie.save()

        data = {
            'zaak': reverse(zaak),
            'statusType': STATUS_TYPE,
            'datumStatusGezet': datetime.datetime.now().isoformat(),
        }
        response = self.client.post(status_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        zaak.refresh_from_db()
        self.assertIsNone(zaak.einddatum)
        self.assertIsNone(zaak.archiefactiedatum)
        self.assertIsNone(zaak.archiefnominatie)

    @override_settings(
        ZDS_CLIENT_CLASS='vng_api_common.mocks.MockClient'
    )
    def test_reopen_zaak_not_allowed(self):
        zaak = ZaakFactory.create(
            einddatum=timezone.now(),
            zaaktype=ZAAKTYPE
        )
        status_create_url = get_operation_url('status_create')
        self.autorisatie.scopes = [SCOPE_STATUSSEN_TOEVOEGEN]
        self.autorisatie.save()

        data = {
            'zaak': reverse(zaak),
            'statusType': STATUS_TYPE,
            'datumStatusGezet': datetime.datetime.now().isoformat(),
        }
        response = self.client.post(status_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        data = response.json()
        self.assertEqual(data['detail'], 'Reopening a closed case with current scope is forbidden')
