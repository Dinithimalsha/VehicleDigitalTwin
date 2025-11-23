import asyncio
import websockets
import json
import logging
import sys
from telemetry_generator import TelemetryGenerator
from telemetry_logger import TelemetryLogger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TelemetryServer")

# Global state
CURRENT_MODE = "live"
CONNECTED_CLIENTS = set()

async def handler(websocket, generator):
    """Handles new WebSocket connections."""
    global CURRENT_MODE
    logger.info(f"Client connected: {websocket.remote_address}")
    
    # RESET SIMULATION ON CONNECT (User Feedback: "Start from 0")
    generator.reset()
    logger.info("Simulation RESET for new client.")
    
    CONNECTED_CLIENTS.add(websocket)
    try:
        async for message in websocket:
            logger.info(f"Received: {message}")
            try:
                data = json.loads(message)
                if "command" in data:
                    if data["command"] == "start_playback":
                        CURRENT_MODE = "playback"
                        logger.info("Switched to PLAYBACK mode")
                    elif data["command"] == "start_live":
                        CURRENT_MODE = "live"
                        logger.info("Switched to LIVE mode")
            except json.JSONDecodeError:
                pass
    except websockets.exceptions.ConnectionClosed:
        logger.info("Client disconnected")
    finally:
        CONNECTED_CLIENTS.discard(websocket)

async def broadcast_telemetry():
    """Generates and broadcasts telemetry data to all connected clients."""
    logger.info("Starting telemetry broadcast loop...")
    
    generator = TelemetryGenerator()
    db_logger = TelemetryLogger()
    
    # Start the WebSocket server with access to the generator
    # We use a lambda or partial to pass the generator instance to the handler
    import functools
    bound_handler = functools.partial(handler, generator=generator)
    
    async with websockets.serve(bound_handler, "localhost", 8765):
        logger.info("WebSocket server started on ws://localhost:8765")
        
        # Pre-load playback data for simplicity (or load on demand)
        playback_data = []
        playback_index = 0

        while True:
            # Reload playback data if we just switched to it
            if CURRENT_MODE == "playback" and not playback_data:
                 playback_data = db_logger.get_playback_data()
                 if not playback_data:
                     logger.warning("No playback data found, reverting to live")
                     # CURRENT_MODE = "live" # Optional: force back to live

            if CURRENT_MODE == "live":
                data = generator.get_next_frame()
                db_logger.log(data)
            else:
                if playback_data:
                    if playback_index < len(playback_data):
                        data = playback_data[playback_index]
                        playback_index += 1
                    else:
                        playback_index = 0
                        data = playback_data[playback_index]
                else:
                    # Fallback if no data
                    data = generator.get_next_frame()

            message = json.dumps(data)
            
            if CONNECTED_CLIENTS:
                websockets_to_remove = set()
                # Iterate over a copy of the set to avoid "Set changed size during iteration" error
                for ws in list(CONNECTED_CLIENTS):
                    try:
                        await ws.send(message)
                    except websockets.exceptions.ConnectionClosed:
                        websockets_to_remove.add(ws)
                
                for ws in websockets_to_remove:
                    CONNECTED_CLIENTS.discard(ws)
            
            await asyncio.sleep(1/60)



async def main():
    # Start the telemetry loop (which now owns the server)
    await broadcast_telemetry()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")

