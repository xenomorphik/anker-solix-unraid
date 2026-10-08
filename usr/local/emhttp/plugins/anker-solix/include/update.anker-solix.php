<?php
// Post-update hook called after saving /boot/config/plugins/anker-solix/anker-solix.cfg
// Restart services to apply new credentials or thresholds
shell_exec("/etc/rc.d/rc.anker-solix restart >/dev/null 2>&1 &");
?>
