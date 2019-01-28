import uuid
from datetime import date

from django.contrib.gis.db.models import GeometryField
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

from zds_schema.constants import RolOmschrijving, RolTypes
from zds_schema.descriptors import GegevensGroepType
from zds_schema.fields import (
    DaysDurationField, RSINField, VertrouwelijkheidsAanduidingField
)
from zds_schema.models import APIMixin
from zds_schema.validators import alphanumeric_excluding_diacritic

from .constants import BetalingsIndicatie, ZaakobjectTypes


class Zaak(APIMixin, models.Model):
    """
    Modelleer de structuur van een ZAAK.

    Een samenhangende hoeveelheid werk met een welgedefinieerde aanleiding
    en een welgedefinieerd eindresultaat, waarvan kwaliteit en doorlooptijd
    bewaakt moeten worden.
    """
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4,
        help_text="Unieke resource identifier (UUID4)"
    )

    # Relate 'is_deelzaak_van'
    # De relatie vanuit een zaak mag niet verwijzen naar
    # dezelfde zaak d.w.z. moet verwijzen naar een andere
    # zaak. Die andere zaak mag geen relatie ?is deelzaak
    # van? hebben (d.w.z. deelzaken van deelzaken worden
    # niet ondersteund).
    hoofdzaak = models.ForeignKey(
        'self', limit_choices_to={'hoofdzaak__isnull': True},
        null=True, blank=True, on_delete=models.PROTECT,
        related_name='deelzaken', verbose_name='is deelzaak van',
        help_text=_("De verwijzing naar de ZAAK, waarom verzocht is door de "
                    "initiator daarvan, die behandeld wordt in twee of meer "
                    "separate ZAAKen waarvan de onderhavige ZAAK er één is.")
    )

    identificatie = models.CharField(
        max_length=40, blank=True,
        help_text='De unieke identificatie van de ZAAK binnen de organisatie '
                  'die verantwoordelijk is voor de behandeling van de ZAAK.',
        validators=[alphanumeric_excluding_diacritic]
    )
    bronorganisatie = RSINField(
        help_text='Het RSIN van de Niet-natuurlijk persoon zijnde de '
                  'organisatie die de zaak heeft gecreeerd. Dit moet een geldig '
                  'RSIN zijn van 9 nummers en voldoen aan '
                  'https://nl.wikipedia.org/wiki/Burgerservicenummer#11-proef'
    )
    omschrijving = models.CharField(
        max_length=80, blank=True,
        help_text='Een korte omschrijving van de zaak.')
    toelichting = models.TextField(
        max_length=1000, blank=True,
        help_text='Een toelichting op de zaak.'
    )
    zaaktype = models.URLField(
        help_text="URL naar het zaaktype in de CATALOGUS waar deze voorkomt")
    registratiedatum = models.DateField(
        help_text='De datum waarop de zaakbehandelende organisatie de ZAAK '
                  'heeft geregistreerd. Indien deze niet opgegeven wordt, '
                  'wordt de datum van vandaag gebruikt.',
        default=date.today
    )
    verantwoordelijke_organisatie = RSINField(
        help_text='Het RSIN van de Niet-natuurlijk persoon zijnde de organisatie '
                  'die eindverantwoordelijk is voor de behandeling van de '
                  'zaak. Dit moet een geldig RSIN zijn van 9 nummers en voldoen aan '
                  'https://nl.wikipedia.org/wiki/Burgerservicenummer#11-proef'
    )

    startdatum = models.DateField(
        help_text='De datum waarop met de uitvoering van de zaak is gestart')
    einddatum = models.DateField(
        blank=True, null=True,
        help_text='De datum waarop de uitvoering van de zaak afgerond is.',
    )
    einddatum_gepland = models.DateField(
        blank=True, null=True,
        help_text='De datum waarop volgens de planning verwacht wordt dat de '
                  'zaak afgerond wordt.',
    )
    uiterlijke_einddatum_afdoening = models.DateField(
        blank=True, null=True,
        help_text='De laatste datum waarop volgens wet- en regelgeving de zaak '
                  'afgerond dient te zijn.'
    )
    publicatiedatum = models.DateField(
        _("publicatiedatum"), null=True, blank=True,
        help_text=_("Datum waarop (het starten van) de zaak gepubliceerd is of wordt.")
    )

    communicatiekanaal = models.URLField(
        _("communicatiekanaal"), blank=True,
        help_text=_("Het medium waarlangs de aanleiding om een zaak te starten is ontvangen. "
                    "URL naar een communicatiekanaal in de VNG-Referentielijst van communicatiekanalen.")
    )

    vertrouwelijkheidaanduiding = VertrouwelijkheidsAanduidingField(
        _("vertrouwlijkheidaanduiding"),
        help_text=_("Aanduiding van de mate waarin het zaakdossier van de ZAAK voor de openbaarheid bestemd is.")
    )

    resultaattoelichting = models.TextField(
        _("resultaattoelichting"), blank=True,
        help_text=_("Een toelichting op wat het resultaat van de zaak inhoudt.")
    )

    betalingsindicatie = models.CharField(
        _("betalingsindicatie"), max_length=20, blank=True,
        choices=BetalingsIndicatie.choices,
        help_text=_("Indicatie of de, met behandeling van de zaak gemoeide, "
                    "kosten betaald zijn door de desbetreffende betrokkene.")
    )
    laatste_betaaldatum = models.DateTimeField(
        _("laatste betaaldatum"), blank=True, null=True,
        help_text=_("De datum waarop de meest recente betaling is verwerkt "
                    "van kosten die gemoeid zijn met behandeling van de zaak.")
    )

    zaakgeometrie = GeometryField(
        blank=True, null=True,
        help_text="Punt, lijn of (multi-)vlak geometrie-informatie."
    )

    verlenging_reden = models.CharField(
        _("reden verlenging"), max_length=200, blank=True,
        help_text=_("Omschrijving van de reden voor het verlengen van de behandeling van de zaak.")
    )
    verlenging_duur = DaysDurationField(
        _("duur verlenging"), blank=True, null=True,
        help_text=_("Het aantal werkbare dagen waarmee de doorlooptijd van de "
                    "behandeling van de ZAAK is verlengd (of verkort) ten opzichte "
                    "van de eerder gecommuniceerde doorlooptijd.")
    )
    verlenging = GegevensGroepType({
        'reden': verlenging_reden,
        'duur': verlenging_duur,
    })

    opschorting_indicatie = models.BooleanField(
        _("indicatie opschorting"), default=False,
        help_text=_("Aanduiding of de behandeling van de ZAAK tijdelijk is opgeschort.")
    )
    opschorting_reden = models.CharField(
        _("reden opschorting"), max_length=200, blank=True,
        help_text=_("Omschrijving van de reden voor het opschorten van de 306behandeling van de zaak.")
    )
    opschorting = GegevensGroepType({
        'indicatie': opschorting_indicatie,
        'reden': opschorting_reden,
    })

    selectielijstklasse = models.URLField(
        _("selectielijstklasse"), blank=True,
        help_text=_("URL-referentie naar de categorie in de gehanteerde "
                    "'Selectielijst Archiefbescheiden' die, gezien het zaaktype "
                    "en het resultaattype van de zaak, bepalend is voor het "
                    "archiefregime van de zaak.")
    )

    relevante_andere_zaken = ArrayField(
        models.URLField(_("URL naar andere zaak"), max_length=255),
        blank=True, default=list
    )

    class Meta:
        verbose_name = 'zaak'
        verbose_name_plural = 'zaken'
        unique_together = ('bronorganisatie', 'identificatie')

    def __str__(self):
        return self.identificatie

    def save(self, *args, **kwargs):
        if not self.identificatie:
            self.identificatie = str(uuid.uuid4())

        if self.betalingsindicatie == BetalingsIndicatie.nvt and self.laatste_betaaldatum:
            self.laatste_betaaldatum = None

        super().save(*args, **kwargs)

    @property
    def current_status_uuid(self):
        status = self.status_set.order_by('-datum_status_gezet').first()
        return status.uuid if status else None


