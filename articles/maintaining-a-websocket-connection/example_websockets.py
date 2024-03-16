import asyncio
import websockets
import json

URL = "wss://www.deribit.com/ws/api/v2"

async def print_btc_ticker():
    async with websockets.connect(URL) as websocket:
        msg = {
            "jsonrpc": "2.0",
            "method": "public/ticker",
            "params": {
                "instrument_name": "BTC-PERPETUAL"
            }
        }
        await websocket.send(json.dumps(msg))
        response = await websocket.recv()
        print(response)

if __name__ == "__main__":
    
    asyncio.run(print_btc_ticker())
