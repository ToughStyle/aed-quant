# -*- coding:utf-8 -*-

"""
Trade Module.

Author: CyberQuant
Date:   2023/06/01
Email:  cyberquant@outlook.com
"""

import copy

from aed_quant import const
from aed_quant.utils import tools
from aed_quant.error import Error
from aed_quant.utils import logger
from aed_quant.tasks import SingleTask
from aed_quant.order import ORDER_TYPE_LIMIT
from aed_quant.order import Order
from aed_quant.position import Position


class Trader:
	""" Trade Module.

	Attributes:
		strategy: What's name would you want to created for your strategy.
		platform: Exchange platform name. e.g. `binance` / `okex` / `bitmex`.
		symbol: Symbol name for your trade. e.g. `BTC/USDT`.
		host: HTTP request host.
		wss: Websocket address.
		account_id: TradingAccount name for this trade exchange.
		access_key: TradingAccount's ACCESS KEY.
		secret_key: TradingAccount's SECRET KEY.
		passphrase: API KEY Passphrase. (Only for `OKEx`)
		asset_update_callback: You can use this param to specific a async callback function when you initializing Trade
			object. `asset_update_callback` is like `async def on_asset_update_callback(asset: Asset): pass` and this
			callback function will be executed asynchronous when received AssetEvent.
		order_update_callback: You can use this param to specific a async callback function when you initializing Trade
			object. `order_update_callback` is like `async def on_order_update_callback(order: Order): pass` and this
			callback function will be executed asynchronous when some order state updated.
		position_update_callback: You can use this param to specific a async callback function when you initializing
			Trade object. `position_update_callback` is like `async def on_position_update_callback(position: Position): pass`
			and this callback function will be executed asynchronous when position updated.
		init_success_callback: You can use this param to specific a async callback function when you initializing Trade
			object. `init_success_callback` is like `async def on_init_success_callback(success: bool, error: Error, **kwargs): pass`
			and this callback function will be executed asynchronous after Trade module object initialized successfully.
	"""
	def __init__(self, strategy=None, platform=None, symbol=None, host=None, wss=None, account_id=None, access_key=None,
				 secret_key=None, passphrase=None, asset_update_callback=None, account_update_callback=None,
				 order_update_callback=None, position_update_callback=None, init_success_callback=None, **kwargs):
		"""initialize trade object."""
		kwargs["strategy"] = strategy
		kwargs["platform"] = platform
		kwargs["symbol"] = symbol
		kwargs["host"] = host
		kwargs["wss"] = wss
		kwargs["account_id"] = account_id
		kwargs["access_key"] = access_key
		kwargs["secret_key"] = secret_key
		kwargs["passphrase"] = passphrase
		kwargs["asset_update_callback"] = asset_update_callback
		kwargs["account_update_callback"] = self._on_account_update_callback
		kwargs["order_update_callback"] = self._on_order_update_callback
		kwargs["position_update_callback"] = self._on_position_update_callback
		kwargs["init_success_callback"] = self._on_init_success_callback

		self._raw_params = copy.copy(kwargs)
		self._account_update_callback = account_update_callback
		self._order_update_callback = order_update_callback
		self._position_update_callback = position_update_callback
		self._init_success_callback = init_success_callback

		if platform == const.OKEX:
			from aed_quant.platform.okex import OKExTrade as T
		elif platform == const.OKEX_MARGIN:
			from aed_quant.platform.okex_margin import OKExMarginTrade as T
		elif platform == const.OKEX_FUTURE:
			from aed_quant.platform.okex_future import OKExFutureTrade as T
		elif platform == const.OKEX_SWAP:
			from aed_quant.platform.okex_swap import OKExSwapTrade as T
		elif platform == const.DERIBIT:
			from aed_quant.platform.deribit import DeribitTrade as T
		elif platform == const.BITMEX:
			from aed_quant.platform.bitmex import BitmexTrade as T
		elif platform == const.BINANCE:
			from aed_quant.platform.binance import BinanceTrade as T
		elif platform == const.BINANCE_FUTURE:
			from aed_quant.platform.binance_future import BinanceFutureTrade as T
		elif platform == const.HUOBI:
			from aed_quant.platform.huobi import HuobiTrade as T
		elif platform == const.COINSUPER:
			from aed_quant.platform.coinsuper import CoinsuperTrade as T
		elif platform == const.COINSUPER_PRE:
			from aed_quant.platform.coinsuper_pre import CoinsuperPreTrade as T
		elif platform == const.KRAKEN:
			from aed_quant.platform.kraken import KrakenTrade as T
		elif platform == const.GATE:
			from aed_quant.platform.gate import GateTrade as T
		elif platform == const.KUCOIN:
			from aed_quant.platform.kucoin import KucoinTrade as T
		elif platform == const.HUOBI_FUTURE:
			from aed_quant.platform.huobi_future import HuobiFutureTrade as T
		elif platform == const.DIGIFINEX:
			from aed_quant.platform.digifinex import DigifinexTrade as T
		else:
			logger.error("platform error:", platform, caller=self)
			e = Error("platform error")
			SingleTask.run(self._init_success_callback, False, e)
			return
		kwargs.pop("platform")
		self._t = T(**kwargs)
		
	@property
	def assets(self):
		return self._t.assets

	@property
	def orders(self):
		return self._t.orders

	@property
	def position(self):
		return self._t.position

	@property
	def rest_api(self):
		return self._t.rest_api

	async def create_order(self, action, price, quantity, order_type=ORDER_TYPE_LIMIT, *args, **kwargs):
		""" Create an order.

		Args:
			action: Trade direction, `BUY` or `SELL`.
			price: Price of each contract.
			quantity: The buying or selling quantity.
			order_type: Specific type of order, `LIMIT` or `MARKET`. (default is `LIMIT`)

		Returns:
			order_id: Order ID if created successfully, otherwise it's None.
			error: Error information, otherwise it's None.
		"""
		if not kwargs.get("client_order_id"):
			kwargs["client_order_id"] = tools.get_uuid1().replace("-", "")
		order_id, error = await self._t.create_order(action, price, quantity, order_type, **kwargs)
		return order_id, error

	async def revoke_order(self, *order_ids):
		""" Revoke (an) order(s).

		Args:
			order_ids: Order id list, you can set this param to 0 or multiple items. If you set 0 param, you can cancel
				all orders for this symbol(initialized in Trade object). If you set 1 param, you can cancel an order.
				If you set multiple param, you can cancel multiple orders. Do not set param length more than 100.

		Returns:
			success: If execute successfully, return success information, otherwise it's None.
			error: If execute failed, return error information, otherwise it's None.
		"""
		success, error = await self._t.revoke_order(*order_ids)
		return success, error

	async def get_open_order_ids(self):
		""" Get open order id list.

		Args:
			None.

		Returns:
			order_ids: Open order id list, otherwise it's None.
			error: Error information, otherwise it's None.
		"""
		result, error = await self._t.get_open_order_ids()
		return result, error
	
	async def _on_account_update_callback(self, account_info: dict):
		""" TradingAccount information update callback.

		Args:
			account_info: TradingAccount information dict.
		"""
		if self._account_update_callback:
			SingleTask.run(self._account_update_callback, account_info)
			
	async def _on_order_update_callback(self, order: Order):
		""" Order information update callback.

		Args:
			order: Order object.
		"""
		if self._order_update_callback:
			SingleTask.run(self._order_update_callback, order)

	async def _on_position_update_callback(self, position: Position):
		""" Position information update callback.

		Args:
			position: Position object.
		"""
		if self._position_update_callback:
			SingleTask.run(self._position_update_callback, position)

	async def _on_init_success_callback(self, success: bool, error: Error):
		""" Callback function when initialize Trade module finished.

		Args:
			success: `True` if initialize Trade module success, otherwise `False`.
			error: `Error object` if initialize Trade module failed, otherwise `None`.
		"""
		if self._init_success_callback:
			params = {
				"strategy": self._raw_params["strategy"],
				"platform": self._raw_params["platform"],
				"symbol": self._raw_params["symbol"],
				"account_id": self._raw_params["account_id"]
			}
			await self._init_success_callback(success, error, **params)
