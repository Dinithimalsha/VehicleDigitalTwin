import asyncio
import websockets
import json

async def test_switching():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        print(f"Connected to {uri}")
        
        # Listen for a few live messages
        for _ in range(3):
            msg = await websocket.recv()
            print(f"Live: {msg}")

        # Switch to playback
        print("Sending switch to playback command...")
        await websocket.send(json.dumps({"command": "start_playback"}))

        # Listen for playback messages (might be empty if no logs yet, but server shouldn't crash)
        for _ in range(3):
            msg = await websocket.recv()
            print(f"Playback: {msg}")

        # Switch back to live
        print("Sending switch to live command...")
        await websocket.send(json.dumps({"command": "start_live"}))

        # Listen for live messages
        for _ in range(3):
            msg = await websocket.recv()
            print(f"Live again: {msg}")

if __name__ == "__main__":
    try:
        asyncio.run(asyncio.wait_for(test_switching(), timeout=10))
    except Exception as e:
        print(f"Test finished: {e}")
