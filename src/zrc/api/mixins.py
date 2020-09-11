from typing import Optional

from django.db import models

from rest_framework import serializers

from zrc.api.scopes import SCOPE_ZAKEN_GEFORCEERD_BIJWERKEN
from zrc.datamodel.models import Zaak

from .exceptions import ZaakClosed


class ClosedZaakMixin:
    def _has_override(self, zaak: Zaak) -> bool:
        jwt_auth = self.request.jwt_auth
        return jwt_auth.has_auth(
            scopes=SCOPE_ZAKEN_GEFORCEERD_BIJWERKEN,
            zaaktype=zaak.zaaktype,
            vertrouwelijkheidaanduiding=zaak.vertrouwelijkheidaanduiding,
        )

    def _check_zaak_closed(self, zaak: Optional[Zaak] = None) -> None:
        """
        Raise ZaakClosed if an attempt is made to modify a closed zaak.
        Unless you have the scope SCOPE_ZAKEN_GEFORCEERD_BIJWERKEN, an application
        is not allowed to mutate a closed zaak.
        """
        # if there is no zaak involved, nothing to do
        if not zaak:
            return

        # zaak open -> don't raise exceptions
        if not zaak.is_closed:
            return

        # zaak is closed - do we have the special i-can-do-anything permission?
        if self._has_override(zaak):
            return

        raise ZaakClosed()

    def perform_create(self, serializer: serializers.ModelSerializer) -> None:
        """
        Block the create if the related zaak is closed.
        :raises: PermissionDenied if the related Zaak is closed.
        """
        zaak = serializer.validated_data.get("zaak")
        self._check_zaak_closed(zaak)
        super().perform_create(serializer)

    def perform_update(self, serializer: serializers.ModelSerializer) -> None:
        """
        Block the update if the related zaak is closed.
        :raises: PermissionDenied if the related Zaak is closed.
        """
        zaak = serializer.instance.zaak
        self._check_zaak_closed(zaak)
        super().perform_update(serializer)

    def perform_destroy(self, instance: models.Model) -> None:
        """
        Block the destroy if the related zaak is closed.
        :raises: PermissionDenied if the related Zaak is closed.
        """
        zaak = instance.zaak
        self._check_zaak_closed(zaak)
        super().perform_destroy(instance)
