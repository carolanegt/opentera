from flask_restx import Resource

# from services.RoomReservation.AccessManager import AccessManager, current_login_type, current_user_client, LoginType
from services.shared.ServiceAccessManager import ServiceAccessManager, current_login_type, current_user_client, \
    LoginType
from services.BureauActif.FlaskModule import default_api_ns as api


class QueryUserInfos(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @api.doc(description='Gets user infos from token: user_name, user_uuid',
             responses={200: 'Success'})
    @ServiceAccessManager.token_required
    def get(self):
        user_infos = {
            'user_uuid': 'unknown',
            'user_fullname': 'unknown',
            'is_super_admin': False
        }

        if current_login_type == LoginType.USER_LOGIN:
            user_infos['user_uuid'] = current_user_client.user_uuid
            user_infos['user_fullname'] = current_user_client.user_fullname
            user_infos['is_super_admin'] = current_user_client.user_superadmin

        return user_infos
