import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

# 1. PORTFOLIO DATA (from Excel Calculations)
# We define the bonds, weights, and modified durations you calculated
portfolio_data = {
    'Bond': ['Belgium', 'UK', 'Int. Paper', 'Bausch'],
    'Weight': [0.4, 0.3, 0.2, 0.1],
    'Mod_Duration': [18.6159, 4.7460, 13.8466, 1.6579] 
}
df_portfolio = pd.DataFrame(portfolio_data)

# Calculate the weighted duration
weighted_duration = (df_portfolio['Weight'] * df_portfolio['Mod_Duration']).sum()

# 2. STOCHASTIC MARKET SIMULATION
# We simulate 150 days of interest rate movements leading to the ECB 3.65% benchmark.
np.random.seed(42)
n_days = 150
# We assume a daily volatility of 0.08%, creating a realistic random walk.
daily_volatility = 0.0008 
shocks = np.random.normal(0, daily_volatility, n_days)
# Path is centred around the ECB Benchmark
market_yields = 0.0365 + np.cumsum(shocks)

# 3. STATE SPACE MODELING (Kalman Filter)
# We treat the interest rate as a 'Hidden State' obscured by market noise.
model = sm.tsa.UnobservedComponents(market_yields, level='local level')
# 'bfgs' optimization finds the most likely parameters for the trend.
res = model.fit(method='bfgs', disp=False)

# 4. PROBABILISTIC FORECASTING
# Forecase 12 steps ahad to generate a 95% C.I
forecast_res = res.get_forecast(steps=12)
mean_forecast = forecast_res.predicted_mean
conf_int = forecast_res.conf_int(alpha=0.05) 

# 5. CALCULATING STOCHASTIC RISK
# Using the 'Worst Case' (Upper Bound)
current_rate = market_yields[-1]
worst_case_rate = conf_int[-1, 1] 
delta_r = worst_case_rate - current_rate

P_total = 1000000 
# Loss calculation using your portfolio's specific weighted duration
stochastic_loss = -P_total * weighted_duration * delta_r

# OUTPUT RESULTS
print(f"Total Portfolio Weighted Modified Duration: {weighted_duration:.2f}")
print(f"Current Benchmark Yield: {current_rate:.2%}")
print(f"95% Confidence Upper Bound: {worst_case_rate:.2%}")
print(f"Predicted Portfolio Loss: €{abs(stochastic_loss):,.2f}")

# 6. VISUALIZATION
plt.figure(figsize=(10,6))
plt.plot(market_yields, label='Simulated Yield History (ECB Calibrated)', color='black')
plt.plot(np.arange(n_days, n_days+12), mean_forecast, 'r--', label='Kalman Forecast')
plt.fill_between(np.arange(n_days, n_days+12), conf_int[:, 0], conf_int[:, 1], 
                 color='red', alpha=0.15, label='95% Confidence Interval')
plt.title("State Space Forecasting: Interest Rate Risk Engine")
plt.legend()
plt.show()
