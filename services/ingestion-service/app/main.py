from fastapi import FastAPI
import pika
import json

app = FastAPI()

def send_to_queue(data):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()
    channel.exchange_declare(exchange="metrics", exchange_type="fanout")
    channel.basic_publish(exchange='metrics', routing_key='metrics_queue', body=json.dumps(data))
    connection.close()

@app.post("/ingest")
async def ingest_data(payload: dict):
    # payload: {device_id, metric, value, timestamp}
    send_to_queue(payload)
    return {"status": "sent to queue"}