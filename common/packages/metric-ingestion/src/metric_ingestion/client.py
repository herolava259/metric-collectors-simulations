import httpx 
from pydantic import BaseModel, Field
from datetime import timedelta, datetime, timezone
import psutil
from typing import Set, Optional
from metric_ingestion_models import DeviceMetricGroup, DeviceMetric
import asyncio 

import logging

METRICS: Set[str] = {"cpu_times", "cpu_percent", "cpu_time_percent"}


class IngestionSettings(BaseModel):
    interval_time: timedelta = Field(default_factory=lambda: timedelta(seconds=30))
    ingestion_endpoint: str = Field(default="http://localhost:8001/ingest/metrics")
    exporting_metrics: Optional[Set[str]] = Field(default=None)
    device_id: str = Field(...)
    sending_limit: Optional[int] = Field(default=None)

class MetricIngestionClient(object):
    def __init__(self, setting: IngestionSettings):
        self.setting: IngestionSettings = setting
        self.stop_event = asyncio.Event()

    def _retrieve_metric(self) -> DeviceMetricGroup:
        cpu_usage = psutil.cpu_percent(interval=1)
        ram_usage = psutil.virtual_memory().percent
        ts = datetime.now(timezone.utc).timestamp()
        return DeviceMetricGroup(metrics = [DeviceMetric(name="cpu_usage", timestamp=ts, value = cpu_usage), \
                                            DeviceMetric(name="ram_usage", timestamp=ts, value=ram_usage)], \
                                 device_id=self.setting.device_id)
    
    
    async def metric_streaming(self):

        counter = 0
        def conditional_loop():
            nonlocal counter
            continued = True
            counter += 1 
            if not self.setting.sending_limit :
                continued = counter <= self.setting.sending_limit
            return continued and not self.stop_event.is_set()
        
        while conditional_loop():
            yield self._retrieve_metric()
            #await asyncio.sleep()
            await asyncio.wait_for(self.stop_event.wait(), timeout=float(self.setting.interval_time.microseconds))


    def export_device_information():
        pass

    
    async def start_expose(self):
        logger = logging.getLogger(__name__)

        async with httpx.AsyncClient() as client:
            response = await client.post(self.setting.ingestion_endpoint, content=self.metric_streaming())
            logger.log(response.json())
    
    async def stop_expose(self, ):
        self.stop_event.set()

                

                




        
