from fastapi import FastAPI, Request
import pika
import json
from metric_ingestion_models import IngestionResponse



app = FastAPI()
def create_event_channel():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()
    channel.exchange_declare(exchange="metrics", exchange_type="fanout")

    return connection, channel 

    
    

@app.post("/ingest/metrics", response_model=IngestionResponse)
async def ingest_data(request: Request):
    connection, channel = create_event_channel()
    counter = 0
    async for chunk in request.stream():
        channel.basic_publish(exchange='metrics', routing_key='metrics_queue', body=json.dumps(chunk))
        counter += 1 
        
    connection.close()
    return IngestionResponse(counter=counter)