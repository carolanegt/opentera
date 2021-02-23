from flask_restx import Resource

# from services.RoomReservation.AccessManager import AccessManager, current_login_type, current_user_client, LoginType
from opentera.services.ServiceAccessManager import ServiceAccessManager, current_login_type, current_user_client, \
    LoginType
from services.BureauActif.FlaskModule import default_api_ns as api

# Parser definition(s)
from services.RoomReservation import Globals

get_parser = api.parser()
get_parser.add_argument('id_site', type=int, help='ID of the selected site')


class QueryUserInfos(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @api.expect(get_parser)
    @api.doc(description='Gets user infos from token: user_name, user_uuid',
             responses={200: 'Success'})
    @ServiceAccessManager.token_required
    def get(self):
        parser = get_parser
        args = parser.parse_args()
        user_infos = {
            'user_uuid': 'unknown',
            'user_fullname': 'unknown',
            'is_super_admin': False
        }

        if current_login_type == LoginType.USER_LOGIN:
            user_infos['user_uuid'] = current_user_client.user_uuid
            user_infos['user_fullname'] = current_user_client.user_fullname
            user_infos['is_super_admin'] = current_user_client.user_superadmin

        # If reservation has a session associated to it, get it from OpenTera
        if args['id_site']:
            params = {'id_site': args['id_site'], 'uuid_user': current_user_client.user_uuid}

            endpoint = '/api/service/users/access'
            response = Globals.service.get_from_opentera(endpoint, params)

            if response.status_code == 200:
                role = response.json()
                if args['id_site']:
                    site_admin = True if role['site_role'] == 'admin' else False
                    user_infos.update({'is_site_admin': site_admin})

        return user_infos
