"""
Main entry point for the Voizy Recommender API
"""
import uvicorn
import logging
import configparser
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

Path("logs").mkdir(exist_ok=True)

config = configparser.ConfigParser()
config_file = Path("recommender_config.ini")
if not config_file.exists():
    logger.error(f"Config file not found: {config_file.absolute()}")
    raise FileNotFoundError(f"Config file not found: {config_file.absolute()}")

config.read(config_file)

api_config = {
    'port': config.getint('API', 'PORT', fallback=5000),
    'host': config.get('API', 'HOST', fallback='0.0.0.0'),
    'reload': config.getboolean('API', 'DEBUG', fallback=False)
}

from voizy.api.server import create_app

app = create_app()

if __name__ == "__main__":
    logger.info(f"Starting Voizy Recommender API on {api_config['host']}:{api_config['port']}")
    uvicorn.run(
        "app:app",
        host=api_config['host'],
        port=api_config['port'],
        reload=api_config['reload']
    )