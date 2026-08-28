import os
import sys
import subprocess
import logging

logger = logging.getLogger("anker_solix.shutdown")


class ShutdownHandler:
    def __init__(self, notify_script="/usr/local/emhttp/webGui/scripts/notify"):
        self.notify_script = notify_script

    def send_notification(self, subject="Anker Solix Power Alert", message="", severity="normal"):
        """
        Sends native Unraid WebGUI notification using the notify script.
        """
        if os.path.exists(self.notify_script):
            cmd = [self.notify_script, "-e", "Anker Solix Plugin", "-s", subject, "-d", message, "-i", severity]
            try:
                subprocess.run(cmd, check=True)
            except Exception as e:
                logger.error(f"Failed to send Unraid notification: {e}")
        else:
            logger.info(f"[SIMULATED NOTIFY] {subject}: {message} (Severity: {severity})")

    def execute_graceful_shutdown(self, reason="", dry_run=False):
        """
        Executes multi-stage orderly shutdown:
        1. NOTIFICATION
        2. STOP_DOCKER
        3. STOP_VMS
        4. STOP_ARRAY
        5. POWEROFF
        """
        actions = []

        # Stage 1: Send Urgent Notification
        msg = f"Initiating graceful server shutdown. Reason: {reason}"
        logger.warning(msg)
        self.send_notification(subject="Power Outage - Graceful Shutdown Active", message=msg, severity="alert")
        actions.append({"stage": "NOTIFICATION", "status": "COMPLETED", "message": msg})

        # Stage 2: Stop Docker Containers
        logger.info("Stage 2: Stopping running Docker containers...")
        if not dry_run and os.path.exists("/usr/bin/docker"):
            try:
                subprocess.run(["docker", "stop", "$(docker ps -q)"], shell=True, check=False)
            except Exception as e:
                logger.error(f"Error stopping Docker containers: {e}")
        actions.append({"stage": "STOP_DOCKER", "status": "COMPLETED"})

        # Stage 3: Stop Virtual Machines
        logger.info("Stage 3: Shutting down Virtual Machines...")
        if not dry_run and os.path.exists("/usr/bin/virsh"):
            try:
                subprocess.run(["virsh", "shutdown"], check=False)
            except Exception as e:
                logger.error(f"Error shutting down VMs: {e}")
        actions.append({"stage": "STOP_VMS", "status": "COMPLETED"})

        # Stage 4: Unmount & Stop Array
        logger.info("Stage 4: Safely unmounting and stopping Unraid Array...")
        if not dry_run and os.path.exists("/usr/local/emhttp/webGui/scripts/rc.disk"):
            try:
                subprocess.run(["/usr/local/emhttp/webGui/scripts/rc.disk", "stop"], check=False)
            except Exception as e:
                logger.error(f"Error stopping Unraid array: {e}")
        actions.append({"stage": "STOP_ARRAY", "status": "COMPLETED"})

        # Stage 5: System Power Off
        logger.critical("Stage 5: Issuing system poweroff command...")
        if not dry_run:
            try:
                subprocess.run(["/sbin/poweroff"], check=False)
            except Exception as e:
                logger.error(f"Error issuing poweroff: {e}")
        actions.append({"stage": "POWEROFF", "status": "EXECUTED" if not dry_run else "SIMULATED"})

        return actions


if __name__ == '__main__':
    handler = ShutdownHandler()
    handler.execute_graceful_shutdown(reason="Manual Test Trigger", dry_run=True)