class ZaakProductOfDienst(models.Model):
    zaak = models.ForeignKey('Zaak', help_text=_("hoort bij"), on_delete=models.CASCADE)
    product_of_dienst = models.URLField(
        _("product of dienst"),
        help_text=_("Het product of de dienst die door de zaak wordt voortgebracht. "
                    "Dit is de URL naar de resource zoals die door de producten- "
                    "en dienstencatalogus-API wordt ontsloten.")
    )

    class Meta:
        verbose_name = _("product of dienst")
        verbose_name_plural = _("producten of diensten")

    def __str__(self):
        return _("{zaak}: {product_of_dienst}").format(zaak=self.zaak, product_of_dienst=self.product_of_dienst)


class Status(models.Model):
    """
    Modelleer een status van een ZAAK.

    Een aanduiding van de stand van zaken van een ZAAK op basis van
    betekenisvol behaald resultaat voor de initiator van de ZAAK.
    """
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4,
        help_text="Unieke resource identifier (UUID4)"
    )
    # relaties
    zaak = models.ForeignKey('Zaak', on_delete=models.CASCADE)
    status_type = models.URLField()

    # extra informatie
    datum_status_gezet = models.DateTimeField(
        help_text='De datum waarop de ZAAK de status heeft verkregen.'
    )
    statustoelichting = models.TextField(
        max_length=1000, blank=True,
        help_text='Een, voor de initiator van de zaak relevante, toelichting '
                  'op de status van een zaak.'
    )

    class Meta:
        verbose_name = 'status'
        verbose_name_plural = 'statussen'

    def __str__(self):
        return "Status op {}".format(self.datum_status_gezet)


