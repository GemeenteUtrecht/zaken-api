from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.constants import ZaakobjectTypes
from vng_api_common.tests import (
    JWTAuthMixin, get_operation_url, get_validation_errors
)

from zrc.datamodel.models import (
    Adres, Huishouden, KadastraleOnroerendeZaak, Medewerker, NatuurlijkPersoon,
    NietNatuurlijkPersoon, Overige, TerreinGebouwdObject, WozDeelobject,
    WozObject, WozWaarde, ZaakObject, ZakelijkRecht,
    ZakelijkRechtHeeftAlsGerechtigde
)
from zrc.datamodel.tests.factories import ZaakFactory, ZaakObjectFactory

from ..serializers import (
    ObjectZakelijkRechtSerializer, ZakelijkRechtHeeftAlsGerechtigdeSerializer
)

OBJECT = 'http://example.org/api/zaakobjecten/8768c581-2817-4fe5-933d-37af92d819dd'


class ZaakObjectBaseTestCase(JWTAuthMixin, APITestCase):
    """
    general cases for zaakobject without object_identificatie
    """

    heeft_alle_autorisaties = True

    def test_read_zaakobject_without_identificatie(self):
        zaak = ZaakFactory.create()
        zaakobject = ZaakObjectFactory.create(
            zaak=zaak,
            object=OBJECT,
            type=ZaakobjectTypes.besluit
        )
        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        url = get_operation_url('zaakobject_read', uuid=zaakobject.uuid)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            data,
            {
                'url': f'http://testserver{url}',
                'zaak': f'http://testserver{zaak_url}',
                'object': OBJECT,
                'type': ZaakobjectTypes.besluit,
                'relatieomschrijving': '',
            }
        )

    def test_create_zaakobject_without_identificatie(self):
        url = get_operation_url('zaakobject_create')
        zaak = ZaakFactory.create()
        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        data = {
            'zaak': f'http://testserver{zaak_url}',
            'object': OBJECT,
            'type': ZaakobjectTypes.besluit,
            'relatieomschrijving': 'test',
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ZaakObject.objects.count(), 1)

        zaakobject = ZaakObject.objects.get()

        self.assertEqual(zaakobject.object, OBJECT)

    def test_create_rol_fail_validation(self):
        url = get_operation_url('zaakobject_create')
        zaak = ZaakFactory.create()
        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        data = {
            'zaak': f'http://testserver{zaak_url}',
            'type': ZaakobjectTypes.besluit,
            'relatieomschrijving': 'test',
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        validation_error = get_validation_errors(response, 'nonFieldErrors')
        self.assertEqual(validation_error['code'], 'invalid-zaakobject')


class ZaakObjectAdresTestCase(JWTAuthMixin, APITestCase):
    """
    check polymorphism with simple child object Adres
    """

    heeft_alle_autorisaties = True

    def test_read_zaakobject_adres(self):

        zaak = ZaakFactory.create()
        zaakobject = ZaakObjectFactory.create(
            zaak=zaak,
            object='',
            type=ZaakobjectTypes.adres
        )
        Adres.objects.create(
            zaakobject=zaakobject,
            identificatie='123456',
            wpl_woonplaats_naam='test city',
            gor_openbare_ruimte_naam='test space',
            huisnummer=1
        )

        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        url = get_operation_url('zaakobject_read', uuid=zaakobject.uuid)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            data,
            {
                'url': f'http://testserver{url}',
                'zaak': f'http://testserver{zaak_url}',
                'object': '',
                'relatieomschrijving': '',
                'type': ZaakobjectTypes.adres,
                'objectIdentificatie': {
                    'identificatie': '123456',
                    'wplWoonplaatsNaam': 'test city',
                    'gorOpenbareRuimteNaam': 'test space',
                    'huisnummer': 1,
                    'huisletter': '',
                    'huisnummertoevoeging': '',
                    'postcode': ''
                }
            }
        )

    def test_create_zaakobject_adres(self):
        url = get_operation_url('zaakobject_create')
        zaak = ZaakFactory.create()
        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        data = {
            'zaak': f'http://testserver{zaak_url}',
            'type': ZaakobjectTypes.adres,
            'relatieomschrijving': 'test',
            'objectIdentificatie': {
                'identificatie': '123456',
                'wplWoonplaatsNaam': 'test city',
                'gorOpenbareRuimteNaam': 'test space',
                'huisnummer': 1,
                'huisletter': '',
                'huisnummertoevoeging': '',
                'postcode': ''
            }
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ZaakObject.objects.count(), 1)
        self.assertEqual(Adres.objects.count(), 1)

        zaakobject = ZaakObject.objects.get()
        adres = Adres.objects.get()

        self.assertEqual(zaakobject.adres, adres)
        self.assertEqual(adres.identificatie, '123456')


