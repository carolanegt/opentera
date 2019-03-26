from flask import jsonify, session
from flask_restful import Resource, reqparse
from modules.Globals import auth, db_man
from sqlalchemy.exc import InvalidRequestError
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSite import TeraSite
from libtera.db.models.TeraProject import TeraProject


class QueryProjects(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id_project', type=int, help='id_project')
        self.parser.add_argument('id_site', type=int, help='id_site')

    @auth.login_required
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        args = self.parser.parse_args()

        my_args = {}

        # Make sure we remove the None, safe?
        for key in args:
            if args[key] is not None:
                my_args[key] = args[key]
        try:
            projects = db_man.get_user_projects(current_user, **my_args)
            projects_list = []
            for project in projects:
                projects_list.append(project.to_json())
            return jsonify(projects_list)
        except InvalidRequestError:
            return '', 500

    def post(self):
        return '', 501

    def delete(self):
        return '', 501

