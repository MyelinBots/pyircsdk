import unittest
from unittest.mock import MagicMock
from pyircsdk.event.event import Event


class TestEventMethods(unittest.TestCase):

    def test_create_event(self):
        event = Event()
        self.assertTrue(event)
        self.assertEqual(event.listeners, {})

    def test_fire_event(self):
        mock = MagicMock()
        event = Event()
        event.on('test', mock)
        event.emit('test', 'hello')
        mock.assert_called_with('hello')

    def test_fire_event_no_listener(self):
        event = Event()
        event.emit('test', 'hello')
        self.assertTrue(True)

    def test_multiple_listeners_same_event(self):
        mock1 = MagicMock()
        mock2 = MagicMock()
        event = Event()
        event.on('test', mock1)
        event.on('test', mock2)
        event.emit('test', 'data')
        mock1.assert_called_with('data')
        mock2.assert_called_with('data')

    def test_multiple_different_events(self):
        mock1 = MagicMock()
        mock2 = MagicMock()
        event = Event()
        event.on('event1', mock1)
        event.on('event2', mock2)
        event.emit('event1', 'data1')
        mock1.assert_called_with('data1')
        mock2.assert_not_called()

    def test_emit_with_various_data_types(self):
        mock = MagicMock()
        event = Event()
        event.on('test', mock)

        event.emit('test', None)
        mock.assert_called_with(None)

        event.emit('test', 123)
        mock.assert_called_with(123)

        event.emit('test', {'key': 'value'})
        mock.assert_called_with({'key': 'value'})

        event.emit('test', ['a', 'b', 'c'])
        mock.assert_called_with(['a', 'b', 'c'])

    def test_remove_listener(self):
        mock = MagicMock()
        event = Event()
        event.on('test', mock)
        event.emit('test', 'first')
        mock.assert_called_with('first')

        event.remove('test', mock)
        mock.reset_mock()
        event.emit('test', 'second')
        mock.assert_not_called()

    def test_remove_nonexistent_listener(self):
        mock = MagicMock()
        event = Event()
        # Should not raise
        event.remove('test', mock)
        event.on('test', mock)
        event.remove('test', lambda x: x)  # Different callback

    def test_remove_all_listeners(self):
        mock1 = MagicMock()
        mock2 = MagicMock()
        event = Event()
        event.on('test', mock1)
        event.on('test', mock2)

        event.remove_all('test')
        event.emit('test', 'data')

        mock1.assert_not_called()
        mock2.assert_not_called()

    def test_remove_all_nonexistent_event(self):
        event = Event()
        # Should not raise
        event.remove_all('nonexistent')


if __name__ == '__main__':
    unittest.main()
