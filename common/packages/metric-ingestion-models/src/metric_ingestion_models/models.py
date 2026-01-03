from pydantic import BaseModel, Field 
from typing import Optional, List, TypeVar, Literal, Union, Self
import json

class DeviceInformation:
    os: Literal["linux", "macOS", "window", "other"] = Field(default="linux")
    cpu_count: int = Field(default=1)
    ram: float = Field(default=128)
    

class DeviceMetric(BaseModel):
    name: str = Field(default="cpu_usage")
    timestamp: Optional[float] = Field(default=0.0)
    value: Union[float, int] = Field()

    def from_json(cls, json_value: str) -> Self:
        return cls.__init__(**json.loads(json_value))

TMetric = TypeVar("TMetric", bound=DeviceMetric)

class DeviceMetricGroup(BaseModel):
    metrics: List[TMetric] = Field(default_factory=list)
    device_id: str = Field(default="000-010-0001")

    @classmethod
    def from_json(cls, json_value: str):
        json_object = json.loads(json_value)

        return cls.__init__(device_id=json_object["device_id"],\
                             metrics = [DeviceMetric.from_json(metric_raw) for metric_raw in json_object.get("metrics", [])])

    # TODO: write field validation using pydantic

class IngestionResponse(BaseModel):
    counter: int = Field(default=0, gt=-1)
    status: Literal["success", "error"] = Field(default="success")
    msg: str = Field(default ="No msg")

    