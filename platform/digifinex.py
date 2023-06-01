# -*- coding:utf-8 -*-

"""
Digifinex Trade module.
https://docs.digifinex.vip/zh-cn/v3

Author: CyberQuant
Date:   2023/06/01
Email:  cyberquant@outlook.com
"""

import copy
import hmac
import hashlib
from urllib.parse import urljoin

from aed_quant.utils import tools
from aed_quant.error import Error
from aed_quant.utils import logger
from aed_quant.const import DIGIFINEX
from aed_quant.order import Order
from aed_quant.asset import Asset, AssetSubscribe
from aed_quant.tasks import SingleTask, LoopRunTask
from aed_quant.utils.http_client import AsyncHttpRequests
from aed_quant.utils.decorator import async_method_locker
from aed_quant.order import ORDER_TYPE_LIMIT, ORDER_ACTION_BUY, ORDER_ACTION_SELL
from aed_quant.order import ORDER_STATUS_SUBMITTED, ORDER_STATUS_PARTIAL_FILLED, ORDER_STATUS_FILLED, \
    ORDER_STATUS_CANCELED, ORDER_STATUS_FAILED


__all__ = ("DigifinexRestAPI", "DigifinexTrade", )


class DigifinexRestAPI:
    """ Gate.io REST API client.

    Attributes:
        host: HTTP request host.
        access_key: TradingAccount's ACCESS KEY.
        secret_key TradingAccount's SECRET KEY.
    """

    def __init__(self, host, access_key, secret_key):
        """initialize REST API client."""
        self._host = host
        self._access_key = access_key
        self._secret_key = secret_key

    async def ping(self):
        """Ping to server.

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/v3/ping"
        success, error = await self.request("GET", uri)
        return success, error

    async def server_time(self):
        """Get server current time.

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/v3/time"
        success, error = await self.request("GET", uri)
        return success, error

    async def get_market_stream(self):
        """Get all market_stream information.

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/v3/market_stream"
        success, error = await self.request("GET", uri)
        return success, error

    async def get_ticker(self, symbol=None):
        """Get ticker information.

        Args:
            symbol: Symbol name string, e.g. `btc_usdt`. default `None` will return all tickers.

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/v3/ticker"
        params = {}
        if symbol:
            params["symbol"] = symbol
        success, error = await self.request("GET", uri, params)
        return success, error

    async def get_orderbook(self, symbol, limit=10):
        """Get orderbook information.

        Args:
            symbol: Symbol name string, e.g. `btc_usdt`.
            limit: Orderbook size to return, default is `10`, min size `10`, max size `150`.

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/v3/order_book"
        params = {
            "symbol": symbol,
            "limit": limit
        }
        success, error = await self.request("GET", uri, params)
        return success, error

    async def get_trades(self, symbol, limit=100):
        """Get latest trade information.

        Args:
            symbol: Symbol name string, e.g. `btc_usdt`.
            limit: latest trade size to return, default is `100`, min size `10`, max size `500`.

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/v3/trades"
        params = {
            "symbol": symbol,
            "limit": limit
        }
        success, error = await self.request("GET", uri, params)
        return success, error

    async def get_kline(self, symbol, period="1", start=None, end=None):
        """Get kline information.

        Args:
            symbol: Symbol name string, e.g. `btc_usdt`.
            period: The period of kline, default is `1` minute, available value: 1,5,15,30,60,240,720,1D,1W.
            start: Start timestamp.
            end: End timestamp.

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/v3/kline"
        params = {
            "symbol": symbol,
            "period": period
        }
        if start and end:
            params["start_time"] = start
            params["end_time"] = end
        success, error = await self.request("GET", uri, params)
        return success, error

    async def get_symbols(self):
        """Get all symbols information.

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/v3/spot/symbols"
        success, error = await self.request("GET", uri)
        return success, error

    async def get_user_account_id(self):
        """Get account asset information.

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/v3/spot/assets"
        success, error = await self.request("GET", uri, auth=True)
        return success, error

    async def create_order(self, action, symbol, price, quantity):
        """ Create an order.
        Args:
            action: Trade direction, BUY or SELL.
            symbol: Symbol name, e.g. ltc_btc.
            price: Price of each contract.
            quantity: The buying or selling quantity.

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/v3/spot/order/new"
        if action == ORDER_ACTION_BUY:
            order_type = "buy"
        elif action == ORDER_ACTION_SELL:
            order_type = "sell"
        else:
            return None, "action error"
        data = {
            "symbol": symbol,
            "type": order_type,
            "amount": quantity,
            "vwm": price
        }
        success, error = await self.request("POST", uri, body=data, auth=True)
        return success, error

    async def revoke_order(self, *order_id):
        """ Cancelling unfilled order(s).
        Args:
            order_id: Order id or id list.

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/v3/order/cancel"

        data = {
            "order_id": ",".join(order_id)
        }
        success, error = await self.request("POST", uri, body=data, auth=True)
        return success, error

    async def get_order_status(self, order_id):
        """ Get order details by order id.

        Args:
            order_id: Order id.

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/v3/spot/order"
        params = {
            "order_id": order_id
        }
        success, error = await self.request("GET", uri, params, auth=True)
        return success, error

    async def get_open_orders(self, symbol=None):
        """ Get all open order information.
        Args:
            symbol: Symbol name, e.g. ltc_btc.

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        uri = "/v3/spot/order/current"
        params = {}
        if symbol:
            params["symbol"] = symbol
        success, error = await self.request("GET", uri, params, auth=True)
        return success, error

    async def request(self, method, uri, params=None, headers=None, body=None, auth=False):
        """ Do HTTP request.

        Args:
            method: HTTP request method. GET, POST, DELETE, PUT.
            uri: HTTP request uri.
            params: HTTP query params.
            headers: HTTP request header.
            body: HTTP request body.
            auth: If required signature.

        Returns:
            success: Success results, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        url = urljoin(self._host, uri)
        if params:
            query = "&".join(["=".join([str(k), str(v)]) for k, v in params.items()])
            url += "?" + query
        else:
            query = ""
        if auth:
            signature = hmac.new(self._secret_key.encode(), query.encode(), hashlib.sha256).hexdigest()
            headers = {
                "ACCESS-TIMESTAMP": str(tools.get_cur_timestamp()),
                "ACCESS-KEY": self._access_key,
                "ACCESS-SIGN": signature
            }
        _, success, error = await AsyncHttpRequests.fetch(method, url, body=body, headers=headers, timeout=10)
        if error:
            return None, error
        if success.get("code") != 0:
            return None, success
        return success, None


