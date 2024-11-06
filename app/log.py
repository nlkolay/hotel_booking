# Configure logging
import logging
from app.config import settings


logging.basicConfig(level=settings.LOG_LEVEL)
# logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
logger = logging.getLogger()

# Create a handler (e.g., to write logs to a file)
handler = logging.FileHandler("my_app.log")
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

# Add the handler to the logger
# logger.addHandler(handler)
