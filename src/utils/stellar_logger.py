"""
stellar_logger.py — Live monitoring & content mirroring for Stars Manager.

Two separate Telegram channels, two separate bots:

  STELLAR channel  (STELLAR_BOT_TOKEN  + STELLAR_CHANNEL_ID)
  ─────────────────────────────────────────────────────────
  · Live log stream: captures every print() from every module automatically
  · Workflow start / end notifications with timestamp
  · No configuration needed in other files — stdout interception does it all

  CONTENT channel  (TELEGRAM_BOT_TOKEN + TELEGRAM_CHANNEL_ID)
  ─────────────────────────────────────────────────────────
  · Receives the exact same post published to X (text + image)
  · Called from twitter_bot.py after a successful Twitter publish
  · publish_to_content_channel(text, image_path) is the public API

Usage — add 2 lines to each workflow entry point (main, writer_agent, etc.):

    from utils.stellar_logger import setup_stellar_monitoring
    setup_stellar_monitoring("📝 Writer Agent")

After a successful post:

    from utils.stellar_logger import publish_to_content_channel
    publish_to_content_channel(tweet_text, "/abs/path/to/image.png")
"""

import atexit
import logging
import os
import queue
import sys
import threading
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler

import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_TG_URL = "https://api.telegram.org/bot{token}/{method}"
_RATE_SLEEP = 0.08          # ~12 messages/sec — well below Telegram's 30/sec limit
_MAX_QUEUE  = 500           # drop messages silently if queue is full
_MSG_LIMIT  = 4096          # Telegram's hard cap per message

# Prevent re-entrant calls from _forward_line (e.g. requests printing to stdout)
_reentrant = threading.local()

# ---------------------------------------------------------------------------
# Internal state — set by setup_stellar_monitoring()
# ---------------------------------------------------------------------------

_stellar_sender: "_TelegramSender | None" = None
_workflow_name: str = "unknown"
_original_stdout = sys.stdout   # saved before we wrap it


# ---------------------------------------------------------------------------
# Async queue-based Telegram sender
# ---------------------------------------------------------------------------

class _TelegramSender:
    """
    Drains a queue in a daemon thread and POSTs to Telegram.
    Non-blocking for the main thread. Drops oldest messages if the queue fills.
    """

    def __init__(self, token: str, channel_id: str):
        self._token      = token
        self._channel_id = channel_id
        self._q          = queue.Queue(maxsize=_MAX_QUEUE)
        self._thread     = threading.Thread(
            target=self._worker, daemon=True, name="StellarSender"
        )
        self._thread.start()
        atexit.register(self._flush_on_exit)

    # ------------------------------------------------------------------

    def send_text(self, text: str):
        """Enqueue a plain-text message. Non-blocking."""
        self._enqueue({"text": text[:_MSG_LIMIT], "parse_mode": "HTML"})

    def send_photo(self, image_path: str, caption: str | None = None):
        """Enqueue a photo upload."""
        self._enqueue({"_image_path": image_path, "caption": (caption or "")[:1024]})

    # ------------------------------------------------------------------

    def _enqueue(self, payload: dict):
        try:
            self._q.put_nowait(payload)
        except queue.Full:
            pass  # drop silently — monitoring must never crash the main flow

    def _worker(self):
        while True:
            try:
                payload = self._q.get(timeout=1)
                self._send(payload)
                self._q.task_done()
                time.sleep(_RATE_SLEEP)
            except queue.Empty:
                continue
            except Exception:
                pass  # never crash the daemon thread

    def _send(self, payload: dict):
        try:
            if "_image_path" in payload:
                path = payload.pop("_image_path")
                url  = _TG_URL.format(token=self._token, method="sendPhoto")
                payload["chat_id"] = self._channel_id
                with open(path, "rb") as img:
                    requests.post(url, data=payload, files={"photo": img}, timeout=15)
            else:
                url = _TG_URL.format(token=self._token, method="sendMessage")
                payload["chat_id"] = self._channel_id
                requests.post(url, data=payload, timeout=15)
        except Exception:
            pass  # Telegram errors must never propagate

    def _flush_on_exit(self):
        """Wait up to 5 s for the queue to drain before the process exits."""
        try:
            self._q.join()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# stdout interceptor — captures every print() in the entire process
# ---------------------------------------------------------------------------

class _StellarStream:
    """
    Wraps sys.stdout.  Every complete line is forwarded to the Stellar channel.
    The original stdout still receives everything — console output is preserved.
    """

    def __init__(self, original):
        self._original = original
        self._buf      = ""

    def write(self, text: str):
        self._original.write(text)
        self._buf += text
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            _forward_line(line)

    def flush(self):
        self._original.flush()
        if self._buf.strip():
            _forward_line(self._buf)
            self._buf = ""

    def __getattr__(self, name):
        return getattr(self._original, name)


def _forward_line(line: str):
    """Format and enqueue a single log line for the Stellar channel."""
    if getattr(_reentrant, "active", False):
        return  # guard against re-entrant calls (e.g. requests lib)
    if not _stellar_sender:
        return
    stripped = line.strip()
    if not stripped:
        return

    _reentrant.active = True
    try:
        now = datetime.now().strftime("%H:%M:%S")
        msg = (
            f"<code>[{_workflow_name}]</code>  <code>{now}</code>\n"
            f"{stripped}"
        )
        _stellar_sender.send_text(msg)
    finally:
        _reentrant.active = False


