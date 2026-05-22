import logging
import threading
import time
import urllib.request


_started = False


def start_keep_alive(app):
    """Start an optional background ping loop for Render free-tier deployments."""
    global _started

    if _started or app.config.get("TESTING"):
        return
    if not app.config.get("KEEP_ALIVE_ENABLED"):
        return

    url = app.config.get("KEEP_ALIVE_URL")
    if not url:
        app.logger.warning("KEEP_ALIVE_ENABLED is true, but KEEP_ALIVE_URL is empty.")
        return

    interval = app.config.get("KEEP_ALIVE_INTERVAL_SECONDS", 600)
    logger_name = app.logger.name
    thread = threading.Thread(
        target=_ping_loop,
        args=(url, interval, logger_name),
        daemon=True,
        name="keep-alive-pinger",
    )
    thread.start()
    _started = True
    app.logger.info("Keep-alive pinger started for %s every %s seconds.", url, interval)


def _ping_loop(url, interval, logger_name):
    logger = logging.getLogger(logger_name)
    headers = {"User-Agent": "ai-interview-assistant-keepalive/1.0"}

    while True:
        time.sleep(interval)
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=15) as response:
                logger.info("Keep-alive ping returned HTTP %s.", response.status)
        except Exception as error:
            logger.warning("Keep-alive ping failed: %s", error)
