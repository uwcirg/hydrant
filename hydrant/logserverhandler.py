import json
import logging
import requests
from requests.exceptions import RequestException


class LogServerHandler(logging.Handler):
    """Specialized logging handler capable of nesting json and passing auth"""

    def __init__(self, url, jwt, level):
        super().__init__(level)
        self.jwt = jwt
        self.url = f"{url}/events"

    def emit(self, record):
        log_entry = self.format(record)
        log_entry = {"event": json.loads(log_entry)}
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.jwt}"
        }
        try:
            response = requests.post(url=self.url, headers=headers, json=log_entry)
            response.raise_for_status()
        except RequestException as ex:
            # bootstrap problems - attemtp to log to root logger
            root_logger = logging.getLogger('root')
            root_logger.exception(ex)