class ZaakObjectHuishoudenTestCase(JWTAuthMixin, APITestCase):
    """
    check polymorphism for Huishouden object with nesting
    """
    heeft_alle_autorisaties = True

    def test_read_zaakobject_huishouden(self):
        zaak = ZaakFactory.create()
        zaakobject = ZaakObjectFactory.create(
            zaak=zaak,
            object='',
            type=ZaakobjectTypes.huishouden
        )

        huishouden = Huishouden.objects.create(
            zaakobject=zaakobject,
            nummer='123456',
        )
        TerreinGebouwdObject.objects.create(
            identificatie='1',
            num_identificatie='1',
            oao_identificatie='a',
            wpl_woonplaats_naam='test city',
            gor_openbare_ruimte_naam='test space',
            aoa_huisnummer='11',
            ogo_locatie_aanduiding='test',
            huishouden=huishouden
        )

        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        url = get_operation_url('zaakobject_read', uuid=zaakobject.uuid)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            data,
            {
                'url': f'http://testserver{url}',
                'zaak': f'http://testserver{zaak_url}',
                'object': '',
                'relatieomschrijving': '',
                'type': ZaakobjectTypes.huishouden,
                'objectIdentificatie': {
                    'nummer': '123456',
                    'isGehuisvestIn': {
                        'identificatie': '1',
                        'adresAanduidingGrp': {
                            'numIdentificatie': '1',
                            'oaoIdentificatie': 'a',
                            'wplWoonplaatsNaam': 'test city',
                            'gorOpenbareRuimteNaam': 'test space',
                            'aoaPostcode': '',
                            'aoaHuisnummer': 11,
                            'aoaHuisletter': '',
                            'aoaHuisnummertoevoeging': '',
                            'ogoLocatieAanduiding': 'test'
                        }
                    }
                }
            }
        )

    def test_create_zaakobject_huishouden(self):
        url = get_operation_url('zaakobject_create')
        zaak = ZaakFactory.create()
        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        data = {
            'zaak': f'http://testserver{zaak_url}',
            'type': ZaakobjectTypes.huishouden,
            'relatieomschrijving': 'test',
            'objectIdentificatie': {
                'nummer': '123456',
                'isGehuisvestIn': {
                    'identificatie': '1',
                    'adresAanduidingGrp': {
                        'numIdentificatie': '1',
                        'oaoIdentificatie': 'a',
                        'wplWoonplaatsNaam': 'test city',
                        'gorOpenbareRuimteNaam': 'test space',
                        'aoaPostcode': '1010',
                        'aoaHuisnummer': 11,
                        'aoaHuisletter': 'a',
                        'aoaHuisnummertoevoeging': 'test',
                        'ogoLocatieAanduiding': 'test'
                    }
                }
            }
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ZaakObject.objects.count(), 1)
        self.assertEqual(Huishouden.objects.count(), 1)

        zaakobject = ZaakObject.objects.get()
        huishouden = Huishouden.objects.get()

        self.assertEqual(zaakobject.huishouden, huishouden)
        self.assertEqual(huishouden.nummer, '123456')
        self.assertEqual(huishouden.is_gehuisvest_in.oao_identificatie, 'a')


