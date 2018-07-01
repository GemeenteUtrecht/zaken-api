from drf_extra_fields.fields import Base64FileField
from rest_framework import serializers

from drc.datamodel.models import (
    EnkelvoudigInformatieObject, ZaakInformatieObject
)


class AnyFileType:
    def __contains__(self, item):
        return True


class AnyBase64File(Base64FileField):
    ALLOWED_TYPES = AnyFileType()

    def get_file_extension(self, filename, decoded_file):
        return "bin"


class EnkelvoudigInformatieObjectSerializer(serializers.HyperlinkedModelSerializer):

    inhoud = AnyBase64File()

    class Meta:
        model = EnkelvoudigInformatieObject
        fields = (
            'url',
            'identificatie',
            'bronorganisatie',
            'creatiedatum',
            'titel',
            'auteur',
            'formaat',
            'taal',
            'inhoud'
        )


class ZaakInformatieObjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ZaakInformatieObject
        fields = (
            'url',
            'zaak',
            'informatieobject'
        )