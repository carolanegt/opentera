from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from sqlalchemy import exc
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraDevice import TeraDevice


class TeraProjectTest(BaseModelsTest):

    def test_nullable_args(self):
        with self._flask_app.app_context():
            new_project = TeraProject()
            new_project.id_site = 1
            new_project.project_name = None
            self.db.session.add(new_project)
            self.assertRaises(exc.IntegrityError, self.db.session.commit)
            self.db.session.rollback()
            new_project = TeraProject()
            new_project.id_site = None
            new_project.project_name = 'test_nullable_args'
            self.db.session.add(new_project)
            self.assertRaises(exc.IntegrityError, self.db.session.commit)

    def test_unique_args(self):
        pass

    def test_to_json(self):
        with self._flask_app.app_context():
            new_project = TeraProject()
            new_project.id_site = 1
            new_project.project_name = 'test_to_json'
            self.db.session.add(new_project)
            self.db.session.commit()
            new_project_json = new_project.to_json()
            new_project_json_minimal = new_project.to_json(minimal=True)
            self._check_json(new_project, project_test=new_project_json)
            self._check_json(new_project, project_test=new_project_json_minimal, minimal=True)

    def _check_json(self, project: TeraProject, project_test: dict, minimal=False):
        self.assertGreaterEqual(project_test['id_project'], project.id_project)
        self.assertEqual(project_test['id_site'], project.id_site)
        self.assertEqual(project_test['project_name'], project.project_name)
        if not minimal:
            self.assertEqual(project_test['site_name'], project.project_site.site_name)

    def test_to_json_create_event(self):
        with self._flask_app.app_context():
            new_project = TeraProject()
            new_project.id_site = 1
            new_project.project_name = 'test_to_json_create_event'
            self.db.session.add(new_project)
            self.db.session.commit()
            new_project_json = new_project.to_json_create_event()
            self._check_json(new_project, project_test=new_project_json, minimal=True)

    def test_to_json_update_event(self):
        with self._flask_app.app_context():
            new_project = TeraProject()
            new_project.id_site = 1
            new_project.project_name = 'test_to_json_update_event'
            self.db.session.add(new_project)
            self.db.session.commit()
            new_project_json = new_project.to_json_update_event()
            self._check_json(new_project, project_test=new_project_json, minimal=True)

    def test_to_json_delete_event(self):
        with self._flask_app.app_context():
            new_project = TeraProject()
            new_project.id_site = 1
            new_project.project_name = 'test_to_json_delete_event'
            self.db.session.add(new_project)
            self.db.session.commit()
            new_project_json = new_project.to_json_delete_event()
            self.assertGreaterEqual(new_project_json['id_project'], 1)

    def test_get_users_ids_in_project(self):
        with self._flask_app.app_context():
            new_project = TeraProject()
            new_project.id_site = 1
            new_project.project_name = 'test_get_users_ids_in_project'
            self.db.session.add(new_project)
            self.db.session.commit()
            users_ids = new_project.get_users_ids_in_project()
            self.assertIsNotNone(users_ids)

    def test_get_users_in_project(self):
        with self._flask_app.app_context():
            new_project = TeraProject()
            new_project.id_site = 1
            new_project.project_name = 'test_get_users_in_project'
            self.db.session.add(new_project)
            self.db.session.commit()
            users = new_project.get_users_in_project()
            self.assertIsNotNone(users)

    def test_get_project_by_projectname(self):
        with self._flask_app.app_context():
            new_project = TeraProject()
            new_project.id_site = 1
            new_project.project_name = 'test_get_project_by_projectname'
            self.db.session.add(new_project)
            self.db.session.commit()
            same_project = new_project.get_project_by_projectname(projectname=new_project.project_name)
            self.assertEqual(same_project, new_project)

    def test_get_project_by_id(self):
        with self._flask_app.app_context():
            new_project = TeraProject()
            new_project.id_site = 1
            new_project.project_name = 'test_get_project_by_id'
            self.db.session.add(new_project)
            self.db.session.commit()
            same_project = new_project.get_project_by_id(project_id=new_project.id_project)
            self.assertEqual(same_project, new_project)

    def test_insert_and_delete(self):
        with self._flask_app.app_context():
            new_project = TeraProject()
            new_project.id_site = 1
            new_project.project_name = 'test_insert_and_delete'
            TeraProject.insert(project=new_project)
            # self.assertRaises(Exception, TeraProject.insert(project=new_project))
            id_to_del = new_project.id_project
            TeraProject.delete(id_todel=id_to_del)
            # try:
            #     TeraProject.insert(project=new_project)
            # except Exception as e:
            #     print(e)
            # self.assertRaises(Exception, TeraProject.insert(project=new_project))
            # don't know why the self.assertRaises doesnt work here

    def test_update_set_inactive(self):
        with self._flask_app.app_context():
            new_project = TeraProject()
            new_project.id_site = 1
            new_project.project_name = 'test_update_set_inactive'
            self.db.session.add(new_project)
            self.db.session.commit()

            # Create participants
            participants = []
            for i in range(3):
                part = TeraParticipant()
                part.id_project = new_project.id_project
                part.participant_name = 'Participant #' + str(i+1)
                part.participant_enabled = True
                TeraParticipant.insert(part)
                participants.append(part)

            for part in participants:
                self.assertTrue(part.participant_enabled)

            # Associate devices
            devices = []
            for i in range(2):
                device = TeraDevice()
                device.device_name = 'Device #' + str(i+1)
                device.id_device_type = 1
                TeraDevice.insert(device)
                devices.append(device)
            part = participants[0]
            for device in devices:
                device.device_participants.append(part)
            self.db.session.commit()

            # Set project inactive
            TeraProject.update(new_project.id_project, {'project_enabled': False})

            # Check if participants are inactive
            for part in participants:
                self.assertFalse(part.participant_enabled)

            # Check that associated devices are not anymore
            for device in devices:
                self.assertEqual([], device.device_participants)
