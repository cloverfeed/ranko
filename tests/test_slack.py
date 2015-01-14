from unittest import TestCase

from app.factory import configure_logging
from app.factory import create_app


class SlackTestCase(TestCase):
    """
    This test case inherits from plain unittest.TestCase
    because we need to instanciate apps.
    """

    def test_loggers(self):
        app = create_app(config_file='conf/testing.py')
        self.assertEqual(len(app.logger.handlers), 1)
        extra_config = {'SLACK_API_TOKEN': 'token',
                        'SLACK_CHANNEL': '#general',
                        'SLACK_USERNAME': 'Bobby the bot',
                        'SLACK_ICON_URL': 'whatever',
                        }
        app.config.update(extra_config)
        configure_logging(app)
        self.assertEqual(len(app.logger.handlers), 2)
