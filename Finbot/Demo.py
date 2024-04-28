from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask, render_template, request, jsonify
import sys
import json
import datetime as dt
import pandas as pd
import yfinance as yf
import os
from werkzeug.utils import secure_filename
import plotly.graph_objects as go

app = Flask(__name__, static_url_path='/static')

portfolio: dict = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save_portfolio', methods=['POST'])
def save_portfolio():
    try:
        data = request.json
        filename = data.get('filename', 'portfolio.json')  # Get filename or use default
        with open(filename, 'w') as file:
            json.dump(portfolio, file)
        return 'Portfolio saved successfully!', 200
    except Exception as e:
        print(f"Error saving portfolio: {e}")
        return 'Error saving portfolio.', 500

def add_stock(ticker, amount):
    try:
        if ticker in portfolio:
            portfolio[ticker] += amount
        else:
            portfolio[ticker] = amount
    except Exception as e:
        print(f"Error adding stock: {e}")
        raise e

@app.route('/remove_stock', methods=['POST'])
def remove_stock(ticker=None, amount=None):  # Add default values for parameters
    global portfolio  # Make portfolio variable global within the function
    try:
        if ticker is None or amount is None:  # Check if called internally or via HTTP request
            with open('portfolio.json', 'r') as file:
                portfolio = json.load(file)

            data = request.json
            print("Received data:", data)

            ticker = data['ticker']
            amount = int(data['amount'])
            print("Ticker:", ticker)
            print("Amount:", amount)

            if ticker in portfolio:
                if amount <= portfolio[ticker]:
                    portfolio[ticker] -= amount
                    print("Updated portfolio:", portfolio)
                else:
                    return "You don't have enough shares!", 400
            else:
                return f"You don't own any shares of {ticker}", 400

            with open('portfolio.json', 'w') as file:
                json.dump(portfolio, file)

            return 'Stock removed successfully!', 200
        else:  # If called internally, just process the parameters
            if ticker in portfolio:
                if amount <= portfolio[ticker]:
                    portfolio[ticker] -= amount
                else:
                    raise ValueError("Not enough shares to remove.")
            else:
                raise ValueError("Ticker not found in portfolio.")
    except Exception as e:
        print(f"Error removing stock: {e}")
        return 'Error removing stock.', 500




@app.route('/show_portfolio', methods=['GET'])
def show_portfolio():
    print("Your portfolio (before retrieval):", portfolio)
    if not portfolio:
        return 'Your portfolio is empty.', 204  # No content
    for ticker, shares in portfolio.items():
        print(f"You own {shares} shares of {ticker}")
    print("Your portfolio (after retrieval):", portfolio)
    return jsonify(portfolio), 200

MAX_RETRIES = 3

def fetch_data(ticker):
    for _ in range(MAX_RETRIES):
        try:
            data = yf.download(ticker)
            return data
        except Exception as e:
            print(f"Error fetching data for {ticker} from Yahoo Finance: {e}")

    return None

@app.route('/portfolio_worth', methods=['GET'])
def portfolio_worth():
    try:
        total_worth = 0
        for ticker, shares in portfolio.items():
            data = fetch_data(ticker)
            if data is not None:
                price = data['Close'].iloc[-1]
                total_worth += price * shares
            else:
                print(f"Data retrieval failed for {ticker}. Using fallback data.")

        if not isinstance(total_worth, (int, float)):
            print("Total worth is not a valid numeric value.")
            return 'Error calculating portfolio worth.', 500

        formatted_worth = f'${total_worth:.2f}'
        print(f"Your portfolio is worth {formatted_worth }")
        return f'Your portfolio is worth {formatted_worth}', 200
    except Exception as e:
        print(f"Error calculating portfolio worth: {e}")
        return 'Error calculating portfolio worth.', 500


