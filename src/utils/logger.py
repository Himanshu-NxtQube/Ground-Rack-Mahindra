import logging
import logging.config
import os

LOG_DIR = "output/logs"
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logging(env: str = "dev"):
    logging.config.fileConfig(f"configs/logging-{env}.conf", disable_existing_loggers=False)

def get_logger(name: str):
    return logging.getLogger(name)