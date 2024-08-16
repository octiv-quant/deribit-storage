import datetime
import json
import os
from typing import Any, Dict, List

import orjson
import pandas as pd
import tornado.ioloop
import tornado.websocket

import messages

# Deribit WebSocket API endpoint
ws_url = "wss://www.deribit.com/ws/api/v2"
results: List[Dict[str, Any]] = []

def split_into_chunks(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

async def on_instrument_message(ws_client: tornado.websocket.WebSocketClientConnection, instruments: List[Dict[str, Any]]) -> None:
    instrument_names = [ins["instrument_name"] for ins in instruments]
    for chunk in split_into_chunks(instrument_names, 50):
        payload = orjson.dumps(messages.gen_subscribe_message(chunk)).decode()
        await ws_client.write_message(payload)

async def on_data(data: Dict[str, Any]) -> None:
    data.update(data.pop("greeks", {}))
    data.update(data.pop("stats", {}))
    results.append(data)

async def on_message(ws_client: tornado.websocket.WebSocketClientConnection, message: str) -> None:
    if message is None:
        print("Connection closed by server.")
        return
    raw_data: Dict[str, Any] = json.loads(message)
    id: int = raw_data.get("id", 0)
    params: Dict[str, Any] = raw_data.get("params", {})

    if id == 3:
        await on_instrument_message(ws_client, raw_data.get("result", []))
    elif "data" in params:
        await on_data(params["data"])

async def subscribe_option_chain() -> None:
    try:
        ws_client: tornado.websocket.WebSocketClientConnection = await tornado.websocket.websocket_connect(ws_url)
        print("WebSocket connection established.")

        await ws_client.write_message(orjson.dumps(messages.hearth_beat).decode())
        await ws_client.write_message(orjson.dumps(messages.gen_instrument_message("BTC")).decode())
        await ws_client.write_message(orjson.dumps(messages.gen_instrument_message("ETH")).decode())
        print("Subscribed to BTC and ETH options.")

        while True:
            message: str = await ws_client.read_message()
            if message is None:
                print("Connection closed by server.")
                break
            await on_message(ws_client, message)

    except Exception as e:
        print(f"Error: {e}")


def create_date_folder(base_path: str = '.') -> str:
    # Get the current date in the format "YYYY-MM-DD"
    folder_name = datetime.datetime.now().strftime('%Y-%m-%d')

    # Create the full path
    folder_path = os.path.join(base_path, folder_name)

    # Create the directory if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)

    return folder_path

def create_file_path(folder_path: str, filename: str) -> str:
    # Join the folder path with the filename
    file_path = os.path.join(folder_path, filename)
    return file_path

def export_to_csv(results: List[Dict[str, Any]], filename: str) -> None:
    folder_path = create_date_folder("data")
    file_path = create_file_path(folder_path, filename)
    df = pd.DataFrame(results)
    df["datetime"] = pd.to_datetime(df['timestamp'], unit='ms').dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    df.to_csv(file_path, compression='gzip')


if __name__ == "__main__":
    filename = "Deribit_options--{}.csv.gz".format(datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ"))
    tornado.ioloop.IOLoop.current().run_sync(subscribe_option_chain)
    export_to_csv(results, filename)
