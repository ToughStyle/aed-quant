# -*- coding:utf-8 -*-

"""
Market module.

Author: CyberQuant
Date:   2023/06/01
Email:  cyberquant@outlook.com
"""

import json

from aed_quant import const
from aed_quant.utils import logger


class Orderbook:
	""" Orderbook object.

	Args:
		platform: Exchange platform name, e.g. binance/bitmex.
		symbol: Trade pair name, e.g. ETH/BTC.
		asks: Asks list, e.g. [[vwm, quantity], [...], ...]
		bids: Bids list, e.g. [[vwm, quantity], [...], ...]
		timestamp: Update time, millisecond.
	"""

	def __init__(self, platform=None, symbol=None, asks=None, bids=None, timestamp=None):
		""" Initialize. """
		self.platform = platform
		self.symbol = symbol
		self.asks = asks
		self.bids = bids
		self.timestamp = timestamp

	@property
	def data(self):
		d = {
			"platform": self.platform,
			"symbol": self.symbol,
			"asks": self.asks,
			"bids": self.bids,
			"timestamp": self.timestamp
		}
		return d

	def __str__(self):
		info = json.dumps(self.data)
		return info

	def __repr__(self):
		return str(self)


class Trade:
	""" Trade object.

	Args:
		platform: Exchange platform name, e.g. binance/bitmex.
		symbol: Trade pair name, e.g. ETH/BTC.
		action: Trade action, BUY or SELL.
		price: Order place vwm.
		quantity: Order place quantity.
		timestamp: Update time, millisecond.
	"""

	def __init__(self, platform=None, symbol=None, action=None, price=None, quantity=None, timestamp=None):
		""" Initialize. """
		self.platform = platform
		self.symbol = symbol
		self.action = action
		self.price = price
		self.quantity = quantity
		self.timestamp = timestamp

	@property
	def data(self):
		d = {
			"platform": self.platform,
			"symbol": self.symbol,
			"action": self.action,
			"vwm": self.price,
			"quantity": self.quantity,
			"timestamp": self.timestamp
		}
		return d

	def __str__(self):
		info = json.dumps(self.data)
		return info

	def __repr__(self):
		return str(self)


class Kline:
	""" Kline object.

	Args:
		platform: Exchange platform name, e.g. binance/bitmex.
		symbol: Trade pair name, e.g. ETH/BTC.
		open: Open vwm.
		high: Highest vwm.
		low: Lowest vwm.
		close: Close vwm.
		volume: Total trade volume.
		timestamp: Update time, millisecond.
		kline_type: Kline type name, kline - 1min, kline_5min - 5min, kline_15min - 15min.
	"""

	def __init__(self, platform=None, symbol=None, open=None, high=None, low=None, close=None, volume=None,
	             buy_volume=None, quote=None, buy_quote=None, timestamp=None, kline_type=None, is_closed=False):
		""" Initialize. """
		self.platform = platform
		self.symbol = symbol
		self.open = open
		self.high = high
		self.low = low
		self.close = close
		self.volume = volume
		self.buy_volume = buy_volume
		self.quote = quote
		self.buy_quote = buy_quote
		self.timestamp = timestamp
		self.kline_type = kline_type
		self.is_closed = is_closed

	@property
	def data(self):
		d = {
			"platform": self.platform,
			"symbol": self.symbol,
			"open": self.open,
			"high": self.high,
			"low": self.low,
			"close": self.close,
			"volume": self.volume,
			"buy_volume": self.buy_volume,
			"quote": self.quote,
			"buy_quote": self.buy_quote,
			"timestamp": self.timestamp,
			"kline_type": self.kline_type,
			"is_closed": self.is_closed
		}
		return d

	def __str__(self):
		info = json.dumps(self.data)
		return info

	def __repr__(self):
		return str(self)


class MarketSubscriber:
	""" Subscribe Market.

	Args:
		market_type: Market data type,
			MARKET_TYPE_TRADE = "trade"
			MARKET_TYPE_ORDERBOOK = "orderbook"
			MARKET_TYPE_KLINE = "kline"
			MARKET_TYPE_KLINE_5M = "kline_5m"
			MARKET_TYPE_KLINE_15M = "kline_15m"
		platform: Exchange platform name, e.g. binance/bitmex.
		symbol: Trade pair name, e.g. ETH/BTC.
		callback: Asynchronous callback function for market data update.
				e.g. async def on_event_kline_update(kline: Kline):
						pass
	"""

	def __init__(self, market_type, platform, symbol, callback):
		""" Initialize. """
		if platform == "#" or symbol == "#":
			multi = True
		else:
			multi = False
		if market_type == const.MARKET_TYPE_ORDERBOOK:
			from aed_quant.event import EventOrderbook
			EventOrderbook(platform, symbol).subscribe(callback, multi)
		elif market_type == const.MARKET_TYPE_TRADE:
			from aed_quant.event import EventTrade
			EventTrade(platform, symbol).subscribe(callback, multi)
		elif market_type in [const.MARKET_TYPE_KLINE, const.MARKET_TYPE_KLINE_1M, const.MARKET_TYPE_KLINE_3M, const.MARKET_TYPE_KLINE_5M, const.MARKET_TYPE_KLINE_15M]:
			from aed_quant.event import EventKline
			EventKline(platform, symbol, kline_type=market_type).subscribe(callback, multi)
		else:
			logger.error("market_type error:", market_type, caller=self)
