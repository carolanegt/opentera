from flask_restx import Resource

# from services.RoomReservation.AccessManager import AccessManager, current_login_type, current_user_client, LoginType
from opentera.services.ServiceAccessManager import ServiceAccessManager, current_login_type, current_user_client, \
    LoginType
from services.RoomReservation.FlaskModule import default_api_ns as api

# Parser definition(s)
from services.RoomReservation import Globals

get_parser = api.parser()
get_parser.add_argument('id_site', type=int, help='ID of the selected site')


class QueryAccountInfos(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @api.expect(get_parser)
    @api.doc(description='Gets user infos from token: user_name, user_uuid',
             responses={200: 'Success'})
    @ServiceAccessManager.token_required()
    def get(self):
        parser = get_parser
        args = parser.parse_args()
        account_infos = {
            'login_type': 'unknown',
            'login_id': 0,
            'fullname': '',
            'login_uuid': '',
            'is_super_admin': False,
        }

        if current_login_type == LoginType.USER_LOGIN:
            user = current_user_client.get_user_info()
            account_infos['username'] = user[0]['user_username']
            account_infos.update({'sites': user[0]['sites']})
            account_infos['login_type'] = 'user'
            account_infos['login_uuid'] = current_user_client.user_uuid
            account_infos['login_id'] = current_user_client.id_user
            account_infos['fullname'] = current_user_client.user_fullname
            account_infos['is_super_admin'] = current_user_client.user_superadmin

        return account_infos
