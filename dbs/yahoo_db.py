import yfinance as yf

msft = yf.Ticker("MSFT")

opt = msft.option_chain(msft.options[0])