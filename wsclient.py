import asyncio
import websockets
import json
from pythonosc import osc_message_builder

project = "a56bd00e-d71b-11ee-b5f5-408d5c84af19"
project_load = {"action":"project_ready","value":project}

message = json.dumps(project_load)
ok_response = {"type": "project_ready", "value": project}





go_msg = osc_message_builder.OscMessageBuilder(address="/engine/command/go")
go_msg.add_arg(1)
build_go_msg = go_msg.build()

ok_go_msg = ""

async def load_and_go():
    uri_ws = "ws://master.local/ws"
    async with websockets.connect(uri_ws) as websocket:
        await websocket.send(message)
        response = json.loads( await websocket.recv() )
        print(response)
        while response != ok_response:
            response = json.loads( await websocket.recv() )
            print(response)
            await asyncio.sleep(5)

        print("response was ok, continue")

    uri_realtime = "ws://master.local/realtime"
    async with websockets.connect(uri_realtime) as websocket:
        print(type(go_msg))
        print(go_msg)
        await websocket.send(build_go_msg.dgram)
        response = await websocket.recv()
        print(response)
        while response != ok_response:
            response = json.loads( await websocket.recv() )
            print(response)
            await asyncio.sleep(5)

        print("response was ok, continue")
            


asyncio.get_event_loop().run_until_complete(load_and_go())