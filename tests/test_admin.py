from app.models import ROLE_ADMIN
from app.models import User
from common import RankoTestCase


class AdminTestCase(RankoTestCase):
    def test_admin_unauthorized_guest(self):
        self.assertFalse(self._can_see_admin_panel())

    def test_admin_unauthorized_user(self):
        self._login('a', 'a', signup=True)
        self.assertFalse(self._can_see_admin_panel())

    def test_admin_authorized_admin(self):
        self._login('a', 'a', signup=True)
        user = User.query.one()
        user.role = ROLE_ADMIN
        self.assertTrue(self._can_see_admin_panel())

    def _can_see_admin_panel(self):
        r = self.client.get('/admin/')
        self.assert200(r)
        return 'Document' in r.data
