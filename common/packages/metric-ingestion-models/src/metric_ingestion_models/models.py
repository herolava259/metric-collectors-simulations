from pydantic import BaseModel, Field 
from typing import Optional, List, TypeVar, Literal, Union


class DeviceInformation:
    os: Literal["linux", "macOS", "window", "other"] = Field(default="linux")
    cpu_count: int = Field(default=1)
    

class DeviceMetric(BaseModel):
    name: str = Field(default="cpu_usage")
    timestamp: Optional[float] = Field(default=0.0)
    value: Union[float, int] = Field()

TMetric = TypeVar("TMetric", bound=DeviceMetric)

class DeviceMetricGroup(BaseModel):
    metrics: List[TMetric] = Field(default_factory=list)
    device_id: str = Field(default="000-010-0001")

class IngestionResponse(BaseModel):
    counter: int = Field(default=0, gt=-1)
    status: Literal["success", "error"] = Field(default="success")
    msg: str = Field(default ="No msg")

    