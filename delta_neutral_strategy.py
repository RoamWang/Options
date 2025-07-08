import ccxt
import time

# 初始化 Binance 交易所实例
binance = ccxt.binance({
                'proxies': {'http': 'http://localhost:7897','https': 'http://localhost:7897'},
                'enableRateLimit':True,
                'options': {
        'defaultType': 'option'  # 指定为期货市场
    }
            })

binance.load_markets()


# 获取 Delta 和价格数据
def fetch_option_data(symbol):
    try:
        greeks = binance.fetch_greeks(symbol, params={'type': 'option'})
        ticker = binance.fetch_ticker(symbol, params={'type': 'option'})
        return {
            'symbol': symbol,
            'delta': greeks['delta'],
            'mark_price': greeks['markPrice'],
            'last_price': ticker['last']
        }
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

# Delta 中性组合
def delta_neutral_strategy(instrumentid, underlying_instrumentid):
    #现货行情
    quote = binance.fetch_ticker(underlying_instrumentid)
    #期权行情(包含希腊字母)
    quote_option = fetch_option_data(instrumentid)
    
    if not quote_option or not quote:
        print("Failed to fetch quote.")
        return
    
    # 假设持有 1 张看涨期权（每张期权对应 1 BTC）
    volume_option = 1
    total_delta = quote_option['delta'] * volume_option    
    print(f"position_option: {instrumentid}, Delta: {quote_option['delta']}, Total Delta: {total_delta}")
    
    # 计算对冲所需的现货或期货数量（负 Delta 表示卖出正向资产）
    hedge_quantity = -total_delta
    print(f"Hedge Quantity: {hedge_quantity} BTC (positive = buy, negative = sell)")    

    spot_price = quote['last']
    
    # 执行下单交易（仅打印订单信息）
    if hedge_quantity > 0:
        print(f"Place BUY order for {hedge_quantity} BTC at {spot_price} USDT")
    elif hedge_quantity < 0:
        print(f"Place SELL order for {abs(hedge_quantity)} BTC at {spot_price} USDT")
    

    #期权持仓价值
    option_value = quote_option['last_price'] * volume_option
    #现货持仓价值
    spot_value = hedge_quantity * spot_price

    total_value = option_value + spot_value
    print(f"Portfolio Value: {total_value} USDT")
    print(f"Portfolio Delta: {total_delta + hedge_quantity:.6f} (should be close to 0)")


# 执行 Delta 中性策略
try:
    instrumentid = 'BTC-250709-110000-C'
    underlying_instrumentid = 'BTC/USDT'
    delta_neutral_strategy(instrumentid, underlying_instrumentid)
except Exception as e:
    print(f"Error executing strategy: {e}")
