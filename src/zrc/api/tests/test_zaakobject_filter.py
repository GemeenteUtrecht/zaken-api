from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.constants import ZaakobjectTypes
from vng_api_common.tests import JWTAuthMixin, get_operation_url, get_validation_errors

from zrc.datamodel.tests.factories import ZaakObjectFactory


class ZaakObjectFilterTestCase(JWTAuthMixin, APITestCase):

    heeft_alle_autorisaties = True

    def test_filter_type(self):
        zaakobject1 = ZaakObjectFactory.create(object_type=ZaakobjectTypes.besluit)
        zaakobject2 = ZaakObjectFactory.create(object_type=ZaakobjectTypes.adres)
        zaakobject1_url = get_operation_url("zaakobject_read", uuid=zaakobject1.uuid)
        url = get_operation_url("zaakobject_list")

        response = self.client.get(url, {"objectType": ZaakobjectTypes.besluit})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["url"], f"http://testserver{zaakobject1_url}")

    def test_filter_zaak(self):
        zaakobject1 = ZaakObjectFactory.create()
        zaakobject2 = ZaakObjectFactory.create()
        zaak = zaakobject1.zaak
        zaak_url = get_operation_url("zaak_read", uuid=zaak.uuid)
        zaakobject1_url = get_operation_url("zaakobject_read", uuid=zaakobject1.uuid)
        url = get_operation_url("zaakobject_list")

        response = self.client.get(url, {"zaak": zaak_url})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["url"], f"http://testserver{zaakobject1_url}")

    def test_filter_object(self):
        zaakobject1 = ZaakObjectFactory.create(object="http://example.com/objects/1")
        zaakobject2 = ZaakObjectFactory.create(object="http://example.com/objects/2")
        zaakobject1_url = get_operation_url("zaakobject_read", uuid=zaakobject1.uuid)
        url = get_operation_url("zaakobject_list")

        response = self.client.get(url, {"object": "http://example.com/objects/1"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["url"], f"http://testserver{zaakobject1_url}")

    def test_validate_unknown_query_params(self):
        ZaakObjectFactory.create_batch(2, object="http://example.com/objects/1")
        url = get_operation_url("zaakobject_list")

        response = self.client.get(url, {"someparam": "somevalue"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "nonFieldErrors")
        self.assertEqual(error["code"], "unknown-parameters")
