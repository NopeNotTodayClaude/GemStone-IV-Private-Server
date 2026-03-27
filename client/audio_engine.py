import ctypes
import json
import os
import time
from typing import Callable, Optional


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


class _MciError(RuntimeError):
    pass


class _MciPlayer:
    def __init__(self, alias: str):
        self.alias = alias
        self.path: str = ""
        self.duration_ms: int = 0
        self._open = False
        self._winmm = ctypes.windll.winmm

    def _send(self, command: str) -> str:
        buf = ctypes.create_unicode_buffer(512)
        err = self._winmm.mciSendStringW(command, buf, len(buf), 0)
        if err != 0:
            ebuf = ctypes.create_unicode_buffer(512)
            self._winmm.mciGetErrorStringW(err, ebuf, len(ebuf))
            raise _MciError(ebuf.value or f"MCI error {err}")
        return buf.value

    def _quoted(self, path: str) -> str:
        return path.replace('"', '""')

    def open(self, path: str):
        self.close()
        ext = os.path.splitext(path)[1].lower()
        media_type = ""
        if ext in {".mp3", ".mpeg", ".mpg"}:
            media_type = " type mpegvideo"
        elif ext in {".wav"}:
            media_type = " type waveaudio"
        self._send(f'open "{self._quoted(path)}"{media_type} alias {self.alias}')
        self._send(f"set {self.alias} time format milliseconds")
        self.duration_ms = int(self._send(f"status {self.alias} length") or "0")
        self.path = path
        self._open = True

    def play(self, from_ms: int = 0):
        if not self._open:
            return
        self._send(f"play {self.alias} from {max(0, int(from_ms))}")

    def stop(self):
        if not self._open:
            return
        try:
            self._send(f"stop {self.alias}")
        except _MciError:
            pass

    def close(self):
        if not self._open:
            return
        try:
            self._send(f"close {self.alias}")
        except _MciError:
            pass
        self.path = ""
        self.duration_ms = 0
        self._open = False

    def set_volume(self, percent: float):
        if not self._open:
            return
        value = int(_clamp(percent, 0.0, 100.0) * 10)
        try:
            self._send(f"setaudio {self.alias} volume to {value}")
        except _MciError:
            pass

    def position_ms(self) -> int:
        if not self._open:
            return 0
        try:
            return int(self._send(f"status {self.alias} position") or "0")
        except _MciError:
            return 0


