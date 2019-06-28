from django_filters import filters
from vng_api_common.filtersets import FilterSet

from zrc.datamodel.models import (
    Resultaat, Rol, Status, Zaak, ZaakInformatieObject
)


def get_help_text(model_string, field_name):
    from django.apps import apps
    ModelClass = apps.get_model(*model_string.split('.', 1), False)
    field = ModelClass._meta.get_field(field_name)
    return field.help_text


class ZaakFilter(FilterSet):
    class Meta:
        model = Zaak
        fields = {
            'identificatie': ['exact', ],
            'bronorganisatie': ['exact', ],
            'zaaktype': ['exact', ],
            'archiefnominatie': ['exact', 'in', ],
            'archiefactiedatum': ['exact', 'lt', 'gt', ],
            'archiefstatus': ['exact', 'in', ],
            'startdatum': ['exact', 'gt', 'gte', 'lt', 'lte']
        }


class RolFilter(FilterSet):
    betrokkene_identificatie__natuurlijk_persoon__inp_bsn = filters.CharFilter(
        field_name='natuurlijkpersoon__inp_bsn', help_text=get_help_text('datamodel.NatuurlijkPersoon', 'inp_bsn'))
    betrokkene_identificatie__natuurlijk_persoon__anp_identificatie = filters.CharFilter(
        field_name='natuurlijkpersoon__anp_identificatie', help_text=get_help_text('datamodel.NatuurlijkPersoon', 'anp_identificatie'))
    betrokkene_identificatie__natuurlijk_persoon__inp_a_nummer = filters.CharFilter(
        field_name='natuurlijkpersoon__inp_a_nummer', help_text=get_help_text('datamodel.NatuurlijkPersoon', 'inp_a_nummer'))
    betrokkene_identificatie__niet_natuurlijk_persoon__inn_nnp_id = filters.CharFilter(
        field_name='nietnatuurlijkpersoon__inn_nnp_id', help_text=get_help_text('datamodel.NietNatuurlijkPersoon', 'inn_nnp_id'))
    betrokkene_identificatie__niet_natuurlijk_persoon__ann_identificatie = filters.CharFilter(
        field_name='nietnatuurlijkpersoon__ann_identificatie', help_text=get_help_text('datamodel.NietNatuurlijkPersoon', 'ann_identificatie'))
    betrokkene_identificatie__vestiging__vestigings_nummer = filters.CharFilter(
        field_name='vestiging__vestigings_nummer', help_text=get_help_text('datamodel.Vestiging', 'vestigings_nummer'))
    betrokkene_identificatie__vestiging__identificatie = filters.CharFilter(
        field_name='organisatorischeeenheid__identificatie', help_text=get_help_text('datamodel.OrganisatorischeEenheid', 'identificatie'))
    betrokkene_identificatie__medewerker__identificatie = filters.CharFilter(
        field_name='medewerker__identificatie', help_text=get_help_text('datamodel.Medewerker', 'identificatie'))

    class Meta:
        model = Rol
        fields = (
            'zaak',
            'betrokkene',
            'betrokkene_type',
            'betrokkene_identificatie__natuurlijk_persoon__inp_bsn',
            'betrokkene_identificatie__natuurlijk_persoon__anp_identificatie',
            'betrokkene_identificatie__natuurlijk_persoon__inp_a_nummer',
            'betrokkene_identificatie__niet_natuurlijk_persoon__inn_nnp_id',
            'betrokkene_identificatie__niet_natuurlijk_persoon__ann_identificatie',
            'betrokkene_identificatie__vestiging__vestigings_nummer',
            'betrokkene_identificatie__vestiging__identificatie',
            'betrokkene_identificatie__medewerker__identificatie',
            'rolomschrijving',
        )


class StatusFilter(FilterSet):
    class Meta:
        model = Status
        fields = (
            'zaak',
            'status_type',
        )


class ResultaatFilter(FilterSet):
    class Meta:
        model = Resultaat
        fields = (
            'zaak',
            'resultaat_type',
        )


class ZaakInformatieObjectFilter(FilterSet):
    class Meta:
        model = ZaakInformatieObject
        fields = (
            'zaak',
            'informatieobject',
        )
