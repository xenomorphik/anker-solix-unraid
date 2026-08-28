import unittest
from unittest.mock import patch, call
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../usr/local/emhttp/plugins/anker-solix')))

from shutdown_handler import ShutdownHandler


class TestShutdownHandler(unittest.TestCase):
    def setUp(self):
        self.handler = ShutdownHandler()

    @patch('subprocess.run')
    def test_multi_stage_shutdown_sequence(self, mock_run):
        # Dry run simulation of shutdown sequence
        actions = self.handler.execute_graceful_shutdown(reason="Battery Low (15%)", dry_run=True)
        
        expected_stages = [
            "NOTIFICATION",
            "STOP_DOCKER",
            "STOP_VMS",
            "STOP_ARRAY",
            "POWEROFF"
        ]
        self.assertEqual(len(actions), 5)
        for idx, stage in enumerate(expected_stages):
            self.assertEqual(actions[idx]["stage"], stage)

    @patch('os.path.exists', return_value=True)
    @patch('subprocess.run')
    def test_send_unraid_notification(self, mock_run, mock_exists):
        self.handler.send_notification(subject="Anker Solix Power Alert", message="Operating on battery power", severity="warning")
        
        # Verify subprocess call to /usr/local/emhttp/webGui/scripts/notify
        self.assertTrue(mock_run.called)
        args, kwargs = mock_run.call_args
        cmd = args[0]
        self.assertIn("notify", cmd[0])
        self.assertIn("-s", cmd)
        self.assertIn("Anker Solix Power Alert", cmd)


if __name__ == '__main__':
    unittest.main()
