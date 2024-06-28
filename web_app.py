import json
import logging

from fastapi import FastAPI, WebSocket
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect

import speaker_comm

speaker_settings = {'enabled': 0, 'volume': "20", 'input': 0, 'sw': 0, 'bass': 0, 'treble': 0, "balance": 0}

connections = []

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        connections.append(websocket)
        await websocket.send_json(speaker_settings, mode="text")
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
            if 'enabled' in json_body and json_body['enabled'] is not None and 0 <= json_body['enabled'] <= 1:
                enabled = json_body['enabled']
                logging.info(f"Enabled is : {enabled}")
                speaker_settings['enabled'] = enabled
                if enabled == 1:
                    speaker_comm.enable()
                if enabled == 0:
                    speaker_comm.disable()
            if 'volume' in json_body and json_body['volume'] is not None and 0 <= json_body['volume'] <= 57:
                volume = json_body['volume']
                logging.info(f"Volume is : {volume}")
                speaker_settings['volume'] = volume
                speaker_comm.set_volume(volume)
            if 'input' in json_body and json_body['input'] is not None and 0 <= json_body['input'] <= 2:
                audio_input = json_body['input']
                logging.info(f"Input is : {audio_input}")
                speaker_settings['input'] = audio_input
                speaker_comm.set_input(audio_input)
            if 'sw' in json_body and json_body['sw'] is not None and -10 <= json_body['sw'] <= 10:
                sw = json_body['sw']
                logging.info(f"sw is : {sw}")
                speaker_settings['sw'] = sw
                speaker_comm.set_sw(sw)
            if 'bass' in json_body and json_body['bass'] is not None and -10 <= json_body['bass'] <= 10:
                bass = json_body['bass']
                logging.info(f"Bass is : {bass}")
                speaker_settings['bass'] = bass
                speaker_comm.set_bass(bass)
            if 'treble' in json_body and json_body['treble'] is not None and -10 <= json_body['treble'] <= 10:
                treble = json_body['treble']
                logging.info(f"Treble is : {treble}")
                speaker_settings['treble'] = treble
                speaker_comm.set_treble(treble)
            if 'balance' in json_body and json_body['balance'] is not None and -10 <= json_body['balance'] <= 10:
                balance = json_body['balance']
                logging.info(f"Balance is : {json_body['balance']}")
                speaker_settings['balance'] = json_body['balance']
                speaker_comm.set_balance(balance)

            logging.info(f"Settings was updated : {speaker_settings}")
            logging.info(f"Json is : {json.dumps(speaker_settings)}")
            for client in connections:
                await client.send_text(json.dumps(speaker_settings))
    except WebSocketDisconnect:
        connections.remove(websocket)


app.mount("/", StaticFiles(directory="static", html=True), name="static")


def get_web_app():
    return app
