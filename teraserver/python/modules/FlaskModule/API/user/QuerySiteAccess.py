from flask import jsonify, session, request
from flask_restx import Resource, reqparse, inputs
from sqlalchemy import exc
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSiteAccess import TeraSiteAccess
from modules.DatabaseModule.DBManager import DBManager

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_user', type=int, help='ID of the user from which to request all site roles')
get_parser.add_argument('id_user_group', type=int, help='ID of the user group from which to request all site roles')
get_parser.add_argument('id_site', type=int, help='ID of the site from which to request all user groups roles')
get_parser.add_argument('admins', type=inputs.boolean, help='Flag to limit to sites from which the user is an admin or '
                                                            'users in site that have the admin role')

post_parser = reqparse.RequestParser()
post_parser.add_argument('site_access', type=str, location='json', help='Site access to create / update', required=True)


class QuerySiteAccess(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get user roles for sites. Only one  parameter required and supported at once.',
             responses={200: 'Success - returns list of users roles in sites',
                        400: 'Required parameter is missing (must have at least one id)',
                        500: 'Error occured when loading sites roles'})
    def get(self):
        parser = get_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)
        args = parser.parse_args()

        access = None
        # If we have no arguments, return bad request
        if not any(args.values()):
            return "SiteAccess: missing argument.", 400

        # Query access for user id
        if args['id_user']:
            user_id = args['id_user']

            if user_id in user_access.get_accessible_users_ids():
                access = user_access.query_site_access_for_user(user_id=user_id, admin_only=args['admins'] is not None)

        # Query access for user group
        if args['id_user_group']:
            if args['id_user_group'] in user_access.get_accessible_users_groups_ids():
                from libtera.db.models.TeraUserGroup import TeraUserGroup
                user_group = TeraUserGroup.get_user_group_by_id(args['id_user_group'])
                access = user_group.get_sites_roles()

        # Query access for site id
        if args['id_site']:
            site_id = args['id_site']
            access = user_access.query_access_for_site(site_id=site_id, admin_only=args['admins'] is not None)

        if access is not None:
            access_list = []
            for site, site_role in access.items():
                site_access_json = site.to_json()
                site_access_json['site_role'] = site_role
                access_list.append(site_access_json)
            return jsonify(access_list)

        # No access, but still fine
        return [], 200

    @user_multi_auth.login_required
    @api.expect(post_parser)
    @api.doc(description='Create/update site access for a user group.',
             responses={200: 'Success',
                        403: 'Logged user can\'t modify this site or user access (site admin access required)',
                        400: 'Badly formed JSON or missing fields(id_user or id_site) in the JSON body',
                        500: 'Database error'})
    def post(self):
        # parser = post_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        json_sites = request.json['site_access']

        if not isinstance(json_sites, list):
            json_sites = [json_sites]

        # Validate if we have everything needed
        json_rval = []
        for json_site in json_sites:
            if 'id_user_group' not in json_site:
                return 'Missing id_user_group', 400
            if 'id_site' not in json_site:
                return 'Missing id_site', 400

            # Check if current user can change the access for that site
            if user_access.get_site_role(site_id=json_site['id_site']) != 'admin':
                return 'Forbidden', 403

            # Do the update!
            try:
                access = TeraSiteAccess.update_site_access(json_site['id_user_group'], json_site['id_site'],
                                                           json_site['site_access_role'])
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500

            # TODO: Publish update to everyone who is subscribed to site access update...
            if access:
                json_rval.append(access.to_json())

        return jsonify(json_rval)

    # @user_multi_auth.login_required
    # def delete(self):
    #
    #     return '', 501

