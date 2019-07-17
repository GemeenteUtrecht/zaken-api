from vng_api_common.conf.api import *  # noqa - imports white-listed

REST_FRAMEWORK = BASE_REST_FRAMEWORK.copy()
REST_FRAMEWORK['PAGE_SIZE'] = 100

SECURITY_DEFINITION_NAME = 'JWT-Claims'

SWAGGER_SETTINGS = BASE_SWAGGER_SETTINGS.copy()
SWAGGER_SETTINGS.update({
    'DEFAULT_INFO': 'zrc.api.schema.info',

    'SECURITY_DEFINITIONS': {
        SECURITY_DEFINITION_NAME: {
            # OAS 3.0
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
            # not official...
            # 'scopes': {},  # TODO: set up registry that's filled in later...

            # Swagger 2.0
            # 'name': 'Authorization',
            # 'in': 'header'
            # 'type': 'apiKey',
        }
    },
    'DEFAULT_FIELD_INSPECTORS': (
        'vng_api_common.inspectors.geojson.GeometryFieldInspector',
    ) + BASE_SWAGGER_SETTINGS['DEFAULT_FIELD_INSPECTORS'],
})

GEMMA_URL_INFORMATIEMODEL_VERSIE = '1.0'

repo = 'maykinmedia/vng-referentielijsten'
commit = '50013acbb22866e9dbaef67473becb505025ea5f'
REFERENTIELIJSTEN_API_SPEC = f'https://raw.githubusercontent.com/{repo}/{commit}/src/openapi.yaml'  # noqa

ztc_repo = 'vng-Realisatie/gemma-zaaktypecatalogus'
ztc_commit = '3f672a7e1c03a2e415df4209b0e9fa7c32ce41e4'
ZTC_API_SPEC = f'https://raw.githubusercontent.com/{ztc_repo}/{ztc_commit}/src/openapi.yaml'  # noqa
