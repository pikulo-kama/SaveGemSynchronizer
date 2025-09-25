from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class EventKind:
    """
    Represents kind of subscriptable event.
    """

    """
    Error Kinds
    """
    DriveMetadataMissing = auto()
    SavesDirectoryMissing = auto()
    ErrorUploadingToDrive = auto()


class EventType(Enum):
    """
    Represents type of event.
    """

    Progress = auto()
    Error = auto()
    Done = auto()


@dataclass
class Event:
    """
    Event object.
    """

    _event_type: EventType = field(init=False)
    _event_kind: Optional[str]

    @property
    def type(self):
        """
        Type of event
        """
        return self._event_type

    @property
    def kind(self):
        """
        Kind of event.
        Something like event unique ID.
        """
        return self._event_kind


@dataclass
class ErrorEvent(Event):
    """
    Error event object
    """

    def __post_init__(self):
        self._event_type = EventType.Error


@dataclass
class ProgressEvent(Event):
    """
    Progress event object
    """

    _progress_percentage: int

    def __post_init__(self):
        self._event_type = EventType.Progress

    @property
    def progress(self):
        return self._progress_percentage


@dataclass
class DoneEvent(Event):
    """
    Event that triggers when all work has been done.
    """

    def __post_init__(self):
        self._event_type = EventType.Done


class SubscriptableService:
    """
    Represents service that sends events and allows to
    assign subscribers that would respond to them.
    """

    def __init__(self):
        self.__subscriber_list = list()

        self.__stages = 0
        self.__single_stage_percentage = 0
        self.__progress = 0

    def subscribe(self, subscriber):
        """
        Used to set callback method which would handle
        events produced by service.
        """
        self.__subscriber_list.append(subscriber)

    def _send_event(self, event: Event):
        """
        Used to send events to subscriber
        """
        for subscriber in self.__subscriber_list:
            subscriber(event)

    def _set_stages(self, stage_count: int):
        """
        Used to sent amount of stages that would
        be executed by service.

        Used for single stage percentage calculation.
        """

        self.__stages = stage_count
        self.__single_stage_percentage = 1 / stage_count

        # Reset previous progress.
        self.__progress = 0
        # Just to trigger event and let user know that work has begun.
        self._complete_stage(completion=0)

    def _complete_stage(self, completion=1):
        """
        Used to complete stage fully or partially.
        Will send progress event to subscribers.
        """

        progress = self.__progress + (completion * self.__single_stage_percentage)

        if completion == 1:
            self.__progress += self.__single_stage_percentage
            progress = self.__progress

        self._send_event(ProgressEvent(None, round(progress * 100)))
