# https://github.com/mathiasose/slack_log_handler/blob/6bf12565f8e5242decc13a54ef82b1d89fabab18/slack_log_handler/__init__.py
import traceback
from logging import Handler

from slacker import Chat


class SlackLogHandler(Handler):
    def __init__(self, api_key, channel, stack_trace=False, username='Python logger', icon_url=None, icon_emoji=None):
        Handler.__init__(self)
        self.slack_chat = Chat(api_key)
        self.channel = channel
        self.stack_trace = stack_trace
        self.username = username
        self.icon_url = icon_url
        self.icon_emoji = icon_emoji if (icon_emoji or icon_url) else ':heavy_exclamation_mark:'

        if not self.channel.startswith('#'):
            self.channel = '#' + self.channel

    def emit(self, record):
        message = '{}'.format(record.getMessage())
        if self.stack_trace and record.exc_info:
            message += '\n'
            message += '\n'.join(traceback.format_exception(*record.exc_info))

        self.slack_chat.post_message(
            text=message,
            channel=self.channel,
            username=self.username,
            icon_url=self.icon_url,
            icon_emoji=self.icon_emoji
        )