class Rol(models.Model):
    """
    Modelleer de rol van een BETROKKENE bij een ZAAK.

    Een of meerdere BETROKKENEn hebben een of meerdere ROL(len) in een ZAAK.
    """
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4,
        help_text="Unieke resource identifier (UUID4)"
    )
    zaak = models.ForeignKey('Zaak', on_delete=models.CASCADE)
    betrokkene = models.URLField(help_text="Een betrokkene gerelateerd aan een zaak")
    betrokkene_type = models.CharField(
        max_length=100, choices=RolTypes.choices,
        help_text='Soort betrokkene'
    )

    rolomschrijving = models.CharField(
        max_length=80, choices=RolOmschrijving.choices,
        help_text='Algemeen gehanteerde benaming van de aard van de ROL'
    )
    roltoelichting = models.TextField(max_length=1000)

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Rollen"


class ZaakObject(models.Model):
    """
    Modelleer een object behorende bij een ZAAK.

    Het OBJECT in kwestie kan in verschillende andere componenten leven,
    zoals het RSGB.
    """
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4,
        help_text="Unieke resource identifier (UUID4)"
    )
    zaak = models.ForeignKey('Zaak', on_delete=models.CASCADE)
    object = models.URLField(help_text='URL naar de resource die het OBJECT beschrijft.')
    relatieomschrijving = models.CharField(
        max_length=80, blank=True,
        help_text='Omschrijving van de betrekking tussen de ZAAK en het OBJECT.'
    )
    object_type = models.CharField(
        max_length=100,
        choices=ZaakobjectTypes.choices,
        help_text="Beschrijft het type object gerelateerd aan de zaak"
    )

    class Meta:
        verbose_name = 'zaakobject'
        verbose_name_plural = 'zaakobjecten'


