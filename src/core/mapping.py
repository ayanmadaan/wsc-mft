import json

def instrumentToken(trading_symbol):
    # Load the JSON file
    with open('instruments.json', 'r') as file:
        data = json.load(file)
    
    # Fetch the instrument token using the trading symbol
    instrument_token = data.get(trading_symbol, None)
    
    if instrument_token:
        return instrument_token
    else:
        print(f"No instrument token found for trading symbol: {trading_symbol}")
        return None

# Example usage:
# trading_symbol = 'EURINR23AUG84.5CE'
# token = get_instrument_token(trading_symbol)
# print(f"Instrument token for {trading_symbol}: {token}")