class ZaakObjectMedewerkerTestCase(JWTAuthMixin, APITestCase):
    """
    check polyphormism for Rol-related object Medewerker
    """
    heeft_alle_autorisaties = True

    def test_read_zaakobject_medewerker(self):
        zaak = ZaakFactory.create()
        zaakobject = ZaakObjectFactory.create(
            zaak=zaak,
            object='',
            type=ZaakobjectTypes.medewerker
        )
        Medewerker.objects.create(
            zaakobject=zaakobject,
            identificatie='123456',
            achternaam='Jong',
            voorletters='J',
            voorvoegsel_achternaam='van'
        )

        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        url = get_operation_url('zaakobject_read', uuid=zaakobject.uuid)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            data,
            {
                'url': f'http://testserver{url}',
                'zaak': f'http://testserver{zaak_url}',
                'object': '',
                'relatieomschrijving': '',
                'type': ZaakobjectTypes.medewerker,
                'objectIdentificatie': {
                    'identificatie': '123456',
                    'achternaam': 'Jong',
                    'voorletters': 'J',
                    'voorvoegselAchternaam': 'van'
                }
            }
        )

    def test_create_zaakobject_medewerker(self):
        url = get_operation_url('zaakobject_create')
        zaak = ZaakFactory.create()
        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        data = {
            'zaak': f'http://testserver{zaak_url}',
            'type': ZaakobjectTypes.medewerker,
            'relatieomschrijving': 'test',
            'objectIdentificatie': {
                'identificatie': '123456',
                'achternaam': 'Jong',
                'voorletters': 'J',
                'voorvoegselAchternaam': 'van'
            }
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ZaakObject.objects.count(), 1)
        self.assertEqual(Medewerker.objects.count(), 1)

        zaakobject = ZaakObject.objects.get()
        medewerker = Medewerker.objects.get()

        self.assertEqual(zaakobject.medewerker, medewerker)
        self.assertEqual(medewerker.identificatie, '123456')


class ZaakObjectTerreinGebouwdObjectTestCase(JWTAuthMixin, APITestCase):
    """
    check polyphormism for object TerreinGebouwdObject with GegevensGroep
    """
    heeft_alle_autorisaties = True

    def test_read_zaakobject_terreinGebouwdObject(self):
        zaak = ZaakFactory.create()
        zaakobject = ZaakObjectFactory.create(
            zaak=zaak,
            object='',
            type=ZaakobjectTypes.terreinGebouwdObject
        )

        TerreinGebouwdObject.objects.create(
            identificatie='12345',
            num_identificatie='1',
            oao_identificatie='a',
            wpl_woonplaats_naam='test city',
            gor_openbare_ruimte_naam='test space',
            aoa_huisnummer='11',
            ogo_locatie_aanduiding='test',
            zaakobject=zaakobject
        )

        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        url = get_operation_url('zaakobject_read', uuid=zaakobject.uuid)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            data,
            {
                'url': f'http://testserver{url}',
                'zaak': f'http://testserver{zaak_url}',
                'object': '',
                'relatieomschrijving': '',
                'type': ZaakobjectTypes.terreinGebouwdObject,
                'objectIdentificatie': {
                    'identificatie': '12345',
                    'adresAanduidingGrp': {
                        'numIdentificatie': '1',
                        'oaoIdentificatie': 'a',
                        'wplWoonplaatsNaam': 'test city',
                        'gorOpenbareRuimteNaam': 'test space',
                        'aoaPostcode': '',
                        'aoaHuisnummer': 11,
                        'aoaHuisletter': '',
                        'aoaHuisnummertoevoeging': '',
                        'ogoLocatieAanduiding': 'test'
                    }
                }
            }
        )

    def test_create_zaakobject_terreinGebouwdObject(self):
        url = get_operation_url('zaakobject_create')
        zaak = ZaakFactory.create()
        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        data = {
            'zaak': f'http://testserver{zaak_url}',
            'type': ZaakobjectTypes.terreinGebouwdObject,
            'relatieomschrijving': 'test',
            'objectIdentificatie': {
                'identificatie': '12345',
                'adresAanduidingGrp': {
                    'numIdentificatie': '1',
                    'oaoIdentificatie': 'a',
                    'wplWoonplaatsNaam': 'test city',
                    'gorOpenbareRuimteNaam': 'test space',
                    'aoaPostcode': '1010',
                    'aoaHuisnummer': 11,
                    'aoaHuisletter': 'a',
                    'aoaHuisnummertoevoeging': 'test',
                    'ogoLocatieAanduiding': 'test'
                }
            }
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ZaakObject.objects.count(), 1)
        self.assertEqual(TerreinGebouwdObject.objects.count(), 1)

        zaakobject = ZaakObject.objects.get()
        terrein_gebouwd = TerreinGebouwdObject.objects.get()

        self.assertEqual(zaakobject.terreingebouwdobject, terrein_gebouwd)
        self.assertEqual(terrein_gebouwd.identificatie, '12345')
        self.assertEqual(terrein_gebouwd.oao_identificatie, 'a')