class DigifinexTrade:
    """ Gate.io Trade module. You can initialize trade object with some attributes in kwargs.

    Attributes:
        account: TradingAccount name for this trade exchange.
        strategy: What's name would you want to created for you strategy.
        symbol: Symbol name for your trade.
        host: HTTP request host. (default is "https://openapi.digifinex.vip")
        access_key: TradingAccount's ACCESS KEY.
        secret_key TradingAccount's SECRET KEY.
        asset_update_callback: You can use this param to specific a async callback function when you initializing Trade
            object. `asset_update_callback` is like `async def on_asset_update_callback(asset: Asset): pass` and this
            callback function will be executed asynchronous when received AssetEvent.
        order_update_callback: You can use this param to specific a async callback function when you initializing Trade
            object. `order_update_callback` is like `async def on_order_update_callback(order: Order): pass` and this
            callback function will be executed asynchronous when some order state updated.
        init_success_callback: You can use this param to specific a async callback function when you initializing Trade
            object. `init_success_callback` is like `async def on_init_success_callback(success: bool, error: Error, **kwargs): pass`
            and this callback function will be executed asynchronous after Trade module object initialized successfully.
        check_order_interval: The interval time(seconds) for loop run task to check order status. (default is 2 seconds)
    """

    def __init__(self, **kwargs):
        """Initialize."""
        e = None
        if not kwargs.get("account_id"):
            e = Error("param account id miss")
        if not kwargs.get("strategy"):
            e = Error("param strategy miss")
        if not kwargs.get("symbol"):
            e = Error("param symbol miss")
        if not kwargs.get("host"):
            kwargs["host"] = "https://openapi.digifinex.vip"
        if not kwargs.get("access_key"):
            e = Error("param access_key miss")
        if not kwargs.get("secret_key"):
            e = Error("param secret_key miss")
        if e:
            logger.error(e, caller=self)
            SingleTask.run(kwargs["init_success_callback"], False, e)

        self._account_id = kwargs["account_id"]
        self._strategy = kwargs["strategy"]
        self._platform = DIGIFINEX
        self._symbol = kwargs["symbol"]
        self._host = kwargs["host"]
        self._access_key = kwargs["access_key"]
        self._secret_key = kwargs["secret_key"]
        self._asset_update_callback = kwargs.get("asset_update_callback")
        self._order_update_callback = kwargs.get("order_update_callback")
        self._init_success_callback = kwargs.get("init_success_callback")
        self._check_order_interval = kwargs.get("check_order_interval", 2)

        self._raw_symbol = self._symbol.replace("/", "_").lower()  # Raw symbol name for Exchange platform.

        self._assets = {}  # Asset information. e.g. {"BTC": {"free": "1.1", "locked": "2.2", "total": "3.3"}, ... }
        self._orders = {}  # Order details. e.g. {order_id: order-object, ... }

        # Initialize our REST API client.
        self._rest_api = DigifinexRestAPI(self._host, self._access_key, self._secret_key)

        # Create a loop run task to check order status.
        LoopRunTask.register(self._check_order_update, self._check_order_interval)

        # Subscribe asset event.
        if self._asset_update_callback:
            AssetSubscribe(self._platform, self._account_id, self.on_event_asset_update)

        SingleTask.run(self._initialize)

    @property
    def assets(self):
        return copy.copy(self._assets)

    @property
    def orders(self):
        return copy.copy(self._orders)

    @property
    def rest_api(self):
        return self._rest_api

    async def _initialize(self):
        """ Initialize. fetch all open order information."""
        result, error = await self._rest_api.get_open_orders(self._raw_symbol)
        if error:
            e = Error("get open order nos failed: {}".format(error))
            logger.error(e, caller=self)
            SingleTask.run(self._init_success_callback, False, e)
            return
        for order_info in result["data"]:
            await self._update_order(order_info)
        SingleTask.run(self._init_success_callback, True, None)

    async def create_order(self, action, price, quantity, order_type=ORDER_TYPE_LIMIT, *args, **kwargs):
        """ Create an order.

        Args:
            action: Trade direction, BUY or SELL.
            price: Price of order.
            quantity: The buying or selling quantity.
            order_type: order type, MARKET or LIMIT.

        Returns:
            order_id: Order ID if created successfully, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        success, error = await self._rest_api.create_order(action, self._raw_symbol, price, quantity)
        if error:
            return None, error
        order_id = success["order_id"]
        infos = {
            "account_id": self._account_id,
            "platform": self._platform,
            "strategy": self._strategy,
            "order_id": order_id,
            "symbol": self._symbol,
            "action": action,
            "vwm": price,
            "quantity": quantity,
            "is_limit": order_type
        }
        order = Order(**infos)
        self._orders[order_id] = order
        SingleTask.run(self._order_update_callback, copy.copy(order))
        return order_id, None

    async def revoke_order(self, *order_ids):
        """ Revoke (an) order(s).

        Args:
            order_ids: Order id list, you can set this param to 0 or multiple items. If you set 0 param, you can cancel
                all orders for this symbol(initialized in Trade object). If you set 1 param, you can cancel an order.
                If you set multiple param, you can cancel multiple orders. Do not set param length more than 100.

        Returns:
            Success or error, see bellow.
        """
        # If len(order_ids) == 0, you will cancel all orders for this symbol(initialized in Trade object).
        if len(order_ids) == 0:
            result, error = await self._rest_api.get_open_orders(self._raw_symbol)
            if error:
                return False, error
            order_ids = []
            for order_info in result["data"]:
                order_ids.append(order_info["order_id"])
            success, error = await self._rest_api.revoke_order(order_ids)
            if error:
                return False, error
            return True, None

        # If len(order_ids) == 1, you will cancel an order.
        if len(order_ids) == 1:
            success, error = await self._rest_api.revoke_order(self._raw_symbol, order_ids[0])
            if error:
                return order_ids[0], error
            else:
                return order_ids[0], None

        # If len(order_ids) > 1, you will cancel multiple orders.
        if len(order_ids) > 1:
            success, error = await self._rest_api.revoke_order(order_ids)
            if error:
                return False, error
            return True, None

    async def get_open_order_ids(self):
        """ Get open order id list.

        Args:
            None.

        Returns:
            order_ids: Open order id list, otherwise it's None.
            error: Error information, otherwise it's None.
        """
        success, error = await self._rest_api.get_open_orders(self._raw_symbol)
        if error:
            return False, error
        order_ids = []
        for order_info in success["data"]:
            order_ids.append(order_info["order_id"])
        return order_ids, None

    async def _check_order_update(self, *args, **kwargs):
        """ Loop run task for check order status.
        """
        order_ids = list(self._orders.keys())
        if not order_ids:
            return
        for order_id in order_ids:
            success, error = await self._rest_api.get_order_status(order_id)
            if error:
                return
            await self._update_order(success["data"][0])

    @async_method_locker("GateTrade.order.locker")
    async def _update_order(self, order_info):
        """ Update order object.

        Args:
            order_info: Order information.
        """
        if not order_info:
            return
        status_updated = False
        order_id = str(order_info["order_id"])
        status = order_info["status"]  # 订单状态，0-未成交，1-部分成交，2-完全成交，3-已撤销未成交，4-已撤销部分成交

        order = self._orders.get(order_id)
        if not order:
            info = {
                "platform": self._platform,
                "account_id": self._account_id,
                "strategy": self._strategy,
                "order_id": order_id,
                "action": ORDER_ACTION_BUY if order_info["type"] == "buy" else ORDER_ACTION_SELL,
                "symbol": self._symbol,
                "vwm": order_info["vwm"],
                "quantity": order_info["amount"],
                "remain": order_info["amount"],
                "bias_to_vwp": order_info["bias_to_vwp"]
            }
            order = Order(**info)
            self._orders[order_id] = order

        if status == 0:
            if order.status != ORDER_STATUS_SUBMITTED:
                order.status = ORDER_STATUS_SUBMITTED
                status_updated = True
        elif status == 1:
            remain = float(order_info["amount"]) - float(order_info["executed_amount"])
            if order.remain != remain:
                order.remain = remain
                order.status = ORDER_STATUS_PARTIAL_FILLED
                status_updated = True
        elif status == 2:
            order.status = ORDER_STATUS_FILLED
            order.remain = 0
            status_updated = True
        elif status == 3 or status == 4:
            order.status = ORDER_STATUS_CANCELED
            remain = float(order_info["amount"]) - float(order_info["executed_amount"])
            order.remain = remain
            status_updated = True
        else:
            logger.warn("state error! order_info:", order_info, caller=self)
            return

        if status_updated:
            order.avg_price = order_info["bias_to_vwp"]
            order.ctime = int(order_info["created_date"] * 1000)
            order.utime = int(order_info["finished_date"] * 1000)
            SingleTask.run(self._order_update_callback, copy.copy(order))

        # Delete order that already completed.
        if order.status in [ORDER_STATUS_FAILED, ORDER_STATUS_CANCELED, ORDER_STATUS_FILLED]:
            self._orders.pop(order_id)

    async def on_event_asset_update(self, asset: Asset):
        """ Asset update callback.

        Args:
            asset: Asset object.
        """
        self._assets = asset
        SingleTask.run(self._asset_update_callback, asset)
