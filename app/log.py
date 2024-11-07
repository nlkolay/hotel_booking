import logging
from datetime import datetime, timezone

from logtail import LogtailHandler
from pythonjsonlogger import jsonlogger

from app.config import settings

logger = logging.getLogger()

handler = logging.StreamHandler() # To terminal or Sentry

# handler = LogtailHandler(source_token=settings.BETTER_STACK_TOKEN) #  To Better Stack
logger.handlers = []


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            log_record["timestamp"] = now
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname


formatter = CustomJsonFormatter(
    "%(timestamp)s %(level)s %(message)s %(module)s %(funcName)s"
)

handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(settings.LOG_LEVEL)
