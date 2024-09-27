import json, asyncio, socket
from websockets.asyncio.server import serve, ServerConnection
import websockets

import colors

"""
Do not touch this code unless you know what you are doing!

Refer to config.json for configuration.
"""

config = {}

conns = []

async def handler(websocket: ServerConnection):
    try:
        print(f"{colors.BRIGHT_CYAN}Connection established from {colors.BRIGHT_CYAN_BLACK_BG}{websocket.remote_address}{colors.RESET}")
        conns.append(websocket)

        await websocket.send(json.dumps({
                "type": "connection_established", 
                "online": len(conns),
                "config": config
            }))
        
        for conn in conns:
            if conn != websocket:
                await conn.send(json.dumps({"type": "user_joined",}))

        while True:
            message = await websocket.recv()
            dict = json.loads(message)

            match dict["type"]:
                case "message":
                    await handle_message(websocket, dict)

    except websockets.exceptions.ConnectionClosedError:
        await remove_conn(websocket)
    
    except websockets.exceptions.ConnectionClosedOK:
        await remove_conn(websocket)
    
    except Exception as e:
        print(f"{colors.BRIGHT_RED}An error occurred: {e}{colors.RESET}")

async def remove_conn(conn):
    conns.remove(conn)

    for conn in conns:
        if conn != conn:
            await conn.send(json.dumps({"type": "user_left",}))

    print(f"{colors.BRIGHT_CYAN}Connection closed from {colors.BRIGHT_CYAN_BLACK_BG}{conn.remote_address}{colors.RESET}")

async def main():
    global config
    with open("config.json", "r") as json_data:
        config = json.load(json_data)
        json_data.close()
    
    if not config:
        raise Exception("Config file is empty or does not exist.")
        return
    
    if config["host"] == "default":
        config["host"] = socket.gethostbyname(socket.gethostname()) # Automatically set IP
    
    if config["port"] == "default":
        config["port"] = 5520 # Default port
    
    for channel in config["channels"]:
        channels_seen = []
        if channel in channels_seen:
            raise Exception(f"Duplicate channel name: {channel}")
        channels_seen.append(channel)
    
    async with serve(handler, config["host"], config["port"]):
        print(f"{colors.BRIGHT_GREEN}Server started on {colors.BRIGHT_GREEN_BLACK_BG}ws://{config["host"]}:{config["port"]}{colors.RESET}")
        await asyncio.get_running_loop().create_future()

async def handle_message(websocket, dict):
    for conn in conns:
        await conn.send(json.dumps(dict))

if __name__ == "__main__":
    asyncio.run(main())