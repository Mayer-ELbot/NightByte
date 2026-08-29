"""
SteamDown Ultra AI - Audio Alerts & Sound Effects
Native Windows audio synthesizer for countdown, warnings, and notifications.
"""

import sys
import threading
import time

try:
    import winsound
except ImportError:
    winsound = None


class SoundManager:
    """Provides non-blocking audio alerts for key application events."""

    @staticmethod
    def play_async(target_func, *args):
        """Run sound playback in a daemon thread."""
        thread = threading.Thread(target=target_func, args=args, daemon=True)
        thread.start()

    @classmethod
    def alert_countdown_tick(cls):
        """Soft tick sound during final countdown seconds."""
        if not winsound:
            return
        def _play():
            try:
                winsound.Beep(880, 70)  # A5 note, short crisp tick
            except Exception:
                pass
        cls.play_async(_play)

    @classmethod
    def alert_warning(cls):
        """Urgent warning chime when shutdown countdown starts."""
        if not winsound:
            return
        def _play():
            try:
                # Double beep rising pitch
                winsound.Beep(700, 150)
                time.sleep(0.05)
                winsound.Beep(1000, 250)
            except Exception:
                pass
        cls.play_async(_play)

    @classmethod
    def alert_network_lost(cls):
        """Distinct warning tone when internet drops."""
        if not winsound:
            return
        def _play():
            try:
                # Descending tone
                winsound.Beep(800, 200)
                time.sleep(0.08)
                winsound.Beep(500, 300)
            except Exception:
                pass
        cls.play_async(_play)

    @classmethod
    def alert_network_restored(cls):
        """Pleasant chime when internet connection resumes."""
        if not winsound:
            return
        def _play():
            try:
                # Ascending tone
                winsound.Beep(523, 120)  # C5
                winsound.Beep(659, 120)  # E5
                winsound.Beep(784, 200)  # G5
            except Exception:
                pass
        cls.play_async(_play)

    @classmethod
    def alert_completed(cls):
        """Success chime when all downloads complete."""
        if not winsound:
            return
        def _play():
            try:
                winsound.Beep(600, 150)
                time.sleep(0.05)
                winsound.Beep(900, 350)
            except Exception:
                pass
        cls.play_async(_play)
