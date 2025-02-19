from flask import request
from flask_babel import gettext
from flask_restx import Resource
from services.FileTransferService.FlaskModule import file_api_ns as api
from opentera.services.ServiceAccessManager import ServiceAccessManager
from services.FileTransferService.libfiletransferservice.db.models.AssetFileData import AssetFileData
import services.FileTransferService.Globals as Globals

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('access_token', type=str, required=True, help='Access token proving that the requested assets '
                                                                      'can be accessed.')
get_parser.add_argument('asset_uuid', type=str, required=True, help='UUID of the asset to get info')

post_schema = api.schema_model('assets',
                               {'properties':
                                   {
                                       'asset_uuid':
                                           {
                                               'type': 'string',
                                               'location': 'json'
                                           },
                                       'access_token':
                                           {
                                               'type': 'string',
                                               'location': 'json'
                                           }
                                   }
                                })


class QueryAssetFileInfos(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.expect(get_parser, validate=True)
    @api.doc(description='Query informations about stored file',
             responses={200: 'Success - Return informations about file',
                        400: 'Bad request',
                        403: 'Access denied to the requested asset'})
    @ServiceAccessManager.service_or_others_token_required(allow_dynamic_tokens=True, allow_static_tokens=False)
    def get(self):
        args = get_parser.parse_args()

        if not Globals.service.has_access_to_asset(args['access_token'], args['asset_uuid']):
            return gettext('Access denied for that asset'), 403

        # Ok, all is fine, we can provide the requested information
        asset = AssetFileData.get_asset_for_uuid(uuid_asset=args['asset_uuid'])

        if not asset:
            return gettext('No asset found'), 404

        return asset.to_json()

    @api.expect(post_schema)
    @api.doc(description='Query information about multiple assets at the same time or update an existing asset '
                         'information. If the \'asset_uuids\' list is present in the data, return assets. Otherwise, '
                         'uses the \'file_asset\' informations to update the data',
             responses={200: 'Success - Return informations about file assets',
                        400: 'Required parameter is missing',
                        403: 'Access denied to the requested asset'})
    @ServiceAccessManager.service_or_others_token_required(allow_dynamic_tokens=True, allow_static_tokens=False)
    def post(self):
        if 'assets' not in request.json and 'file_asset' not in request.json:
            return gettext('Badly formatted request'), 400

        if 'assets' in request.json:
            # Verify access tokens
            assets = request.json['assets']
            requested_assets_uuids = []
            for asset in assets:
                if 'access_token' not in asset:
                    return gettext('Missing access token for at least one requested asset'), 400
                if 'asset_uuid' not in asset:
                    return gettext('Missing asset UUID for at least one requested asset'), 400

                if not Globals.service.has_access_to_asset(access_token=asset['access_token'],
                                                           asset_uuid=asset['asset_uuid']):
                    return gettext('Access denied for at least one requested asset'), 403
                requested_assets_uuids.append(asset['asset_uuid'])

            # Query assets data
            assets = AssetFileData.get_assets_for_uuids(requested_assets_uuids)

            return [asset.to_json() for asset in assets]
        else:
            # Update file asset
            asset_json = request.json['file_asset']

            if 'access_token' not in asset_json:
                return gettext('Missing access token'), 400

            if 'asset_uuid' not in asset_json:
                return gettext('Missing asset uuid'), 400

            allowed_asset_uuids = Globals.service.get_accessible_asset_uuids(asset_json['access_token'])

            if asset_json['asset_uuid'] not in allowed_asset_uuids:
                return gettext('Forbidden'), 403

            # Only change possible here is the original file name, as other information are linked to the file itself
            if 'asset_original_filename' not in asset_json:
                return gettext('Only original filename can be changed from here'), 400

            asset = AssetFileData.get_asset_for_uuid(asset_json['asset_uuid'])

            if not asset:
                return gettext('No asset found'), 404

            asset.asset_original_filename = asset_json['asset_original_filename']
            asset.commit()

            return asset.to_json()
