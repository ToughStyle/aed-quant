from typing import Union

import numpy as np
from pandas import DataFrame
from aed_quant.utils.tools import get_cur_timestamp_ms, ts_to_datetime_str


def parse_history_kline(platform: str, raw_data: Union[list, dict]) -> DataFrame:
	if 'binance' in platform:
		# data = np.array(raw_data, dtype=np.float32)
		columns = [
			"timestamp", "open", "high", "low", "close", "volume", "timestamp_", "quote",
			"trade_count", "buy_volume", "buy_quote", "ignore"]
		df = DataFrame(raw_data, columns=columns)
		n = len(df)
		now_ms = get_cur_timestamp_ms()
		now_str = ts_to_datetime_str(now_ms / 1000)
		last_kline_start_ms = df.timestamp[n - 1]
		last_kline_str = ts_to_datetime_str(last_kline_start_ms / 1000)
		interval_ms = df.timestamp[n - 2] - df.timestamp[n - 3]
		next_kline_to_come_in_sec = (last_kline_start_ms + interval_ms - now_ms) / 1000
		print(f"{next_kline_to_come_in_sec = }")
		df = process_kline(df[: n - 1])
		return df


def process_kline(df: DataFrame) -> DataFrame:
	columns = ['open', 'high', 'low', 'close', 'volume', 'quote']
	if 'buy_volume' in df.columns:
		columns += ['buy_volume', 'buy_quote']
	df = df[columns].astype(np.float32)
	df = df[df['volume'] > 0]
	df.reset_index(inplace=True, drop=True)
	df['bias_to_vwp'] = df['quote'] / df['volume']
	if 'buy_volume' in df.columns:
		df['sell_volume'] = df['volume'] - df['buy_volume']
		df['sell_quote'] = df['quote'] - df['buy_quote']
	return df


def parse_stream_kline(raw_data: Union[list, dict]) -> DataFrame:
	if 'binance' in raw_data.get('platform'):
		return process_kline(DataFrame(raw_data, index=[0]))
		