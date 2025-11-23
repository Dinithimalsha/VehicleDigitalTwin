import asyncio
import websockets
import json

async def test_client():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        print(f"Connected to {uri}")
        try:
            async for message in websocket:
                data = json.loads(message)
                print(f"Received: Speed={data.get('speed_kmh')} km/h, RPM={data.get('rpm')}")
                # Just receive 5 messages then exit
                if data.get('rpm') > 0: # Just a dummy check
                    break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Run for a short time
    try:
        asyncio.run(asyncio.wait_for(test_client(), timeout=5))
    except asyncio.TimeoutError:
        print("Test finished (timeout)")
