# -*- coding:utf-8 -*-

"""
Config module.

Author: CyberQuant
Date:   2023/06/01
Email:  cyberquant@outlook.com
"""

import json

from aed_quant.utils import tools


class Config:
    """ Config module will load a json file like `config.json` and parse the content to json object.
        1. Configure content must be key-value pair, and `key` will be set as Config module's attributes;
        2. Invoking Config module's attributes cat get those values;
        3. Some `key` name is upper case are the build-in, and all `key` will be set to lower case:
            SERVER_ID: Server id, every running process has a unique id.
            LOG: Logger print config.
            RABBITMQ: RabbitMQ config, default is None.
            ACCOUNTS: Trading Exchanges config list, default is [].
            MARKETS: Market Server config list, default is {}.
            HEARTBEAT: Server heartbeat config, default is {}.
            PROXY: HTTP proxy config, default is None.
    """

    def __init__(self):
        self.server_id = None
        self.log = {}
        self.rabbitmq = {}
        self.accounts = []
        self.market_stream = {}
        self.heartbeat = {}
        self.proxy = None

    def loads(self, config_file=None):
        """ Load config file.

        Args:
            config_file: config dict or json filepath.
        """
        if isinstance(config_file, dict):
            self._update(config_file)
            return
        
        configures = {}
        if isinstance(config_file, str):
            try:
                with open(config_file) as f:
                    data = f.read()
                    configures = json.loads(data)
            except Exception as e:
                print(e)
                exit(0)
            if not configures:
                print("config json file error!")
                exit(0)
        self._update(configures)

    def _update(self, update_fields):
        """ Update config attributes.

        Args:
            update_fields: Update fields.
        """
        self.server_id = update_fields.get("SERVER_ID", tools.get_uuid1())
        self.log = update_fields.get("LOG", {})
        self.rabbitmq = update_fields.get("RABBITMQ", None)
        self.accounts = update_fields.get("ACCOUNTS", [])
        self.market_stream = update_fields.get("MARKETS", {})
        self.heartbeat = update_fields.get("HEARTBEAT", {})
        self.proxy = update_fields.get("PROXY", None)

        for k, v in update_fields.items():
            setattr(self, k, v)


config = Config()
