from flask.views import MethodView
from flask import render_template, request
from services.RoomReservation.AccessManager import AccessManager


class Index(MethodView):
    # Decorators everywhere?
    # decorators = [auth.login_required]

    def __init__(self, *args, **kwargs):
        print('Index.__init__', args, kwargs)
        self.flaskModule = kwargs.get('flaskModule', None)
        print(self.flaskModule)

    @AccessManager.token_required
    def get(self):
        hostname = self.flaskModule.config.server_config['hostname']
        port = self.flaskModule.config.server_config['port']
        backend_hostname = self.flaskModule.config.backend_config['hostname']
        backend_port = self.flaskModule.config.backend_config['port']
        if 'X_EXTERNALHOST' in request.headers:
            backend_hostname = request.headers['X_EXTERNALHOST'];

        if 'X_EXTERNALPORT' in request.headers:
            backend_port = request.headers['X_EXTERNALPORT'];

        return render_template('index.html', hostname=hostname, port=port,
                               backend_hostname=backend_hostname, backend_port=backend_port)

    def post(self):
        print('post')
        pass