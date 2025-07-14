from loguru import logger
import os
import sys
from dotenv import load_dotenv
log_dir = os.path.join(os.path.dirname(__file__), "logs")
app_log_dir = os.path.join(log_dir, "app")
error_log_dir = os.path.join(log_dir, "error")
access_log_dir = os.path.join(log_dir, "access")
load_dotenv()

os.makedirs(app_log_dir, exist_ok=True)
os.makedirs(error_log_dir, exist_ok=True)
os.makedirs(access_log_dir, exist_ok=True)

logger.remove()

logger.add(os.path.join(app_log_dir,"{time:DD-MM-YYYY}.log"),
        level="INFO",
        rotation='1 day',
        retention='7 days',
        compression='zip',
        format="{time:DD-MM-YYYY HH:mm:ss} | {level} | {message}"
      )
    
logger.add(os.path.join(error_log_dir,"{time:DD-MM-YYYY}.log"),
           level="ERROR",
           retention='30 days',
           rotation='1 day',
           compression='zip',
           format="{time:DD-MM-YYYY HH:mm:ss} | {level} | {message} | {exception}",
           backtrace=True,
           diagnose=True,
            )


logger.add(os.path.join(access_log_dir, "access_{time:YYYY-MM-DD}.log"), 
           level="INFO", 
           rotation="1 day", 
           retention="30 days", 
           compression="zip", 
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
           backtrace=True,
           diagnose=True
           )


if os.getenv("ENV",'development')=='development':
    logger.add(sys.stderr,level="DEBUG", format="{time:DD-MM-YYYY} | {level}| {message}")
__all__ = ["logger"]