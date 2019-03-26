from libtera.db.Base import db
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSiteGroup import TeraSiteGroup
from libtera.db.models.TeraSiteAccess import TeraSiteAccess
from libtera.db.models.TeraSite import TeraSite
from libtera.db.models.TeraProject import TeraProject
from libtera.db.models.TeraProjectAccess import TeraProjectAccess
from libtera.db.models.TeraProjectGroup import TeraProjectGroup

from modules.FlaskModule.FlaskModule import flask_app


class DBManager:
    """db_infos = {
        'user': '',
        'pw': '',
        'db': '',
        'host': '',
        'port': '',
        'type': ''
    }"""

    def __init__(self):
        pass

    @staticmethod
    def create_defaults():
        if TeraSiteGroup.get_count() == 0:
            print("No sitegroups - creating default usergroups")
            # TeraSiteGroup.create_default_usergroups()

        if TeraUser.get_count() == 0:
            print('No users - creating default admin user')
            TeraUser.create_default_account()

    @staticmethod
    def open(db_infos, echo=False):
        db_uri = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % db_infos

        flask_app.config.update({
            'SQLALCHEMY_DATABASE_URI': db_uri,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ECHO': echo
        })

        # Create db engine
        db.init_app(flask_app)
        db.app = flask_app

        # Init tables
        db.drop_all()
        db.create_all()

    @staticmethod
    def open_local(db_infos, echo=False):
        db_uri = 'sqlite:///%(filename)s' % db_infos

        flask_app.config.update({
            'SQLALCHEMY_DATABASE_URI': db_uri,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ECHO': echo
        })

        # Create db engine
        db.init_app(flask_app)
        db.app = flask_app

        # Init tables
        db.create_all()