# ---------------------------------------------------------------------------
# Public API — Stellar (log) channel
# ---------------------------------------------------------------------------

def setup_stellar_monitoring(workflow: str = "unknown"):
    """
    Activate live monitoring for this workflow.

    Call once at the very top of each entry-point script (writer_agent.main(),
    image_agent.main(), twitter_bot.post_content(), main.run(), etc.).

    Args:
        workflow: Human-readable label shown as prefix in every Telegram message.
                  Recommended format:  "📝 Writer Agent" / "🎨 Image Agent" / etc.
    """
    global _stellar_sender, _workflow_name

    _workflow_name = workflow

    token      = os.getenv("STELLAR_BOT_TOKEN")
    channel_id = os.getenv("STELLAR_CHANNEL_ID")

    if not token or not channel_id:
        # Degraded mode — log locally, skip Telegram
        _setup_local_logger()
        return

    _stellar_sender = _TelegramSender(token, channel_id)

    # Wrap stdout once — idempotent
    if not isinstance(sys.stdout, _StellarStream):
        sys.stdout = _StellarStream(sys.stdout)

    _setup_local_logger()

    # Announce workflow start
    _stellar_sender.send_text(
        f"🚀  <b>Workflow iniciado</b>\n"
        f"<code>{workflow}</code>  ·  {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}"
    )


def notify_workflow_end(success: bool = True, error: str | None = None):
    """
    Send a completion / failure summary to the Stellar channel.
    Call in a finally block or at the end of each entry point.
    """
    if not _stellar_sender:
        return
    if success:
        _stellar_sender.send_text(
            f"✅  <b>Workflow completado</b>\n"
            f"<code>{_workflow_name}</code>  ·  {datetime.now().strftime('%H:%M:%S')}"
        )
    else:
        _stellar_sender.send_text(
            f"❌  <b>Workflow fallido</b>\n"
            f"<code>{_workflow_name}</code>\n"
            f"Error: {error or 'desconocido'}"
        )


# ---------------------------------------------------------------------------
# Public API — Content channel
# ---------------------------------------------------------------------------

def publish_to_content_channel(text: str, image_path: str | None = None) -> bool:
    """
    Mirror a published post to the Telegram CONTENT channel.

    Uses TELEGRAM_BOT_TOKEN + TELEGRAM_CHANNEL_ID (separate from Stellar).
    Thread separators (---) are converted to a horizontal rule for Telegram.

    Args:
        text:       The tweet/post text (can contain "---" thread separators).
        image_path: Absolute path to the generated image, or None.

    Returns:
        True if the message was sent successfully, False otherwise.
    """
    token      = os.getenv("TELEGRAM_BOT_TOKEN")
    channel_id = os.getenv("TELEGRAM_CHANNEL_ID")

    if not token or not channel_id:
        print("⚠️  stellar_logger: TELEGRAM_BOT_TOKEN/CHANNEL_ID no configurados — content channel omitido.")
        return False

    # Normalise thread separators for Telegram (no native thread support)
    clean = text.replace("\n---\n", "\n\n─────────\n\n").replace("---", "\n─────────\n")

    try:
        if image_path and os.path.exists(image_path):
            _content_send_photo(token, channel_id, image_path, clean)
        else:
            _content_send_text(token, channel_id, clean)

        print("✅  stellar_logger: post replicado en canal de contenido de Telegram.")
        return True

    except Exception as e:
        print(f"❌  stellar_logger: error publicando en canal de contenido — {e}")
        return False


def _content_send_text(token: str, channel_id: str, text: str):
    url = _TG_URL.format(token=token, method="sendMessage")
    requests.post(url, data={
        "chat_id":    channel_id,
        "text":       text[:_MSG_LIMIT],
        "parse_mode": "HTML",
    }, timeout=15).raise_for_status()


def _content_send_photo(token: str, channel_id: str, image_path: str, caption: str):
    if len(caption) <= 1024:
        url = _TG_URL.format(token=token, method="sendPhoto")
        with open(image_path, "rb") as img:
            requests.post(url, data={
                "chat_id":    channel_id,
                "caption":    caption,
                "parse_mode": "HTML",
            }, files={"photo": img}, timeout=30).raise_for_status()
    else:
        # Caption too long — send image first, then text separately
        url_photo = _TG_URL.format(token=token, method="sendPhoto")
        with open(image_path, "rb") as img:
            requests.post(url_photo, data={"chat_id": channel_id},
                          files={"photo": img}, timeout=30).raise_for_status()
        _content_send_text(token, channel_id, caption)


# ---------------------------------------------------------------------------
# Local file logger (always available, regardless of Telegram config)
# ---------------------------------------------------------------------------

def _setup_local_logger() -> logging.Logger:
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    _logger = logging.getLogger("StarsManager")
    _logger.setLevel(logging.DEBUG)

    if _logger.handlers:
        return _logger  # already configured — avoid duplicate handlers

    # Console handler → goes to (possibly intercepted) stdout
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    console.setLevel(logging.INFO)
    _logger.addHandler(console)

    # Rotating file handler → local disk only
    try:
        fh = RotatingFileHandler(
            os.path.join(log_dir, "stellar_activity.log"),
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        fh.setFormatter(fmt)
        fh.setLevel(logging.DEBUG)
        _logger.addHandler(fh)
    except Exception:
        pass  # file logging is optional

    return _logger


# Global logger — importable by any module that wants structured logging
logger = _setup_local_logger()