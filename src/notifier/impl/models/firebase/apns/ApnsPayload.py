from typing import Optional, Union, List

from pydantic import BaseModel, Field


class Alert(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    body: Optional[str] = None
    launch_image: Optional[str] = Field(None, alias='launch-image')
    title_loc_key: Optional[str] = Field(None, alias='title-loc-key')
    title_loc_args: Optional[List[str]] = Field(None, alias='title-loc-args')
    subtitle_loc_key: Optional[str] = Field(None, alias='subtitle-loc-key')
    subtitle_loc_args: Optional[List[str]] = Field(None, alias='subtitle-loc-args')
    loc_key: Optional[str] = Field(None, alias='loc-key')
    loc_args: Optional[List[str]] = Field(None, alias='loc-args')


class Sound(BaseModel):
    critical: Optional[int] = None
    name: Optional[str] = None
    volume: Optional[float] = None


class Aps(BaseModel):
    alert: Optional[Union[Alert, str]] = None
    badge: Optional[int] = None
    sound: Optional[Union[Sound, str]] = None
    thread_id: Optional[int] = Field(None, alias='thread-id')
    category: Optional[str] = None
    content_available: Optional[int] = Field(None, alias='content-available')
    mutable_content: Optional[int] = Field(None, alias='mutable-content')
    target_content_id: Optional[str] = Field(None, alias='target-content-id')
    interruption_level: Optional[str] = Field(None, alias='interruption-level')
    relevance_score: Optional[float] = Field(None, alias='relevance-score')
    filter_criteria: Optional[str] = Field(None, alias='filter-criteria')


class ApnsPayload(BaseModel):
    aps: Optional[Aps] = None
