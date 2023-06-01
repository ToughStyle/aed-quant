# -*- coding:utf-8 -*-

"""
Asset module.

Author: CyberQuant
Date:   2023/06/01
Email:  cyberquant@outlook.com
"""

import json


class Asset:
    """ Asset object.

    Args:
        platform: Exchange platform name, e.g. binance/bitmex.
        account: Trade account name, e.g. test@gmail.com.
        assets: Asset information, e.g. {"BTC": {"free": "1.1", "locked": "2.2", "total": "3.3"}, ... }
        timestamp: Published time, millisecond.
        update: If any update? True or False.
    """

    def __init__(self, platform=None, account=None, assets=None, timestamp=None, update=False):
        """ Initialize. """
        self.platform = platform
        self.account = account
        self.assets = assets
        self.timestamp = timestamp
        self.update = update

    @property
    def data(self):
        d = {
            "platform": self.platform,
            "account_id": self.account,
            "assets": self.assets,
            "timestamp": self.timestamp,
            "update": self.update
        }
        return d

    def __str__(self):
        info = json.dumps(self.data)
        return info

    def __repr__(self):
        return str(self)


class AssetSubscribe:
    """ Subscribe Asset.

    Args:
        platform: Exchange platform name, e.g. binance/bitmex.
        account: Trade account name, e.g. test@gmail.com.
        callback: Asynchronous callback function for market data update.
                e.g. async def on_event_account_id_update(asset: Asset):
                        pass
    """

    def __init__(self, platform, account, callback):
        """ Initialize. """
        if platform == "#" or account == "#":
            multi = True
        else:
            multi = False
        from aed_quant.event import EventAsset
        EventAsset(platform, account).subscribe(callback, multi)
