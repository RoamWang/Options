
from QuantLib import *

#instrumentid 合约代码
#option_class 期权类型 CALL PUT
#strike_price 行权价
#expire_date 到期日
#underlying_last_price 标的资产最新价格
#market_price 市场价格(买一价+卖一价)/2
def greek_func(instrumentid, option_class, strike_price, expire_date, underlying_last_price, market_price):
    calculation_date = Date(7, 7, 2025)
    Settings.instance().evaluationDate = calculation_date
    expiration_date = expire_date
    option_type = Option.Call if option_class == "CALL" else Option.Put
    # 无风险利率
    risk_free_rate = 0.03               
    # 商品期货无股息
    dividend_rate = 0.00

    # 2. 构建贴现曲线
    yield_curve = FlatForward(calculation_date, risk_free_rate, Actual365Fixed())
    dividend_curve = FlatForward(calculation_date, dividend_rate, Actual365Fixed())

    # 3. 标的资产随机过程
    spot_handle = QuoteHandle(SimpleQuote(underlying_last_price))
    process = BlackScholesMertonProcess(
        spot_handle,
        YieldTermStructureHandle(dividend_curve),
        YieldTermStructureHandle(yield_curve),
        BlackVolTermStructureHandle(
            BlackConstantVol(calculation_date, NullCalendar(), 0.20, Actual365Fixed())
        )
    )

    # 4. 期权对象构建
    payoff = PlainVanillaPayoff(option_type, strike_price)
    exercise = EuropeanExercise(expiration_date)
    option = EuropeanOption(payoff, exercise)

    # 5. 计算隐含波动率
    implied_vol = 0
    try:
        implied_vol = option.impliedVolatility(market_price, process, 1e-6, 100)
    except Exception as e:
        implied_vol = 0


    process = BlackScholesMertonProcess(
        spot_handle,
        YieldTermStructureHandle(dividend_curve),
        YieldTermStructureHandle(yield_curve),
        BlackVolTermStructureHandle(
            BlackConstantVol(calculation_date, NullCalendar(), implied_vol, Actual365Fixed())
        )
    )

    # 6. 重新设置定价引擎计算希腊值
    option.setPricingEngine(AnalyticEuropeanEngine(process))

    # 7. 结果输出
    # print(f"期权合约: {instrumentid}")
    # print(f"最新价格: {last_price:.2f}")
    # print(f"市场价格: {market_price:.2f}")
    # print(f"隐含波动率: {implied_vol*100:.2f}%")
    # print(f"Delta: {option.delta():.4f}")
    # print(f"Gamma: {option.gamma():.6f}")
    # print(f"理论价格: {option.NPV():.2f}元/吨")
    # print("------------------------------------------------")
    print(f"合约: {instrumentid}, 标的最新价: {underlying_last_price:.2f}, 市场价: {market_price:.2f}, 隐含波动率: {implied_vol*100:.2f}%, Delta: {option.delta():.4f}, Gamma: {option.gamma():.6f}, 理论价格: {option.NPV():.2f}元/吨")

