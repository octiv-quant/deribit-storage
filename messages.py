from typing import List


hearth_beat = {
    "id": 2,
    "jsonrpc": "2.0",
    "method": "public/set_heartbeat",
    "params": {"interval": 10}
}
def gen_instrument_message(symbol):
    instrument_message = {
        "id": 3,
        "jsonrpc": "2.0",
        "method": "public/get_instruments",
        "params": {"currency": symbol, "kind": "option", "include_spots": False}
    }
    return instrument_message

def gen_subscribe_message(tickers: List[str]):
    payload = [f"incremental_ticker.{ticker}" for ticker in tickers]
    subscribe_message = {
        "jsonrpc": "2.0",
        "method": "public/subscribe",
        "params": {
            "channels": payload
        }
    }
    return subscribe_message
