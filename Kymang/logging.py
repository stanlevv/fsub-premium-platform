import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter("[%(levelname)s] - %(name)s - %(message)s", "%d-%b %H:%M")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)

logging.getLogger("hydrogram").setLevel(logging.WARNING)
logging.getLogger("hydrogram.client").setLevel(logging.WARNING)
logging.getLogger("hydrogram.session.auth").setLevel(logging.CRITICAL)
logging.getLogger("hydrogram.session.session").setLevel(logging.CRITICAL)

LOGS = logging.getLogger(__name__)

