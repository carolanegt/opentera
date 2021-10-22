from flask_restx import Resource
from flask_babel import gettext
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import service_api_ns as api
from modules.DatabaseModule.DBManager import DBManager

from opentera.db.models.TeraSite import TeraSite
from sqlalchemy.exc import InvalidRequestError

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_site', type=int, help='ID of the site to query')


class ServiceQuerySites(Resource):

    def __init__(self, _api, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self, _api)

    @LoginModule.service_token_or_certificate_required
    @api.expect(get_parser)
    @api.doc(description='Return site information.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged service doesn\'t have permission to access the requested data'})
    def get(self):
        parser = get_parser
        args = parser.parse_args()

        service_access = DBManager.serviceAccess(current_service)

        sites = []
        # Can only query site with an id
        if not args['id_site']:
            return gettext('Missing site id'), 400

        if args['id_site']:
            sites = [TeraSite.get_site_by_id(args['id_site'])]

        try:
            sites_list = []
            for site in sites:
                site_json = site.to_json(minimal=True)
                sites_list.append(site_json)

            return sites_list

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         ServiceQuerySites.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Invalid request'), 500
