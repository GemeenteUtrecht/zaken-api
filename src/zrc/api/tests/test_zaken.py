import unittest

from django.contrib.gis.geos import Point
from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase
from zds_schema.mocks import ZTCMockClient
from zds_schema.tests import JWTScopesMixin, generate_jwt

from zrc.datamodel.tests.factories import StatusFactory, ZaakFactory
from zrc.tests.utils import isodatetime, utcdatetime

from ..scopes import (
    SCOPE_STATUSSEN_TOEVOEGEN, SCOPE_ZAKEN_ALLES_LEZEN, SCOPE_ZAKEN_CREATE
)
from .utils import reverse


@override_settings(LINK_FETCHER='zds_schema.mocks.link_fetcher_200')
class ApiStrategyTests(JWTScopesMixin, APITestCase):

    scopes = [
        SCOPE_ZAKEN_CREATE,
        SCOPE_ZAKEN_ALLES_LEZEN,
    ]
    zaaktypes = ['https://example.com/foo/bar']

    @unittest.expectedFailure
    def test_api_10_lazy_eager_loading(self):
        raise NotImplementedError

    @unittest.expectedFailure
    def test_api_11_expand_nested_resources(self):
        raise NotImplementedError

    @unittest.expectedFailure
    def test_api_12_subset_fields(self):
        raise NotImplementedError

    def test_api_44_crs_headers(self):
        # We wijken bewust af - EPSG:4326 is de standaard projectie voor WGS84
        # De andere opties in de API strategie lijken in de praktijk niet/nauwelijks
        # gebruikt te worden, en zien er vreemd uit t.o.v. wel courant gebruikte
        # opties.
        zaak = ZaakFactory.create(zaakgeometrie=Point(4.887990, 52.377595))  # LONG LAT
        url = reverse('zaak-detail', kwargs={'uuid': zaak.uuid})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_412_PRECONDITION_FAILED)

        response = self.client.get(url, HTTP_ACCEPT_CRS='dummy')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

        response = self.client.get(url, HTTP_ACCEPT_CRS='EPSG:4326')
        self.assertEqual(
            response['Content-Crs'],
            'EPSG:4326'
        )

    def test_api_51_status_codes(self):
        with self.subTest(crud='create'):
            url = reverse('zaak-list')

            response = self.client.post(url, {
                'zaaktype': 'https://example.com/foo/bar',
                'bronorganisatie': '517439943',
                'verantwoordelijkeOrganisatie': '517439943',
                'registratiedatum': '2018-06-11',
                'startdatum': '2018-06-11',
            }, HTTP_ACCEPT_CRS='EPSG:4326')

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response['Location'], response.data['url'])

        with self.subTest(crud='read'):
            response_detail = self.client.get(
                response.data['url'],
                HTTP_ACCEPT_CRS='EPSG:4326'
            )
            self.assertEqual(response_detail.status_code, status.HTTP_200_OK)


class ZakenTests(JWTScopesMixin, APITestCase):

    scopes = [
        SCOPE_ZAKEN_CREATE,
        SCOPE_ZAKEN_ALLES_LEZEN,
    ]

    @override_settings(
        LINK_FETCHER='zds_schema.mocks.link_fetcher_200',
        ZDS_CLIENT_CLASS='zds_schema.mocks.MockClient'
    )
    def test_zaak_afsluiten(self):
        zaak = ZaakFactory.create()
        zaak_url = reverse('zaak-detail', kwargs={'uuid': zaak.uuid})
        status_list_url = reverse('status-list')
        token = generate_jwt([SCOPE_STATUSSEN_TOEVOEGEN])
        self.client.credentials(HTTP_AUTHORIZATION=token)

        # Validate StatusTypes from Mock client
        ztc_mock_client = ZTCMockClient()

        status_type_1 = ztc_mock_client.retrieve('statustype', uuid=1)
        self.assertFalse(status_type_1['isEindstatus'])

        status_type_2 = ztc_mock_client.retrieve('statustype', uuid=2)
        self.assertTrue(status_type_2['isEindstatus'])

        # Set initial status
        response = self.client.post(status_list_url, {
            'zaak': zaak_url,
            'statusType': 'http://example.com/ztc/api/v1/catalogussen/1/zaaktypen/1/statustypen/1',
            'datumStatusGezet': isodatetime(2018, 10, 1, 10, 00, 00),
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

        zaak.refresh_from_db()
        self.assertIsNone(zaak.einddatum)

        # Set eindstatus
        datum_status_gezet = utcdatetime(2018, 10, 22, 10, 00, 00)
        response = self.client.post(status_list_url, {
            'zaak': zaak_url,
            'statusType': 'http://example.com/ztc/api/v1/catalogussen/1/zaaktypen/1/statustypen/2',
            'datumStatusGezet': datum_status_gezet.isoformat(),
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

        zaak.refresh_from_db()
        self.assertEqual(zaak.einddatum, datum_status_gezet.date())

    @override_settings(
        LINK_FETCHER='zds_schema.mocks.link_fetcher_200',
        ZDS_CLIENT_CLASS='zds_schema.mocks.MockClient'
    )
    def test_zaak_heropen_reset_einddatum(self):
        token = generate_jwt([SCOPE_STATUSSEN_TOEVOEGEN])
        self.client.credentials(HTTP_AUTHORIZATION=token)
        zaak = ZaakFactory.create(einddatum='2019-01-07')
        StatusFactory.create(
            zaak=zaak,
            status_type='http://example.com/ztc/api/v1/catalogussen/1/zaaktypen/1/statustypen/2',
            datum_status_gezet='2019-01-07T12:51:41+0000',
        )
        zaak_url = reverse('zaak-detail', kwargs={'uuid': zaak.uuid})
        status_list_url = reverse('status-list')

        # Set status other than eindstatus
        datum_status_gezet = utcdatetime(2019, 1, 7, 12, 53, 25)
        response = self.client.post(status_list_url, {
            'zaak': zaak_url,
            'statusType': 'http://example.com/ztc/api/v1/catalogussen/1/zaaktypen/1/statustypen/1',
            'datumStatusGezet': datum_status_gezet.isoformat(),
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

        zaak.refresh_from_db()
        self.assertIsNone(zaak.einddatum)

    @override_settings(
        LINK_FETCHER='zds_schema.mocks.link_fetcher_200',
        ZDS_CLIENT_CLASS='zds_schema.mocks.MockClient'
    )
    def test_enkel_initiele_status_met_scope_aanmaken(self):
        """
        Met de scope zaken.aanmaken mag je enkel een status aanmaken als er
        nog geen status was.
        """
        zaak = ZaakFactory.create()
        zaak_url = reverse('zaak-detail', kwargs={'uuid': zaak.uuid})
        status_list_url = reverse('status-list')

        # initiele status
        response = self.client.post(status_list_url, {
            'zaak': zaak_url,
            'statusType': 'http://example.com/ztc/api/v1/catalogussen/1/zaaktypen/1/statustypen/1',
            'datumStatusGezet': isodatetime(2018, 10, 1, 10, 00, 00),
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # extra status - mag niet, onafhankelijk van de data
        response = self.client.post(status_list_url, {
            'zaak': zaak_url,
            'statusType': 'http://example.com/ztc/api/v1/catalogussen/1/zaaktypen/1/statustypen/1',
            'datumStatusGezet': isodatetime(2018, 10, 1, 10, 00, 00),
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(zaak.status_set.count(), 1)