class AudioManager:
    def __init__(
        self,
        media_root: str,
        rules_path: str,
        log_cb: Optional[Callable[[str], None]] = None,
    ):
        self.media_root = media_root
        self.rules_path = rules_path
        self.log_cb = log_cb

        self.music_enabled = True
        self.sfx_enabled = True
        self.music_volume = 65
        self.sfx_volume = 75

        self._rules = self._load_rules()
        self._players = {
            "a": _MciPlayer("gsiv_music_a"),
            "b": _MciPlayer("gsiv_music_b"),
        }
        self._active_slot: Optional[str] = None
        self._pending_slot: Optional[str] = None
        self._active_track: Optional[dict] = None
        self._target_track: Optional[dict] = None
        self._fade: Optional[dict] = None
        self._current_zone: str = ""
        self._warned_missing: set[str] = set()
        self._loop_armed = False
        self._sfx_seq = 0
        self._active_sfx: list[dict] = []

    def _log(self, message: str):
        if self.log_cb:
            try:
                self.log_cb(message)
            except Exception:
                pass

    def _load_rules(self) -> dict:
        if not os.path.exists(self.rules_path):
            return {"music": {"zones": {}}}
        try:
            with open(self.rules_path, "r", encoding="utf-8-sig") as f:
                return json.load(f)
        except Exception:
            return {"music": {"zones": {}}}

    def reload_rules(self):
        self._rules = self._load_rules()
        self.on_zone_changed(self._current_zone, force=True)

    def shutdown(self):
        self._fade = None
        self._active_slot = None
        self._pending_slot = None
        self._active_track = None
        self._target_track = None
        self._loop_armed = False
        for player in self._players.values():
            player.close()
        for entry in self._active_sfx:
            try:
                entry["player"].close()
            except Exception:
                pass
        self._active_sfx.clear()

    def apply_settings(
        self,
        *,
        music_enabled: bool,
        music_volume: int,
        sfx_enabled: bool,
        sfx_volume: int,
    ):
        self.music_enabled = bool(music_enabled)
        self.sfx_enabled = bool(sfx_enabled)
        self.music_volume = int(_clamp(int(music_volume), 0, 100))
        self.sfx_volume = int(_clamp(int(sfx_volume), 0, 100))
        if not self.music_enabled or self.music_volume <= 0:
            self._begin_stop_fade(900)
            return
        if self._active_slot and not self._fade:
            self._players[self._active_slot].set_volume(self.music_volume)

    def on_zone_changed(self, zone_name: str, force: bool = False):
        zone_name = str(zone_name or "")
        if not force and zone_name == self._current_zone:
            return
        self._current_zone = zone_name
        zones = self._rules.get("music", {}).get("zones", {})
        track = zones.get(zone_name)
        self._target_track = track if isinstance(track, dict) else None
        self._switch_music()

    def tick(self):
        self._tick_fade()
        self._tick_loop()
        self._tick_sfx()

    def play_sfx(
        self,
        file_name: str,
        *,
        stop_after_ms: Optional[int] = None,
        stop_fraction: Optional[float] = None,
    ):
        if not self.sfx_enabled or self.sfx_volume <= 0:
            return
        file_name = str(file_name or "").strip()
        if not file_name:
            return
        path = file_name if os.path.isabs(file_name) else os.path.join(self.media_root, "sfx", file_name)
        if not os.path.exists(path):
            if path not in self._warned_missing:
                self._warned_missing.add(path)
                self._log(f"[Audio] Missing sfx file: {path}")
            return
        self._sfx_seq += 1
        alias = f"gsiv_sfx_{self._sfx_seq}"
        player = _MciPlayer(alias)
        try:
            player.open(path)
            player.set_volume(self.sfx_volume)
            player.play(0)
            duration_ms = max(0, int(player.duration_ms or 0))
            limit_ms = duration_ms + 250 if duration_ms > 0 else 5000
            if stop_fraction is not None and duration_ms > 0:
                fraction = _clamp(float(stop_fraction), 0.0, 1.0)
                limit_ms = max(1, int(duration_ms * fraction))
            if stop_after_ms is not None:
                limit_ms = max(1, min(limit_ms, int(stop_after_ms)))
            self._active_sfx.append(
                {
                    "player": player,
                    "stop_at": time.monotonic() + (limit_ms / 1000.0),
                }
            )
        except Exception as e:
            self._log(f"[Audio] Could not play sfx '{os.path.basename(path)}': {e}")
            player.close()

    def _resolve_track_path(self, track: Optional[dict]) -> Optional[str]:
        if not track:
            return None
        rel = str(track.get("file") or "").strip()
        if not rel:
            return None
        path = rel if os.path.isabs(rel) else os.path.join(self.media_root, "music", rel)
        if os.path.exists(path):
            return path
        if path not in self._warned_missing:
            self._warned_missing.add(path)
            self._log(f"[Audio] Missing music file: {path}")
        return None

    def _other_slot(self, slot: Optional[str]) -> str:
        return "b" if slot == "a" else "a"

    def _track_key(self, track: Optional[dict]) -> str:
        return self._resolve_track_path(track) or ""

    def _switch_music(self):
        if not self.music_enabled or self.music_volume <= 0:
            self._begin_stop_fade(900)
            return

        desired_path = self._resolve_track_path(self._target_track)
        active_path = self._players[self._active_slot].path if self._active_slot else ""

        if not desired_path:
            self._begin_stop_fade(1200)
            return

        if self._active_slot and active_path == desired_path and not self._pending_slot:
            self._players[self._active_slot].set_volume(self.music_volume)
            return

        if not self._active_slot:
            slot = "a"
            if self._open_and_play(slot, desired_path, 0):
                self._active_slot = slot
                self._active_track = dict(self._target_track or {})
                self._start_fade(None, slot, self._fade_in_ms(self._target_track))
            return

        new_slot = self._other_slot(self._active_slot)
        self._players[new_slot].close()
        if self._open_and_play(new_slot, desired_path, 0):
            self._pending_slot = new_slot
            self._start_fade(self._active_slot, new_slot, self._crossfade_ms(self._active_track, self._target_track))

    def _open_and_play(self, slot: str, path: str, start_volume: int) -> bool:
        try:
            player = self._players[slot]
            player.open(path)
            player.set_volume(start_volume)
            player.play(0)
            return True
        except Exception as e:
            self._log(f"[Audio] Could not play '{os.path.basename(path)}': {e}")
            self._players[slot].close()
            return False

    def _start_fade(self, from_slot: Optional[str], to_slot: Optional[str], duration_ms: int):
        self._loop_armed = False
        self._fade = {
            "from": from_slot,
            "to": to_slot,
            "start": time.monotonic(),
            "duration": max(1, int(duration_ms)),
        }

    def _tick_fade(self):
        if not self._fade:
            return
        started = self._fade["start"]
        duration = self._fade["duration"] / 1000.0
        progress = _clamp((time.monotonic() - started) / duration, 0.0, 1.0)

        from_slot = self._fade.get("from")
        to_slot = self._fade.get("to")

        if from_slot:
            self._players[from_slot].set_volume((1.0 - progress) * self.music_volume)
        if to_slot:
            self._players[to_slot].set_volume(progress * self.music_volume)

        if progress < 1.0:
            return

        if from_slot:
            self._players[from_slot].close()
        self._active_slot = to_slot
        self._pending_slot = None
        if self._active_slot and self._target_track:
            self._active_track = dict(self._target_track)
            self._players[self._active_slot].set_volume(self.music_volume)
        else:
            self._active_track = None
        self._fade = None
        self._loop_armed = False

    def _tick_loop(self):
        if self._fade or not self._active_slot or not self.music_enabled or self.music_volume <= 0:
            return
        if not self._active_track:
            return
        loop_ms = int(self._active_track.get("loop_crossfade_ms", 0) or 0)
        if loop_ms <= 0:
            return
        active = self._players[self._active_slot]
        if active.duration_ms <= 0:
            return
        pos = active.position_ms()
        if pos < max(0, active.duration_ms - loop_ms):
            self._loop_armed = False
            return
        if self._loop_armed:
            return
        next_slot = self._other_slot(self._active_slot)
        path = active.path
        self._players[next_slot].close()
        if self._open_and_play(next_slot, path, 0):
            self._pending_slot = next_slot
            self._start_fade(self._active_slot, next_slot, loop_ms)
            self._loop_armed = True

    def _begin_stop_fade(self, duration_ms: int):
        if not self._active_slot:
            self.shutdown()
            return
        self._target_track = None
        self._start_fade(self._active_slot, None, duration_ms)

    def _tick_sfx(self):
        if not self._active_sfx:
            return
        now = time.monotonic()
        keep: list[dict] = []
        for entry in self._active_sfx:
            player = entry.get("player")
            stop_at = float(entry.get("stop_at", 0))
            if now < stop_at:
                keep.append(entry)
                continue
            try:
                player.stop()
            except Exception:
                pass
            try:
                player.close()
            except Exception:
                pass
        self._active_sfx = keep

    def _fade_in_ms(self, track: Optional[dict]) -> int:
        if not track:
            return 2200
        return int(track.get("fade_in_ms", 2200) or 2200)

    def _fade_out_ms(self, track: Optional[dict]) -> int:
        if not track:
            return 2200
        return int(track.get("fade_out_ms", 2200) or 2200)

    def _crossfade_ms(self, current_track: Optional[dict], next_track: Optional[dict]) -> int:
        return max(self._fade_out_ms(current_track), self._fade_in_ms(next_track))
