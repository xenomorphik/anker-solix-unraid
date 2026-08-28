import unittest
import os
import tempfile
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../usr/local/emhttp/plugins/anker-solix')))

from solix_daemon import SolixDaemon


class TestConfigReader(unittest.TestCase):
    def test_parse_valid_cfg(self):
        with tempfile.NamedTemporaryFile("w+", delete=False) as tf:
            tf.write('ANKERUSER="admin@example.com"\n')
            tf.write('ANKERPASSWORD="mypassword123"\n')
            tf.write('ANKERCOUNTRY="us"\n')
            tf.write('POLL_INTERVAL="15"\n')
            tf.write('TIME_LIMIT_MIN="20"\n')
            tf.write('BATTERY_LIMIT_PCT="25"\n')
            tf.flush()
            
            daemon = SolixDaemon(config_path=tf.name)
            cfg = daemon.read_config()
            
            self.assertEqual(cfg["ANKERUSER"], "admin@example.com")
            self.assertEqual(cfg["ANKERPASSWORD"], "mypassword123")
            self.assertEqual(cfg["ANKERCOUNTRY"], "us")
            self.assertEqual(cfg["POLL_INTERVAL"], "15")
            self.assertEqual(cfg["TIME_LIMIT_MIN"], "20")
            self.assertEqual(cfg["BATTERY_LIMIT_PCT"], "25")
            
        os.remove(tf.name)


if __name__ == '__main__':
    unittest.main()
