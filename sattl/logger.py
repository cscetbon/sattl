import logging
from datetime import datetime
from pythonjsonlogger import jsonlogger

logger: logging.Logger = None


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            # this doesn't use record.created, so it is slightly off
            log_record['timestamp'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        log_record['level'] = log_record.get('levelname', record.levelname).upper()


def setup_logging():
    global logger
    logger = logging.getLogger()
    logger.setLevel('INFO')
    formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
    handler = logging.StreamHandler()
    handler.setLevel('INFO')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