class ZaakEigenschap(models.Model):
    """
    Een relevant inhoudelijk gegeven waarvan waarden bij
    ZAAKen van eenzelfde ZAAKTYPE geregistreerd moeten
    kunnen worden en dat geen standaard kenmerk is van een
    ZAAK.

    Het RGBZ biedt generieke kenmerken van zaken. Bij zaken van een bepaald zaaktype kan de
    behoefte bestaan om waarden uit te wisselen van gegevens die specifiek zijn voor die zaken. Met
    dit groepattribuutsoort simuleren we de aanwezigheid van dergelijke eigenschappen. Aangezien
    deze eigenschappen specifiek zijn per zaaktype, modelleren we deze eigenschappen hier niet
    specifiek. De eigenschappen worden per zaaktype in een desbetreffende zaaktypecatalogus
    gespecificeerd.
    """
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4,
        help_text="Unieke resource identifier (UUID4)"
    )
    zaak = models.ForeignKey('Zaak', on_delete=models.CASCADE)
    eigenschap = models.URLField(help_text="URL naar de eigenschap in het ZTC")
    # TODO - validatie _zou kunnen_ de configuratie van ZTC uitlezen om input
    # te valideren, en per eigenschap een specifiek datatype terug te geven.
    # In eerste instantie laten we het aan de client over om validatie en
    # type-conversie te doen.
    waarde = models.TextField()

    class Meta:
        verbose_name = 'zaakeigenschap'
        verbose_name_plural = 'zaakeigenschappen'


class ZaakKenmerk(models.Model):
    """
    Model representatie van de Groepattribuutsoort 'Kenmerk'
    """
    zaak = models.ForeignKey('datamodel.Zaak', on_delete=models.CASCADE)
    kenmerk = models.CharField(
        max_length=40,
        help_text='Identificeert uniek de zaak in een andere administratie.')
    bron = models.CharField(
        max_length=40,
        help_text='De aanduiding van de administratie waar het kenmerk op '
                  'slaat.')

    class Meta:
        verbose_name = 'zaak kenmerk'
        verbose_name_plural = 'zaak kenmerken'


class ZaakInformatieObject(models.Model):
    """
    Modelleer INFORMATIEOBJECTen die bij een ZAAK horen.
    """
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4,
        help_text="Unieke resource identifier (UUID4)"
    )
    zaak = models.ForeignKey(Zaak, on_delete=models.CASCADE)
    informatieobject = models.URLField(
        "informatieobject",
        help_text="URL-referentie naar het informatieobject in het DRC, waar "
                  "ook de relatieinformatie opgevraagd kan worden."
    )

    class Meta:
        verbose_name = "zaakinformatieobject"
        verbose_name_plural = "zaakinformatieobjecten"
        unique_together = ('zaak', 'informatieobject')

    def __str__(self) -> str:
        return f"{self.zaak} - {self.informatieobject}"


class KlantContact(models.Model):
    """
    Modelleer het contact tussen een medewerker en een klant.

    Een uniek en persoonlijk contact van een burger of bedrijfsmedewerker met
    een MEDEWERKER van de zaakbehandelende organisatie over een onderhanden of
    afgesloten ZAAK.
    """
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4,
        help_text="Unieke resource identifier (UUID4)"
    )
    zaak = models.ForeignKey('Zaak', on_delete=models.CASCADE)
    identificatie = models.CharField(
        max_length=14, unique=True,
        help_text='De unieke aanduiding van een KLANTCONTACT'
    )
    datumtijd = models.DateTimeField(
        help_text='De datum en het tijdstip waarop het KLANTCONTACT begint'
    )
    kanaal = models.CharField(
        blank=True, max_length=20,
        help_text='Het communicatiekanaal waarlangs het KLANTCONTACT gevoerd wordt'
    )

    class Meta:
        verbose_name = "klantcontact"
        verbose_name_plural = "klantcontacten"

    def __str__(self):
        return self.identificatie

    def save(self, *args, **kwargs):
        if not self.identificatie:
            gen_id = True
            while gen_id:
                identificatie = get_random_string(length=12)
                gen_id = self.__class__.objects.filter(identificatie=identificatie).exists()
            self.identificatie = identificatie
        super().save(*args, **kwargs)
