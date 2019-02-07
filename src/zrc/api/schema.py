from django.conf import settings

from drf_yasg import openapi

description = """Een API om een zaakregistratiecomponent te benaderen.

De `ZAAK` is het kernobject in deze API, waaraan verschillende andere
resources gerelateerd zijn. De ZRC API werkt samen met andere ZGW API's, t.w.
DRC, ZTC en BRC, om tot volledige functionaliteit te komen.

**Autorisatie**

Deze API vereist autorisatie. Je kan de
[token-tool](https://ref.tst.vng.cloud/tokens/) gebruiken om JWT-tokens te
genereren.

**Handige links**

* [Aan de slag](https://ref.tst.vng.cloud/ontwikkelaars/)
* ["Papieren" standaard](https://ref.tst.vng.cloud/standaard/)
"""

info = openapi.Info(
    title="Zaakregistratiecomponent (ZRC) API",
    default_version=settings.API_VERSION,
    description=description,
    contact=openapi.Contact(
        email="support@maykinmedia.nl",
        url="https://github.com/VNG-Realisatie/gemma-zaken"
    ),
    license=openapi.License(name="EUPL 1.2"),
)