class ZaakObjectWozObjectTestCase(JWTAuthMixin, APITestCase):
    """
    check polymorphism for WozObject object with GegevensGroep
    """
    heeft_alle_autorisaties = True

    def test_read_zaakobject_wozObject(self):
        zaak = ZaakFactory.create()
        zaakobject = ZaakObjectFactory.create(
            zaak=zaak,
            object='',
            type=ZaakobjectTypes.wozObject
        )

        WozObject.objects.create(
            woz_object_nummer='12345',
            oao_identificatie='a',
            wpl_woonplaats_naam='test city',
            gor_openbare_ruimte_naam='test space',
            aoa_huisnummer='11',
            locatie_omschrijving='test',
            zaakobject=zaakobject
        )

        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        url = get_operation_url('zaakobject_read', uuid=zaakobject.uuid)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            data,
            {
                'url': f'http://testserver{url}',
                'zaak': f'http://testserver{zaak_url}',
                'object': '',
                'relatieomschrijving': '',
                'type': ZaakobjectTypes.wozObject,
                'objectIdentificatie': {
                    'wozObjectNummer': '12345',
                    'aanduidingWozObject': {
                        'oaoIdentificatie': 'a',
                        'wplWoonplaatsNaam': 'test city',
                        'aoaPostcode': '',
                        'gorOpenbareRuimteNaam': 'test space',
                        'aoaHuisnummer': 11,
                        'aoaHuisletter': '',
                        'aoaHuisnummertoevoeging': '',
                        'locatieOmschrijving': 'test'
                    }
                }
            }
        )

    def test_create_zaakobject_wozObject(self):
        url = get_operation_url('zaakobject_create')
        zaak = ZaakFactory.create()
        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        data = {
            'zaak': f'http://testserver{zaak_url}',
            'type': ZaakobjectTypes.wozObject,
            'relatieomschrijving': 'test',
            'objectIdentificatie': {
                'wozObjectNummer': '12345',
                'aanduidingWozObject': {
                    'oaoIdentificatie': 'a',
                    'wplWoonplaatsNaam': 'test city',
                    'aoaPostcode': '',
                    'gorOpenbareRuimteNaam': 'test space',
                    'aoaHuisnummer': 11,
                    'aoaHuisletter': '',
                    'aoaHuisnummertoevoeging': '',
                    'locatieOmschrijving': 'test'
                }
            }
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ZaakObject.objects.count(), 1)
        self.assertEqual(WozObject.objects.count(), 1)

        zaakobject = ZaakObject.objects.get()
        wozobject = WozObject.objects.get()

        self.assertEqual(zaakobject.wozobject, wozobject)
        self.assertEqual(wozobject.woz_object_nummer, '12345')
        self.assertEqual(wozobject.oao_identificatie, 'a')


