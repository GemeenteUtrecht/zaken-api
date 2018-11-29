from django.utils import timezone

import factory
import factory.fuzzy
from zds_schema.constants import ObjectTypes, RolOmschrijving, RolTypes


class ZaakFactory(factory.django.DjangoModelFactory):
    zaaktype = factory.Faker('url')
    registratiedatum = factory.Faker('date_this_month', before_today=True)
    startdatum = factory.Faker('date_this_month', before_today=True)
    bronorganisatie = factory.Faker('ssn', locale='nl_NL')
    verantwoordelijke_organisatie = factory.Faker('ssn', locale='nl_NL')

    class Meta:
        model = 'datamodel.Zaak'


class ZaakInformatieObjectFactory(factory.django.DjangoModelFactory):
    zaak = factory.SubFactory(ZaakFactory)
    informatieobject = factory.Faker('url')

    class Meta:
        model = 'datamodel.ZaakInformatieObject'


class ZaakEigenschapFactory(factory.django.DjangoModelFactory):
    zaak = factory.SubFactory(ZaakFactory)
    eigenschap = factory.Faker('url')
    waarde = factory.Faker('word')

    class Meta:
        model = 'datamodel.ZaakEigenschap'


class ZaakObjectFactory(factory.django.DjangoModelFactory):
    zaak = factory.SubFactory(ZaakFactory)
    object = factory.Faker('url')
    object_type = factory.fuzzy.FuzzyChoice(choices=ObjectTypes.values)

    class Meta:
        model = 'datamodel.ZaakObject'


class RolFactory(factory.django.DjangoModelFactory):
    zaak = factory.SubFactory(ZaakFactory)
    betrokkene = factory.Faker('url')
    betrokkene_type = factory.fuzzy.FuzzyChoice(RolTypes.values)
    rolomschrijving = factory.fuzzy.FuzzyChoice(RolOmschrijving.values)

    class Meta:
        model = 'datamodel.Rol'


class StatusFactory(factory.django.DjangoModelFactory):
    zaak = factory.SubFactory(ZaakFactory)
    status_type = factory.Faker('url')
    datum_status_gezet = factory.Faker('date_time_this_month', tzinfo=timezone.utc)

    class Meta:
        model = 'datamodel.Status'
