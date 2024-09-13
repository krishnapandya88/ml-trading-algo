# -*- coding: utf-8 -*-
"""Untitled3.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/15TJbzCrsLXI0yLDF-Rgjy8h37A6z8iwX
"""



!pip install yfinance pandas numpy matplotlib scipy statsmodels scikit-learn ipywidgets

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.tsa.arima.model import ARIMA
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import ipywidgets as widgets
from IPython.display import display

# Extended list of Indian stocks
stock_symbols = [
    ('Reliance Industries', 'RELIANCE.NS'),
    ('Tata Consultancy Services', 'TCS.NS'),
    ('HDFC Bank', 'HDFCBANK.NS'),
    ('Infosys', 'INFY.NS'),
    ('ICICI Bank', 'ICICIBANK.NS'),
    ('Hindustan Unilever', 'HINDUNILVR.NS'),
    ('State Bank of India', 'SBIN.NS'),
    ('Bharti Airtel', 'BHARTIARTL.NS'),
    ('ITC', 'ITC.NS'),
    ('Kotak Mahindra Bank', 'KOTAKBANK.NS'),
    ('Larsen & Toubro', 'LT.NS'),
    ('Axis Bank', 'AXISBANK.NS'),
    ('Asian Paints', 'ASIANPAINT.NS'),
    ('HCL Technologies', 'HCLTECH.NS'),
    ('Maruti Suzuki India', 'MARUTI.NS'),
    ('Adani Enterprises', 'ADANIENT.NS'),
    ('Adani Ports', 'ADANIPORTS.NS'),
    ('Wipro', 'WIPRO.NS'),
    ('UltraTech Cement', 'ULTRACEMCO.NS'),
    ('Bajaj Finance', 'BAJFINANCE.NS')
]

def get_stock_data(stock_symbol, period='1y'):
    stock = yf.Ticker(stock_symbol)
    data = stock.history(period=period)
    if data.empty:
        print(f"Couldn't retrieve data for {stock_symbol}. Please check the symbol or period.")
        return None
    return data

def calculate_returns(data):
    data['Daily_Return'] = data['Close'].pct_change()
    data['Cumulative_Return'] = (1 + data['Daily_Return']).cumprod() - 1
    return data

def calculate_volatility(data, window=21):
    data['Volatility'] = data['Daily_Return'].rolling(window=window).std() * np.sqrt(252)
    return data

def calculate_sharpe_ratio(data, risk_free_rate=0.05):
    sharpe_ratio = (data['Daily_Return'].mean() * 252 - risk_free_rate) / (data['Daily_Return'].std() * np.sqrt(252))
    return sharpe_ratio

def perform_monte_carlo_simulation(data, num_simulations=1000, time_horizon=252):
    last_price = data['Close'].iloc[-1]
    returns = data['Daily_Return'].dropna()

    simulation_df = pd.DataFrame()

    for i in range(num_simulations):
        prices = [last_price]
        for _ in range(time_horizon):
            price = prices[-1] * (1 + np.random.choice(returns))
            prices.append(price)
        simulation_df[i] = prices

    return simulation_df

def forecast_arima(data, order=(1,1,1)):
    model = ARIMA(data['Close'], order=order)
    results = model.fit()
    forecast = results.forecast(steps=30)
    return forecast

def train_random_forest(data):
    data['Target'] = data['Close'].shift(-1)
    data = data.dropna()

    features = ['Open', 'High', 'Low', 'Close', 'Volume']
    X = data[features]
    y = data['Target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    rmse = np.sqrt(mse)

    return model, rmse

def analyze_stock(stock_symbol, period='1y'):
    data = get_stock_data(stock_symbol, period)
    if data is None:
        return None

    data = calculate_returns(data)
    data = calculate_volatility(data)
    sharpe_ratio = calculate_sharpe_ratio(data)

    monte_carlo_sim = perform_monte_carlo_simulation(data)
    arima_forecast = forecast_arima(data)
    rf_model, rf_rmse = train_random_forest(data)

    return {
        'data': data,
        'sharpe_ratio': sharpe_ratio,
        'monte_carlo_sim': monte_carlo_sim,
        'arima_forecast': arima_forecast,
        'rf_model': rf_model,
        'rf_rmse': rf_rmse
    }

def plot_results(analysis_results):
    data = analysis_results['data']
    monte_carlo_sim = analysis_results['monte_carlo_sim']
    arima_forecast = analysis_results['arima_forecast']

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 18))

    # Plot historical prices and returns
    ax1.plot(data.index, data['Close'], label='Close Price')
    ax1.set_title('Historical Stock Price')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price')
    ax1.legend()

    ax1_twin = ax1.twinx()
    ax1_twin.plot(data.index, data['Cumulative_Return'], color='red', label='Cumulative Return')
    ax1_twin.set_ylabel('Cumulative Return')
    ax1_twin.legend(loc='lower right')

    # Plot Monte Carlo simulation
    ax2.plot(monte_carlo_sim)
    ax2.set_title('Monte Carlo Simulation')
    ax2.set_xlabel('Days')
    ax2.set_ylabel('Simulated Price')

    # Plot ARIMA forecast
    ax3.plot(data.index[-100:], data['Close'].tail(100), label='Historical')
    ax3.plot(pd.date_range(start=data.index[-1], periods=31)[1:], arima_forecast, label='ARIMA Forecast')
    ax3.set_title('ARIMA Forecast')
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Price')
    ax3.legend()

    plt.tight_layout()
    plt.show()

def calculate_potential_profit_loss(initial_price, final_price, quantity):
    total_investment = initial_price * quantity
    final_value = final_price * quantity
    profit_loss = final_value - total_investment
    percentage = (profit_loss / total_investment) * 100
    return profit_loss, percentage

def on_analyze_button_clicked(b):
    with output:
        output.clear_output()
        stock_symbol = dropdown.value
        period = period_dropdown.value
        quantity = quantity_input.value

        print(f"Analyzing {stock_symbol} for period: {period}")
        results = analyze_stock(stock_symbol, period)

        if results:
            data = results['data']
            initial_price = data['Close'].iloc[0]
            final_price = data['Close'].iloc[-1]
            profit_loss, percentage = calculate_potential_profit_loss(initial_price, final_price, quantity)

            print(f"Initial price: ₹{initial_price:.2f}")
            print(f"Latest price: ₹{final_price:.2f}")
            print(f"Volatility: {data['Volatility'].iloc[-1]:.2%}")
            print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
            print(f"Random Forest RMSE: {results['rf_rmse']:.2f}")
            print(f"\nFor {quantity} shares:")
            print(f"Potential {'Profit' if profit_loss >= 0 else 'Loss'}: ₹{abs(profit_loss):.2f} ({percentage:.2f}%)")

            plot_results(results)
        else:
            print("Analysis failed. Please check your inputs and try again.")

# UI setup
dropdown = widgets.Dropdown(
    options=stock_symbols,
    description='Select Stock:',
)

period_dropdown = widgets.Dropdown(
    options=[('1 Month', '1mo'), ('3 Months', '3mo'), ('6 Months', '6mo'), ('1 Year', '1y'), ('2 Years', '2y'), ('5 Years', '5y')],
    description='Period:',
    value='1y'
)

quantity_input = widgets.IntText(
    value=100,
    description='Quantity:',
    min=1
)

analyze_button = widgets.Button(description="Analyze Stock")
output = widgets.Output()

analyze_button.on_click(on_analyze_button_clicked)
display(dropdown, period_dropdown, quantity_input, analyze_button, output)