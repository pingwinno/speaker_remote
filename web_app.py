import asyncio
import json
import logging

from fastapi import FastAPI, WebSocket
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect

import speaker_comm
from speaker_comm import settings

connections = []

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        connections.append(websocket)

        await websocket.send_text(settings.to_json())
        while True:
            data = await websocket.receive_text()
            json_body = {}
            try:
                json_body = json.loads(data)
            except ValueError:
                logging.error(f"Cannot handle a message: {data}")
                await websocket.send_text("Unsupported message type")

            logging.info(f"Message text was: {data}")
            logging.info(f"Message json was: {json_body}")
            if 'enabled' in json_body and json_body['enabled'] is not None:
                enabled = json_body['enabled']
                logging.info(f"Enabled is : {enabled}")
                if enabled == 1:
                    while speaker_comm.enable() != 1:
                        await asyncio.sleep(1)
                if enabled == 0:
                    await speaker_comm.disable()
                    await asyncio.sleep(2)
            if 'volume' in json_body and json_body['volume'] is not None:
                volume = json_body['volume']
                logging.info(f"Volume is : {volume}")
                speaker_comm.set_volume(volume)
            if 'input' in json_body and json_body['input'] is not None:
                audio_input = json_body['input']
                logging.info(f"Input is : {audio_input}")
                speaker_comm.set_input(audio_input)
            if 'sw' in json_body and json_body['sw'] is not None:
                sw = json_body['sw']
                logging.info(f"sw is : {sw}")
                speaker_comm.set_sw(sw)
            if 'bass' in json_body and json_body['bass'] is not None:
                bass = json_body['bass']
                logging.info(f"Bass is : {bass}")
                speaker_comm.set_bass(bass)
            if 'treble' in json_body and json_body['treble'] is not None:
                treble = json_body['treble']
                logging.info(f"Treble is : {treble}")
                speaker_comm.set_treble(treble)
            if 'balance' in json_body and json_body['balance'] is not None:
                balance = json_body['balance']
                logging.info(f"Balance is : {json_body['balance']}")
                speaker_comm.set_balance(balance)

            logging.info(f"Settings was updated : {settings.to_json()}")
            logging.info(f"Json is : {settings.to_json()}")
            for client in connections:
                await (client.send_bytes(settings.to_json()))
    except WebSocketDisconnect:
        connections.remove(websocket)


app.mount("/", StaticFiles(directory="static", html=True), name="static")


def get_web_app():
    return app