def portfolio_gains(starting_date):
    if not starting_date:
        return 'Missing starting date parameter.', 400

    try:
        starting_date = dt.datetime.strptime(starting_date, "%Y-%m-%d")
    except ValueError:
        return 'Invalid starting date format. Use YYYY-MM-DD.', 400

    total_investment = 0
    total_value_now = 0

    try:
        for ticker, shares in portfolio.items():
            try:
                data = fetch_data(ticker)
                if data is not None:
                    price_now = data['Close'].iloc[-1]
                    price_then = data.loc[data.index == starting_date]['Close'].values[0]
                    total_investment += price_then * shares
                    total_value_now += price_now * shares
            except Exception as e:
                print(f"Error fetching data for {ticker} while calculating portfolio worth: {e}")

        relative_gains = ((total_value_now - total_investment) / total_investment) * 100
        absolute_gains = total_value_now - total_investment

        # Format gains as a string
        gains_string = f'Relative gains: {relative_gains:.2f}%, Absolute gains: ${absolute_gains:.2f}'
        correct_list = [gains_string, 200]  # This is a list
        return correct_list
    except Exception as e:
        print(f"Error calculating gains: {e}")
        return 'Error calculating gains.', 500

def plot_chart(ticker, starting_date):
    if not starting_date:
        return 'Missing starting date parameter.', 400

    try:
        starting_date = dt.datetime.strptime(starting_date, "%Y-%m-%d")
    except ValueError:
        return 'Invalid starting date format. Use YYYY-MM-DD.', 400

    data = fetch_data(ticker)
    if data is None:
        print(f"Data retrieval failed for {ticker}. Unable to plot chart.")
        return 'Error fetching data for chart. Please try again.', 500

    try:
        chart_filename = f"{ticker}_chart.png"

        # Plotly code for generating the chart
        fig = go.Figure(data=[go.Scatter(x=data.index, y=data['Close'])])
        fig.update_layout(title=f"{ticker} Stock Price Chart", xaxis_title="Date", yaxis_title="Price")
        fig.write_html(chart_filename)  # Save as HTML for headless browser

        # Use Selenium to open the chart and capture screenshot
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run Chrome in headless mode

        # Fix for recent Selenium changes
        driver = webdriver.Chrome(ChromeDriverManager().install(), options)

        driver.get(f"file://{os.path.abspath(chart_filename)}")  # Open HTML file in browser

        # Adjust these values based on your chart and desired image size
        width = 800
        height = 600
        driver.set_window_size(width, height)

        screenshot = driver.get_screenshot_as_png()
        with open(chart_filename, 'wb') as file:
            file.write(screenshot)

        driver.quit()

        # Construct full path to the image for static file serving
        chart_filename = os.path.join(app.static_folder, chart_filename)

        return {'chart_filename': chart_filename}, 200
    except Exception as e:
        print(f"Error plotting chart: {e}")
        return 'Error generating chart. Please try again.', 500




@app.route('/execute_command', methods=['POST'])
def execute_command():
    try:
        data = request.json

        # Validate required fields for some commands
        if 'command' not in data:
            return 'Missing command parameter.', 400
        command = data['command']

        # Ensure both ticker and amount are provided for add/remove portfolio
        if command in ('add_portfolio', 'remove_portfolio'):
            if 'ticker' not in data or 'amount' not in data:
                return 'Missing required data (ticker and amount) for the command.', 400
            ticker = data['ticker']
            amount = int(data['amount'])

            # Validate amount (must be positive for add, non-negative for remove)
            if amount < 0:
                return 'Invalid amount. Amount cannot be negative for removing stocks.', 400

        if command == 'add_portfolio':
            add_stock(ticker, amount)
            save_portfolio()
            return ' Stock added successfully! ', 200
        elif command == 'remove_portfolio':
            remove_stock(ticker, amount)  # Pass ticker and amount as arguments
            save_portfolio()
            return ' Stock removed successfully! ', 200
        elif command == 'show_portfolio':
            return show_portfolio()
        elif command == 'portfolio_worth':
            worth = portfolio_worth()
            return f'Your portfolio is worth ${worth:.2f}', 200
        elif command == 'plot_chart':
            chart_data = plot_chart(data.get('ticker'), data.get('starting_date'))  # Use .get() for optional parameters
            return chart_data
        elif command == 'portfolio_gains':
            starting_date = data.get('starting_date')
            gains_string = portfolio_gains(starting_date)  # Pass starting_date as an argument
            return gains_string, 200
        elif command == 'bye':
            return 'Session ended. Goodbye!', 200
        else:
            return 'Invalid command.', 400
    except Exception as e:
        print(f"Error executing command: {e}")
        return 'Error executing command', 500



@app.route('/bye', methods=['GET'])
def bye():
    return 'Session ended. Goodbye!', 200

 
if __name__ == '__main__':
   app.run(debug=True)