class ZaakObjectWozDeelobjectTestCase(JWTAuthMixin, APITestCase):
    """
    check polymorphism for WozDeelobject object with nesting
    """
    heeft_alle_autorisaties = True

    def test_read_zaakobject_wozDeelObject(self):
        zaak = ZaakFactory.create()
        zaakobject = ZaakObjectFactory.create(
            zaak=zaak,
            object='',
            type=ZaakobjectTypes.wozDeelobject
        )

        woz_deel_object = WozDeelobject.objects.create(
            zaakobject=zaakobject,
            nummer_woz_deel_object='12345'
        )

        WozObject.objects.create(
            woz_object_nummer='1',
            oao_identificatie='a',
            wpl_woonplaats_naam='test city',
            gor_openbare_ruimte_naam='test space',
            aoa_huisnummer='11',
            locatie_omschrijving='test',
            woz_deelobject=woz_deel_object
        )

        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        url = get_operation_url('zaakobject_read', uuid=zaakobject.uuid)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            data,
            {
                'url': f'http://testserver{url}',
                'zaak': f'http://testserver{zaak_url}',
                'object': '',
                'relatieomschrijving': '',
                'type': ZaakobjectTypes.wozDeelobject,
                'objectIdentificatie': {
                    'nummerWozDeelObject': '12345',
                    'isOnderdeelVan': {
                        'wozObjectNummer': '1',
                        'aanduidingWozObject': {
                            'oaoIdentificatie': 'a',
                            'wplWoonplaatsNaam': 'test city',
                            'aoaPostcode': '',
                            'gorOpenbareRuimteNaam': 'test space',
                            'aoaHuisnummer': 11,
                            'aoaHuisletter': '',
                            'aoaHuisnummertoevoeging': '',
                            'locatieOmschrijving': 'test'
                        }
                    }
                }
            }
        )

    def test_create_zaakobject_wozDeelObject(self):
        url = get_operation_url('zaakobject_create')
        zaak = ZaakFactory.create()
        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        data = {
            'zaak': f'http://testserver{zaak_url}',
            'type': ZaakobjectTypes.wozDeelobject,
            'relatieomschrijving': 'test',
            'objectIdentificatie': {
                'nummerWozDeelObject': '12345',
                'isOnderdeelVan': {
                    'wozObjectNummer': '1',
                    'aanduidingWozObject': {
                        'oaoIdentificatie': 'a',
                        'wplWoonplaatsNaam': 'test city',
                        'aoaPostcode': '',
                        'gorOpenbareRuimteNaam': 'test space',
                        'aoaHuisnummer': 11,
                        'aoaHuisletter': '',
                        'aoaHuisnummertoevoeging': '',
                        'locatieOmschrijving': 'test'
                    }
                }
            }
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ZaakObject.objects.count(), 1)
        self.assertEqual(WozDeelobject.objects.count(), 1)

        zaakobject = ZaakObject.objects.get()
        wozdeelobject = WozDeelobject.objects.get()

        self.assertEqual(zaakobject.wozdeelobject, wozdeelobject)
        self.assertEqual(wozdeelobject.nummer_woz_deel_object, '12345')
        self.assertEqual(wozdeelobject.is_onderdeel_van.oao_identificatie, 'a')


