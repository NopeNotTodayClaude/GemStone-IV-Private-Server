"""
persistence_writer.py
---------------------
Moves hot fire-and-forget SQL writes off the world authority loop.
"""

from __future__ import annotations

import logging
import multiprocessing as mp
import queue
import time

import mysql.connector

log = logging.getLogger(__name__)


def _db_config_from_config(config) -> dict:
    primary = {
        "host": config.get("database.development.host", "127.0.0.1"),
        "port": int(config.get("database.development.port", 3306) or 3306),
        "database": config.get("database.development.database", "gemstone_dev"),
        "user": config.get("database.development.username", "gemstone"),
        "password": config.get("database.development.password", "gemstone_dev"),
        "charset": "utf8mb4",
        "autocommit": True,
    }
    fallback = {
        "host": "127.0.0.1",
        "port": 3306,
        "database": "gemstone_dev",
        "user": "root",
        "password": "",
        "charset": "utf8mb4",
        "autocommit": True,
    }
    return {"primary": primary, "fallback": fallback}


def _open_writer_conn(db_options: dict):
    errors: list[str] = []
    for key in ("primary", "fallback"):
        opts = dict(db_options.get(key) or {})
        if not opts:
            continue
        try:
            return mysql.connector.connect(**opts)
        except Exception as exc:
            errors.append(f"{key}: {exc}")
    raise RuntimeError("; ".join(errors) or "no DB options available")


def _writer_main(db_options: dict, task_queue, stop_event, flush_event):
    conn = None
    while True:
        if stop_event.is_set() and task_queue.empty():
            break
        try:
            task = task_queue.get(timeout=0.5)
        except queue.Empty:
            if flush_event is not None and task_queue.empty():
                flush_event.set()
            continue
        if task is None:
            if stop_event.is_set():
                break
            continue
        sql = str(task.get("sql") or "").strip()
        params = tuple(task.get("params") or ())
        if not sql:
            continue
        attempts = 0
        while attempts < 2:
            attempts += 1
            try:
                if conn is None or not conn.is_connected():
                    conn = _open_writer_conn(db_options)
                cur = conn.cursor()
                cur.execute(sql, params)
                conn.commit()
                break
            except Exception as exc:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass
                    conn = None
                if attempts >= 2:
                    print(f"[PersistenceWriter] SQL failed: {exc} | {sql[:140]}")
                else:
                    time.sleep(0.15)
        if flush_event is not None and task_queue.empty():
            flush_event.set()
    if conn is not None:
        try:
            conn.close()
        except Exception:
            pass


class PersistenceWriterService:
    def __init__(self, config):
        self._config = config
        self._ctx = mp.get_context("spawn")
        self._queue = None
        self._stop_event = None
        self._flush_event = None
        self._process = None
        self._enabled = False

    def start(self):
        workers_enabled = bool(self._config.get("services.persistence_writer.enabled", True))
        if not workers_enabled:
            log.info("PersistenceWriter disabled by config")
            return
        max_queue = max(128, int(self._config.get("services.persistence_writer.queue_size", 2048) or 2048))
        self._queue = self._ctx.Queue(maxsize=max_queue)
        self._stop_event = self._ctx.Event()
        self._flush_event = self._ctx.Event()
        self._process = self._ctx.Process(
            target=_writer_main,
            args=(_db_config_from_config(self._config), self._queue, self._stop_event, self._flush_event),
            name="GemStonePersistenceWriter",
            daemon=True,
        )
        self._process.start()
        self._enabled = True
        log.info("PersistenceWriter ready (pid=%s, queue=%d)", self._process.pid, max_queue)

    @property
    def enabled(self) -> bool:
        return bool(self._enabled and self._process and self._process.is_alive())

    def submit(self, sql: str, params=None) -> bool:
        if not self.enabled or self._queue is None:
            return False
        try:
            if self._flush_event is not None:
                self._flush_event.clear()
            self._queue.put_nowait({"sql": str(sql or ""), "params": list(params or ())})
            return True
        except queue.Full:
            log.warning("PersistenceWriter queue full; falling back inline")
            return False
        except Exception:
            log.exception("PersistenceWriter enqueue failed")
            return False

    def flush(self, timeout: float = 5.0):
        if not self.enabled or self._queue is None or self._flush_event is None:
            return
        if self._queue.empty():
            return
        self._flush_event.clear()
        deadline = time.time() + max(0.5, float(timeout or 5.0))
        while time.time() < deadline:
            if self._queue.empty() and self._flush_event.wait(timeout=0.2):
                return

    def shutdown(self, timeout: float = 5.0):
        process = self._process
        if not process:
            return
        try:
            self.flush(timeout=max(1.0, float(timeout or 5.0) * 0.6))
        except Exception:
            log.debug("PersistenceWriter flush on shutdown failed", exc_info=True)
        try:
            if self._stop_event is not None:
                self._stop_event.set()
            if self._queue is not None:
                self._queue.put_nowait(None)
        except Exception:
            pass
        process.join(timeout=max(1.0, float(timeout or 5.0)))
        if process.is_alive():
            process.terminate()
            process.join(timeout=1.0)
        self._enabled = False
        self._process = None
        self._queue = None
        self._stop_event = None
        self._flush_event = None
