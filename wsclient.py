import asyncio
import websockets
import json
from pythonosc import osc_message_builder, osc_message
import argparse

project_id_file = '/etc/cuems/project_id'

default_project = "a56bd00e-d71b-11ee-b5f5-408d5c84af19"



try:
    with open(project_id_file, "r") as my_file:
        project = my_file.read()
        
except FileNotFoundError as e:
    print(f'can not open project_if file {e}')

    project = default_project




parser = argparse.ArgumentParser(description='Load project and send GO.')

parser.add_argument('project_id', nargs='?', type=str, help='project uuid', default=None)
args = parser.parse_args()
if args.project_id != None:
    project = args.project_id


project_load = {"action":"project_ready","value":project}

message = json.dumps(project_load)
ok_response = {"type": "project_ready", "value": project}





go_msg = osc_message_builder.OscMessageBuilder(address="/engine/command/go")
go_msg.add_arg(1)
build_go_msg = go_msg.build()

go_ok_msg = "/engine/command/go"

stop_msg = osc_message_builder.OscMessageBuilder(address="/engine/command/stop")
stop_msg.add_arg(1)
build_stop_msg = stop_msg.build()


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

        print("----------response was ok, continue----------")

    uri_realtime = "ws://master.local/realtime"
    async with websockets.connect(uri_realtime) as websocket:
  
        await websocket.send(build_go_msg.dgram)
        
        response = osc_message.OscMessage(await websocket.recv())
        print(response.address, end =" ")
        print(response.params)
        while response.address != go_ok_msg:
            response = osc_message.OscMessage(await websocket.recv())

            print(response.address, end =" ")
            print(response.params)

        print("----------Engine is running, exit----------")
            


asyncio.get_event_loop().run_until_complete(load_and_go())