class ZaakObjectWozWaardeTestCase(JWTAuthMixin, APITestCase):
    """
    check polymorphism for WozWaarde object with nesting
    """
    heeft_alle_autorisaties = True

    def test_read_zaakobject_wozWaarde(self):
        zaak = ZaakFactory.create()
        zaakobject = ZaakObjectFactory.create(
            zaak=zaak,
            object='',
            type=ZaakobjectTypes.wozWaarde
        )

        woz_warde = WozWaarde.objects.create(
            zaakobject=zaakobject,
            waardepeildatum='2019'
        )

        WozObject.objects.create(
            woz_object_nummer='1',
            oao_identificatie='a',
            wpl_woonplaats_naam='test city',
            gor_openbare_ruimte_naam='test space',
            aoa_huisnummer='11',
            locatie_omschrijving='test',
            woz_warde=woz_warde
        )

        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        url = get_operation_url('zaakobject_read', uuid=zaakobject.uuid)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            data,
            {
                'url': f'http://testserver{url}',
                'zaak': f'http://testserver{zaak_url}',
                'object': '',
                'relatieomschrijving': '',
                'type': ZaakobjectTypes.wozWaarde,
                'objectIdentificatie': {
                    'waardepeildatum': '2019',
                    'isVoor': {
                        'wozObjectNummer': '1',
                        'aanduidingWozObject': {
                            'oaoIdentificatie': 'a',
                            'wplWoonplaatsNaam': 'test city',
                            'aoaPostcode': '',
                            'gorOpenbareRuimteNaam': 'test space',
                            'aoaHuisnummer': 11,
                            'aoaHuisletter': '',
                            'aoaHuisnummertoevoeging': '',
                            'locatieOmschrijving': 'test'
                        }
                    }
                }
            }
        )

    def test_create_zaakobject_wozWaarde(self):
        url = get_operation_url('zaakobject_create')
        zaak = ZaakFactory.create()
        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        data = {
            'zaak': f'http://testserver{zaak_url}',
            'type': ZaakobjectTypes.wozWaarde,
            'relatieomschrijving': 'test',
            'objectIdentificatie': {
                'waardepeildatum': '2019',
                'isVoor': {
                    'wozObjectNummer': '1',
                    'aanduidingWozObject': {
                        'oaoIdentificatie': 'a',
                        'wplWoonplaatsNaam': 'test city',
                        'aoaPostcode': '',
                        'gorOpenbareRuimteNaam': 'test space',
                        'aoaHuisnummer': 11,
                        'aoaHuisletter': '',
                        'aoaHuisnummertoevoeging': '',
                        'locatieOmschrijving': 'test'
                    }
                }
            }
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ZaakObject.objects.count(), 1)
        self.assertEqual(WozWaarde.objects.count(), 1)

        zaakobject = ZaakObject.objects.get()
        wozwaarde = WozWaarde.objects.get()

        self.assertEqual(zaakobject.wozwaarde, wozwaarde)
        self.assertEqual(wozwaarde.waardepeildatum, '2019')
        self.assertEqual(wozwaarde.is_voor.oao_identificatie, 'a')


