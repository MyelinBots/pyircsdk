import unittest
from unittest.mock import MagicMock

from pyircsdk import IRCSDK, IRCSDKConfig, Message
from pyircsdk.event.event import Event


class TestHighVolumeMessages(unittest.TestCase):
    """Tests for handling large volumes of IRC messages"""

    def setUp(self):
        config = IRCSDKConfig(host='irc.example.com', port=6667, ssl=False)
        self.irc = IRCSDK(config)
        self.irc.irc = MagicMock()

    def test_handle_100_messages_in_single_buffer(self):
        """Test processing 100 messages received in a single buffer"""
        message_count = 100
        received_messages = []

        def capture_message(msg):
            received_messages.append(msg)

        self.irc.event.on('message', capture_message)

        # Build a buffer with 100 PRIVMSG lines
        lines = []
        for i in range(message_count):
            lines.append(f':user{i}!user@host PRIVMSG #channel :Message number {i}')
        raw = ('\r\n'.join(lines) + '\r\n').encode('utf-8')

        self.irc.handle_raw_message(raw)

        self.assertEqual(len(received_messages), message_count)
        # Verify first and last messages
        self.assertEqual(received_messages[0].messageFrom, 'user0')
        self.assertEqual(received_messages[99].messageFrom, 'user99')

    def test_handle_1000_messages_in_single_buffer(self):
        """Test processing 1000 messages received in a single buffer"""
        message_count = 1000
        received_messages = []

        def capture_message(msg):
            received_messages.append(msg)

        self.irc.event.on('message', capture_message)

        lines = []
        for i in range(message_count):
            lines.append(f':user{i}!user@host PRIVMSG #channel :Message {i}')
        raw = ('\r\n'.join(lines) + '\r\n').encode('utf-8')

        self.irc.handle_raw_message(raw)

        self.assertEqual(len(received_messages), message_count)

    def test_handle_mixed_message_types_high_volume(self):
        """Test processing a mix of different IRC message types"""
        received_messages = []
        connected_events = []

        def capture_message(msg):
            received_messages.append(msg)

        def capture_connected(data):
            connected_events.append(data)

        self.irc.event.on('message', capture_message)
        self.irc.event.on('connected', capture_connected)

        lines = []
        # Mix of message types
        for i in range(200):
            lines.append(f':user{i}!user@host PRIVMSG #channel :Hello {i}')
        for i in range(50):
            lines.append(f'PING :server{i}')
        for i in range(100):
            lines.append(f':user{i}!user@host JOIN #channel{i}')
        for i in range(50):
            lines.append(f':user{i}!user@host PART #channel :Leaving')
        # Add MOTD end to trigger connected event
        lines.append(':server 376 nick :End of /MOTD command.')

        raw = ('\r\n'.join(lines) + '\r\n').encode('utf-8')
        self.irc.handle_raw_message(raw)

        # Should have received all messages (PRIVMSG + PING + JOIN + PART + 376)
        self.assertEqual(len(received_messages), 401)
        # Should have 50 PONG responses
        self.assertEqual(self.irc.irc.send.call_count, 50)
        # Should have triggered connected event
        self.assertEqual(len(connected_events), 1)

    def test_rapid_sequential_message_processing(self):
        """Test processing many small buffers in rapid succession"""
        message_count = 500
        received_messages = []

        def capture_message(msg):
            received_messages.append(msg)

        self.irc.event.on('message', capture_message)

        for i in range(message_count):
            raw = f':user!user@host PRIVMSG #channel :Message {i}\r\n'.encode('utf-8')
            self.irc.handle_raw_message(raw)

        self.assertEqual(len(received_messages), message_count)

    def test_large_message_content(self):
        """Test handling messages with large content (close to IRC limit)"""
        received_messages = []

        def capture_message(msg):
            received_messages.append(msg)

        self.irc.event.on('message', capture_message)

        # IRC messages can be up to 512 bytes, content up to ~400 chars
        large_content = 'A' * 400
        lines = []
        for i in range(100):
            lines.append(f':user!user@host PRIVMSG #channel :{large_content}')
        raw = ('\r\n'.join(lines) + '\r\n').encode('utf-8')

        self.irc.handle_raw_message(raw)

        self.assertEqual(len(received_messages), 100)
        for msg in received_messages:
            self.assertEqual(len(msg.message), 400)

    def test_no_message_loss_under_load(self):
        """Verify no messages are lost when processing large volumes"""
        message_ids = set()
        received_ids = []

        def capture_message(msg):
            # Extract the ID from the message
            if msg.message and msg.message.startswith('ID:'):
                received_ids.append(int(msg.message[3:]))

        self.irc.event.on('message', capture_message)

        message_count = 1000
        lines = []
        for i in range(message_count):
            message_ids.add(i)
            lines.append(f':user!user@host PRIVMSG #channel :ID:{i}')
        raw = ('\r\n'.join(lines) + '\r\n').encode('utf-8')

        self.irc.handle_raw_message(raw)

        # Verify we got all messages
        self.assertEqual(len(received_ids), message_count)
        # Verify no duplicates
        self.assertEqual(len(set(received_ids)), message_count)
        # Verify correct IDs
        self.assertEqual(set(received_ids), message_ids)


