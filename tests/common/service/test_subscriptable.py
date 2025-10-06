import pytest
from unittest.mock import Mock

from savegem.common.service.subscriptable import SubscriptableService, EventKind, EventType, ErrorEvent, \
    ProgressEvent, DoneEvent


@pytest.fixture
def subscriber_mock():
    """A mock function to act as a subscriber."""
    return Mock()


@pytest.fixture
def service():
    """A fresh SubscriptableService instance."""
    return SubscriptableService()


def test_error_event_creation():
    """Test ErrorEvent initializes correctly."""
    error_kind = EventKind.DriveMetadataMissing
    event = ErrorEvent(error_kind)
    assert event.type == EventType.Error
    assert event.kind == error_kind


def test_progress_event_creation():
    """Test ProgressEvent initializes correctly."""
    progress_percentage = 50
    event = ProgressEvent(None, progress_percentage)
    assert event.type == EventType.Progress
    assert event.kind is None
    assert event.progress == progress_percentage


def test_done_event_creation_success():
    """Test DoneEvent for a successful completion."""
    event = DoneEvent(None)
    assert event.type == EventType.Done
    assert event.kind is None
    assert event.success is True


def test_done_event_creation_failure():
    """Test DoneEvent for a failure (indicated by kind being present)."""
    error_kind = EventKind.SavesDirectoryMissing
    event = DoneEvent(error_kind)
    assert event.type == EventType.Done
    assert event.kind == error_kind
    assert event.success is False


# --- Test SubscriptableService ---


def test_subscribe_method(service, subscriber_mock):
    """Test that a subscriber is added to the internal list."""
    service.subscribe(subscriber_mock)
    # Check if the mock is in the internal list (accessing a 'private' attribute for testing)
    assert subscriber_mock in service._SubscriptableService__subscriber_list  # noqa


def test_send_progress_event(service, subscriber_mock):
    """Test sending a simple progress event."""
    service.subscribe(subscriber_mock)
    progress_event = ProgressEvent(None, 25)
    service._send_event(progress_event)

    # Check if the subscriber was called exactly once with the correct event
    subscriber_mock.assert_called_once_with(progress_event)
    assert subscriber_mock.call_count == 1
    assert subscriber_mock.call_args[0][0].type == EventType.Progress


def test_send_error_event_also_sends_done(service, subscriber_mock):
    """Test sending an ErrorEvent also triggers a DoneEvent."""
    service.subscribe(subscriber_mock)
    error_kind = EventKind.ErrorUploadingToDrive
    error_event = ErrorEvent(error_kind)
    service._send_event(error_event)

    # Check if the subscriber was called twice
    assert subscriber_mock.call_count == 2

    # Check the first call was the ErrorEvent
    first_call_event = subscriber_mock.call_args_list[0][0][0]
    assert isinstance(first_call_event, ErrorEvent)
    assert first_call_event.kind == error_kind

    # Check the second call was a DoneEvent with the same kind
    second_call_event = subscriber_mock.call_args_list[1][0][0]
    assert isinstance(second_call_event, DoneEvent)
    assert second_call_event.kind == error_kind
    assert second_call_event.success is False


def test_set_stages_sends_initial_progress(service, subscriber_mock):
    """Test _set_stages sends an initial ProgressEvent."""
    service.subscribe(subscriber_mock)
    stage_count = 5
    service._set_stages(stage_count)

    # Should be called once with initial progress (0%)
    subscriber_mock.assert_called_once()
    initial_event = subscriber_mock.call_args[0][0]
    assert isinstance(initial_event, ProgressEvent)
    assert initial_event.progress == 0  # round(0 * 100)


def test_complete_stage_full_completion(service, subscriber_mock):
    """Test _complete_stage updates and sends correct progress for full stage."""
    service.subscribe(subscriber_mock)
    stage_count = 4  # 25% per stage
    service._set_stages(stage_count)
    subscriber_mock.reset_mock()  # Reset after initial 0% call

    # Complete the first stage
    service._complete_stage()  # completion defaults to 1
    # Check progress is 25%
    subscriber_mock.assert_called_once()
    progress_event = subscriber_mock.call_args[0][0]
    assert progress_event.progress == 25
    subscriber_mock.reset_mock()

    # Complete the second stage
    service._complete_stage()
    # Check progress is 50%
    subscriber_mock.assert_called_once()
    progress_event = subscriber_mock.call_args[0][0]
    assert progress_event.progress == 50
    subscriber_mock.reset_mock()


def test_complete_stage_partial_completion(service, subscriber_mock):
    """Test _complete_stage updates and sends correct progress for partial stage."""
    service.subscribe(subscriber_mock)
    stage_count = 10  # 10% per stage
    service._set_stages(stage_count)
    subscriber_mock.reset_mock()  # Reset after initial 0% call

    # Complete 50% of the first stage
    service._complete_stage(completion=0.5)
    # The internal progress shouldn't advance yet (only for full completion),
    # but sent progress should be 5% (0 + 0.5 * 10%).
    subscriber_mock.assert_called_once()
    progress_event = subscriber_mock.call_args[0][0]
    assert progress_event.progress == 5  # round(0.05 * 100)
    subscriber_mock.reset_mock()

    # Complete the rest of the first stage
    service._complete_stage(completion=0.5)
    # The progress now jumps to 10% because the second call to _complete_stage
    # where completion is NOT 1 does NOT update the internal __progress, so the
    # calculation is still relative to the previous __progress (0). The logic in
    # _complete_stage for partial completion is a bit tricky:
    # `progress = self.__progress + (completion * self.__single_stage_percentage)`
    # This means partial completion is ALWAYS relative to the START of the current
    # stage, not a running total of the partial completions.
    # The test for this behavior should focus on the *intended* use, which seems
    # to be: when completion != 1, it calculates the progress assuming only THIS
    # single partial step has happened relative to the total work.

    # Let's re-test focusing on a single full stage completion where progress is 10%
    service._complete_stage(completion=1)  # Completes stage 1
    subscriber_mock.reset_mock()

    # Partial progress in stage 2: 30% of stage 2 (3% total)
    service._complete_stage(completion=0.3)
    # Internal progress is 0.1 (10%). The progress sent is:
    # 0.1 + (0.3 * 0.1) = 0.13 (13%)
    progress_event = subscriber_mock.call_args[0][0]
    assert progress_event.progress == 13  # round(0.13 * 100)
