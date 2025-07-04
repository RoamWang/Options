
from QuantLib import *

# 1. 合约参数初始化
calculation_date = Date(4, 7, 2025)
Settings.instance().evaluationDate = calculation_date
expiration_date = Date(25, 7, 2025)  # 2025年8月到期
strike_price = 78000.0              # 行权价82,000元/吨
option_type = Option.Call           # 看涨期权
spot_price = 79730.0                # 标的期货最新价
market_price = 2180.0                # 期权市场中间价
risk_free_rate = 0.03               # 无风险利率
dividend_rate = 0.00                # 商品期货无股息

# 2. 构建贴现曲线
yield_curve = FlatForward(calculation_date, risk_free_rate, Actual365Fixed())
dividend_curve = FlatForward(calculation_date, dividend_rate, Actual365Fixed())

# 3. 标的资产随机过程
spot_handle = QuoteHandle(SimpleQuote(spot_price))
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
implied_vol = option.impliedVolatility(market_price, process, 1e-6, 100)

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
print(f"期权合约: cu2508C78000")
print(f"隐含波动率: {implied_vol*100:.2f}%")
print(f"Delta: {option.delta():.4f}")
print(f"Gamma: {option.gamma():.6f}")
print(f"理论价格: {option.NPV():.2f}元/吨")