class ZaakObjectZakelijkRechtTestCase(JWTAuthMixin, APITestCase):
    """
    check polymorphism for ZakelijkRecht object with nesting
    """
    heeft_alle_autorisaties = True

    def test_read_zaakobject_zakelijkRecht(self):
        zaak = ZaakFactory.create()
        zaakobject = ZaakObjectFactory.create(
            zaak=zaak,
            object='',
            type=ZaakobjectTypes.zakelijkRecht
        )

        zakelijk_recht = ZakelijkRecht.objects.create(
            zaakobject=zaakobject,
            identificatie='12345',
            avg_aard='test'
        )

        KadastraleOnroerendeZaak.objects.create(
            zakelijk_recht=zakelijk_recht,
            kadastrale_identificatie='1',
            kadastrale_aanduiding='test'
        )

        heeft_als_gerechtigde = ZakelijkRechtHeeftAlsGerechtigde.objects.create(
            zakelijk_recht=zakelijk_recht
        )
        NatuurlijkPersoon.objects.create(
            zakelijk_rechtHeeft_als_gerechtigde=heeft_als_gerechtigde,
            anp_identificatie='12345',
            inp_a_nummer='1234567890'
        )
        NietNatuurlijkPersoon.objects.create(
            zakelijk_rechtHeeft_als_gerechtigde=heeft_als_gerechtigde,
            ann_identificatie='123456',
        )

        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        url = get_operation_url('zaakobject_read', uuid=zaakobject.uuid)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            data,
            {
                'url': f'http://testserver{url}',
                'zaak': f'http://testserver{zaak_url}',
                'object': '',
                'relatieomschrijving': '',
                'type': ZaakobjectTypes.zakelijkRecht,
                'objectIdentificatie': {
                    'identificatie': '12345',
                    'avgAard': 'test',
                    'heeftBetrekkingOp': {
                        'kadastraleIdentificatie': '1',
                        'kadastraleAanduiding': 'test'
                    },
                    'heeftAlsGerechtigde': {
                        'natuurlijkPersoon': {
                            'inpBsn': '',
                            'anpIdentificatie': '12345',
                            'inpA_nummer': '1234567890',
                            'geslachtsnaam': '',
                            'voorvoegselGeslachtsnaam': '',
                            'voorletters': '',
                            'voornamen': '',
                            'geslachtsaanduiding': '',
                            'geboortedatum': '',
                            'verblijfsadres': '',
                            'subVerblijfBuitenland': ''
                        },
                        'nietNatuurlijkPersoon': {
                            'innNnpId': '',
                            'annIdentificatie': '123456',
                            'statutaireNaam': '',
                            'innRechtsvorm': '',
                            'bezoekadres': '',
                            'subVerblijfBuitenland': ''
                        }
                    }
                }
            }
        )

    def test_create_zaakobject_zakelijkRecht(self):
        url = get_operation_url('zaakobject_create')
        zaak = ZaakFactory.create()
        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        data = {
            'zaak': f'http://testserver{zaak_url}',
            'type': ZaakobjectTypes.zakelijkRecht,
            'relatieomschrijving': 'test',
            'objectIdentificatie': {
                'identificatie': '1111',
                'avgAard': 'test',
                'heeftBetrekkingOp': {
                    'kadastraleIdentificatie': '1',
                    'kadastraleAanduiding': 'test'
                },
                'heeftAlsGerechtigde': {
                    'natuurlijkPersoon': {
                        'inpBsn': '',
                        'anpIdentificatie': '1234',
                        'inpA_nummer': '1234567890',
                    },
                    'nietNatuurlijkPersoon': {
                        'innNnpId': '',
                        'annIdentificatie': '123456',
                    }
                }
            }
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ZaakObject.objects.count(), 1)
        self.assertEqual(ZakelijkRecht.objects.count(), 1)

        zaakobject = ZaakObject.objects.get()
        zakelijkrecht = ZakelijkRecht.objects.get()

        self.assertEqual(zaakobject.zakelijkrecht, zakelijkrecht)
        self.assertEqual(zakelijkrecht.identificatie, '1111')
        self.assertEqual(zakelijkrecht.heeft_betrekking_op.kadastrale_identificatie, '1')
        self.assertEqual(zakelijkrecht.heeft_als_gerechtigde.natuurlijkpersoon.anp_identificatie, '1234')
        self.assertEqual(
            zakelijkrecht.heeft_als_gerechtigde.nietnatuurlijkpersoon.ann_identificatie,
            '123456'
        )


class ZaakObjectOverigeTestCase(JWTAuthMixin, APITestCase):
    """
    check polymorphism for Overige object with JSON field
    """
    heeft_alle_autorisaties = True

    def test_read_zaakobject_overige(self):

        zaak = ZaakFactory.create()
        zaakobject = ZaakObjectFactory.create(
            zaak=zaak,
            object='',
            type=ZaakobjectTypes.overige
        )
        Overige.objects.create(
            zaakobject=zaakobject,
            overige_data={
                'some_field': 'some value'
            }
        )

        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        url = get_operation_url('zaakobject_read', uuid=zaakobject.uuid)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            data,
            {
                'url': f'http://testserver{url}',
                'zaak': f'http://testserver{zaak_url}',
                'object': '',
                'relatieomschrijving': '',
                'type': ZaakobjectTypes.overige,
                'objectIdentificatie': {
                    'overigeData': {
                        'someField': 'some value'
                    }
                }
            }
        )

    def test_create_zaakobject_overige(self):
        url = get_operation_url('zaakobject_create')
        zaak = ZaakFactory.create()
        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        data = {
            'zaak': f'http://testserver{zaak_url}',
            'type': ZaakobjectTypes.overige,
            'relatieomschrijving': 'test',
            'objectIdentificatie': {
                'overigeData': {
                    'someField': 'some value'
                }
            }
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ZaakObject.objects.count(), 1)
        self.assertEqual(Overige.objects.count(), 1)

        zaakobject = ZaakObject.objects.get()
        overige = Overige.objects.get()

        self.assertEqual(zaakobject.overige, overige)
        self.assertEqual(overige.overige_data, {'some_field': 'some value'})
