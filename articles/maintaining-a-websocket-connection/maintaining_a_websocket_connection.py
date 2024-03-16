import asyncio
import logging
import json

import websockets

URL = "wss://www.deribit.com/ws/api/v2"

async def websocket_generator(retry_seconds=5):
    """Generates a new websocket connection. Retries on failure."""
    while True:
        try:
            async with websockets.connect(URL) as websocket:
                yield websocket
        except Exception as e:
            logging.error(f"Websocket connection failed: {e}")
            asyncio.sleep(retry_seconds)
            continue


async def print_btc_ticker():
    """Prints BTC ticker data from Deribit."""
    async for websocket in websocket_generator():
        try:
            # Subscribe to BTC-PERPETUAL ticker data
            msg = {
                "jsonrpc": "2.0",
                "method": "public/subscribe",
                "params": {
                    "channels": ["ticker.BTC-PERPETUAL.100ms"]
                }
            }
            await websocket.send(json.dumps(msg))
            # Continue to listen to incoming messages and print them
            while websocket.open:
                response = await websocket.recv()
                print(response)
        # if anything goes wrong, log the error and continue
        except Exception as e:
            logging.error(f"Error in print_btc_ticker: {e}")
            continue
            # no sleep required here because that's already handled by the generator

if __name__ == "__main__":

    asyncio.run(print_btc_ticker())