class TestEventSystemHighVolume(unittest.TestCase):
    """Tests for event system under high load"""

    def test_many_listeners_same_event(self):
        """Test firing event with many listeners"""
        event = Event()
        listener_count = 100
        call_counts = [0] * listener_count

        for i in range(listener_count):
            idx = i  # Capture in closure
            event.on('test', lambda data, idx=idx: call_counts.__setitem__(idx, call_counts[idx] + 1))

        # Fire event 100 times
        for _ in range(100):
            event.emit('test', 'data')

        # Each listener should have been called 100 times
        for count in call_counts:
            self.assertEqual(count, 100)

    def test_many_different_events(self):
        """Test system with many different event types"""
        event = Event()
        event_count = 100
        results = {}

        for i in range(event_count):
            event_name = f'event_{i}'
            results[event_name] = []
            event.on(event_name, lambda data, name=event_name: results[name].append(data))

        # Fire each event
        for i in range(event_count):
            event.emit(f'event_{i}', f'data_{i}')

        # Verify each event was fired correctly
        for i in range(event_count):
            self.assertEqual(results[f'event_{i}'], [f'data_{i}'])

    def test_rapid_event_emission(self):
        """Test rapid emission of events"""
        event = Event()
        received = []

        event.on('rapid', lambda data: received.append(data))

        emission_count = 10000
        for i in range(emission_count):
            event.emit('rapid', i)

        self.assertEqual(len(received), emission_count)
        self.assertEqual(received, list(range(emission_count)))


class TestMessageParsingPerformance(unittest.TestCase):
    """Tests for message parsing under load"""

    def setUp(self):
        config = IRCSDKConfig(host='irc.example.com', port=6667, ssl=False)
        self.irc = IRCSDK(config)

    def test_parse_1000_messages(self):
        """Test parsing 1000 individual messages"""
        messages = [
            ':nick!user@host PRIVMSG #channel :Hello world',
            'PING :server.example.com',
            ':server 376 nick :End of /MOTD',
            ':nick!user@host JOIN #channel',
            ':nick!user@host PART #channel :Goodbye',
        ]

        parse_count = 1000
        for i in range(parse_count):
            msg = messages[i % len(messages)]
            data, prefix, command, params, trailing = self.irc.parse_message(msg)
            self.assertIsNotNone(command)

    def test_parse_complex_messages(self):
        """Test parsing messages with complex content"""
        complex_messages = [
            ':nick!user@host PRIVMSG #channel :Check out https://example.com/path?query=value&other=123',
            ':nick!user@host PRIVMSG #channel :Special chars: <>&"\' and unicode: éàü',
            ':nick!user@host PRIVMSG #channel :Emoji test (encoded): :) :( :D',
            ':server 353 nick = #channel :@op +voice regular',
            ':nick!user@host KICK #channel target :Reason for kick with spaces',
        ]

        for _ in range(200):
            for msg in complex_messages:
                data, prefix, command, params, trailing = self.irc.parse_message(msg)
                self.assertIsNotNone(command)


class TestBufferHandling(unittest.TestCase):
    """Tests for various buffer scenarios"""

    def setUp(self):
        config = IRCSDKConfig(host='irc.example.com', port=6667, ssl=False)
        self.irc = IRCSDK(config)
        self.irc.irc = MagicMock()

    def test_empty_lines_in_buffer(self):
        """Test handling buffer with empty lines"""
        received_messages = []
        self.irc.event.on('message', lambda msg: received_messages.append(msg))

        # Buffer with empty lines mixed in (double \r\n)
        raw = b':user!user@host PRIVMSG #channel :msg1\r\n\r\n:user!user@host PRIVMSG #channel :msg2\r\n'
        self.irc.handle_raw_message(raw)

        self.assertEqual(len(received_messages), 2)

    def test_partial_unicode_handling(self):
        """Test handling unicode characters in messages"""
        received_messages = []
        self.irc.event.on('message', lambda msg: received_messages.append(msg))

        # Message with unicode
        raw = ':user!user@host PRIVMSG #channel :Héllo wörld 你好\r\n'.encode('utf-8')
        self.irc.handle_raw_message(raw)

        self.assertEqual(len(received_messages), 1)
        self.assertIn('Héllo', received_messages[0].message)

    def test_maximum_line_length(self):
        """Test handling messages at maximum IRC line length"""
        received_messages = []
        self.irc.event.on('message', lambda msg: received_messages.append(msg))

        # Create a message close to 512 byte limit
        prefix = ':user!user@host PRIVMSG #channel :'
        max_content_len = 512 - len(prefix) - 2  # -2 for \r\n
        content = 'X' * max_content_len

        raw = f'{prefix}{content}\r\n'.encode('utf-8')
        self.irc.handle_raw_message(raw)

        self.assertEqual(len(received_messages), 1)

    def test_fragmented_messages(self):
        """Test that fragmented messages across multiple recv calls work"""
        received_messages = []
        self.irc.event.on('message', lambda msg: received_messages.append(msg))

        # Simulate fragmented receive
        fragments = [
            b':user!user@host PRIV',
            b'MSG #channel :Hello ',
            b'world\r\n:user!user@host ',
            b'PRIVMSG #channel :Second message\r\n',
        ]

        for fragment in fragments:
            self.irc.handle_raw_message(fragment)

        self.assertEqual(len(received_messages), 2)
        self.assertEqual(received_messages[0].message, 'Hello world')
        self.assertEqual(received_messages[1].message, 'Second message')

    def test_buffer_state_preserved(self):
        """Test that buffer state is preserved across calls"""
        self.irc.handle_raw_message(b'PING :incomplete')
        self.assertEqual(self.irc._recv_buffer, 'PING :incomplete')

        self.irc.handle_raw_message(b'_server\r\n')
        self.assertEqual(self.irc._recv_buffer, '')
        self.irc.irc.send.assert_called_once_with(b'PONG incomplete_server\r\n')


if __name__ == '__main__':
    unittest.main()
