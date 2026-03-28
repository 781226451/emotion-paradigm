"""
Emotion Video Paradigm
======================
每个 session 包含 3 个 trial，顺序固定：
  Trial 1: 随机播放 assets/videos/positive/ 中的一个视频
  Trial 2: 随机播放 assets/videos/negative/ 中的一个视频
  Trial 3: 随机播放 assets/videos/neutral/  中的一个视频

每个 trial 的流程：
  播放前提示 → 注视点 → 视频播放 → 评分（按键 1/2/3）→ ITI

Run:
    python main.py
"""

import os
import sys
import glob
import random
import csv
from datetime import datetime

from psychopy import visual, core, event, gui, logging

import config


# ── Helpers ────────────────────────────────────────────────────────────────

def get_participant_info() -> dict:
    """Show a dialog to collect participant info."""
    dlg_fields = {
        "participant_id": "",
        "session": "1",
    }
    dlg = gui.DlgFromDict(
        dictionary=dlg_fields,
        title="Participant Info",
        order=["participant_id", "session"],
    )
    if not dlg.OK:
        core.quit()
    dlg_fields["date"] = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return dlg_fields


def pick_random_video(folder: str) -> str:
    """Pick one random video file from a folder."""
    extensions = ("*.mp4", "*.avi", "*.mov", "*.mkv")
    videos = []
    for ext in extensions:
        videos.extend(glob.glob(os.path.join(folder, ext)))
    if not videos:
        raise FileNotFoundError(
            f"No video files found in '{folder}'.\n"
            "Place .mp4/.avi/.mov/.mkv files there before running."
        )
    return random.choice(videos)


def build_session_trials() -> list[dict]:
    """
    Build a 3-trial list for one session:
      Trial 1: random positive video
      Trial 2: random negative video
      Trial 3: random neutral video
    """
    dir_map = {
        "positive": config.POSITIVE_VIDEO_DIR,
        "negative": config.NEGATIVE_VIDEO_DIR,
        "neutral":  config.NEUTRAL_VIDEO_DIR,
    }
    trials = []
    for condition in config.TRIAL_ORDER:
        folder = dir_map[condition]
        filepath = pick_random_video(folder)
        trials.append({
            "condition": condition,
            "video_file": filepath,
            "video_name": os.path.basename(filepath),
        })
    return trials


def show_text_and_wait(
    win: visual.Window,
    text_stim: visual.TextStim,
    text: str,
    wait_keys: list[str] = ("space",),
):
    """Display text and wait for a keypress."""
    text_stim.text = text
    text_stim.draw()
    win.flip()
    event.waitKeys(keyList=list(wait_keys))


def play_video(win: visual.Window, filepath: str) -> float:
    """
    Play a video and return the actual duration (s).
    Supports early abort with Escape.
    autoStart=True (default) starts playback on the first draw().
    """
    mov = visual.MovieStim(win, filename=filepath, loop=False, noAudio=False,
                           autoStart=True)
    onset = core.getTime()

    while not mov.isFinished:
        if event.getKeys(["escape"]):
            mov.stop()
            win.close()
            core.quit()
        mov.draw()
        win.flip()

    duration = core.getTime() - onset
    return duration


def collect_rating(
    win: visual.Window,
    msg_stim: visual.TextStim,
    timeout: float | None = None,
) -> tuple[str | None, float]:
    """
    Show rating prompt and wait for key 1, 2, or 3.
    Returns (key_pressed, response_time_s).
    """
    msg_stim.text = config.RATING_TEXT
    timer = core.Clock()

    while True:
        if event.getKeys(["escape"]):
            win.close()
            core.quit()

        msg_stim.draw()
        win.flip()

        keys = event.getKeys(keyList=config.RESPONSE_KEYS + ["escape"],
                             timeStamped=timer)
        for key, t in keys:
            if key == "escape":
                win.close()
                core.quit()
            if key in config.RESPONSE_KEYS:
                return key, t

        if timeout is not None and timer.getTime() > timeout:
            return None, timer.getTime()


def save_data(rows: list[dict], participant_info: dict):
    """Append trial rows to a CSV file in the data directory."""
    os.makedirs(config.DATA_DIR, exist_ok=True)
    filename = os.path.join(
        config.DATA_DIR,
        f"sub-{participant_info['participant_id']}"
        f"_ses-{participant_info['session']}"
        f"_{participant_info['date']}.csv",
    )
    if not rows:
        return filename

    fieldnames = list(rows[0].keys())
    write_header = not os.path.exists(filename)
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)
    return filename


# ── Main ───────────────────────────────────────────────────────────────────

def run_session(
    win: visual.Window,
    trials: list[dict],
    participant_info: dict,
) -> list[dict]:
    """Run one session (3 trials) and return collected data rows."""

    msg = visual.TextStim(
        win, text="", color="white", height=0.07,
        font=config.FONT_NAME,fontFiles=[config.FONT_PATH] ,wrapWidth=1.6, pos=(0, 0),
    )
    fixation = visual.TextStim(
        win, text="+", color="white", height=0.12, font=config.FONT_NAME,fontFiles=[config.FONT_PATH],
    )

    rows = []

    for trial_idx, trial in enumerate(trials):

        # ── Pre-video prompt ─────────────────────────────────────────────
        show_text_and_wait(win, msg, config.PRE_VIDEO_TEXT)

        # ── Video ────────────────────────────────────────────────────────
        video_onset = core.getTime()
        video_duration = play_video(win, trial["video_file"])

        # ── Rating (1/2/3) ───────────────────────────────────────────────
        rating, rt = collect_rating(win, msg, timeout=config.RATING_TIMEOUT)

        # ── ITI ──────────────────────────────────────────────────────────
        win.flip()
        core.wait(config.ITI_DURATION)

        # ── Record ───────────────────────────────────────────────────────
        row = {
            "participant_id": participant_info["participant_id"],
            "session": participant_info["session"],
            "trial_index": trial_idx + 1,
            "condition": trial["condition"],
            "video_name": trial["video_name"],
            "video_onset": round(video_onset, 4),
            "video_duration": round(video_duration, 4),
            "rating": rating,
            "rating_rt": round(rt, 4) if rt is not None else None,
        }
        rows.append(row)

        # Stream to disk after each trial (crash-safe)
        save_data([row], participant_info)

    return rows


def main():
    # ── Participant info ────────────────────────────────────────────────
    participant_info = get_participant_info()

    # ── Window ──────────────────────────────────────────────────────────
    win = visual.Window(
        size=config.SCREEN_SIZE,
        fullscr=config.FULL_SCREEN,
        color=config.BACKGROUND_COLOR,
        units="norm",
        allowGUI=False,
        winType="pyglet",
    )
    win.mouseVisible = False
    logging.console.setLevel(logging.WARNING)

    # ── Build trial list ─────────────────────────────────────────────────
    try:
        trials = build_session_trials()
    except FileNotFoundError as e:
        win.close()
        print(f"\nERROR: {e}")
        sys.exit(1)

    # ── Instructions ────────────────────────────────────────────────────
    msg = visual.TextStim(
        win, text="", color="white", height=0.06,
        font=config.FONT_NAME,fontFiles=[config.FONT_PATH], wrapWidth=1.6,
    )
    show_text_and_wait(win, msg, config.INSTRUCTION_TEXT)

    # ── Session ──────────────────────────────────────────────────────────
    run_session(win, trials, participant_info)

    # ── End ──────────────────────────────────────────────────────────────
    show_text_and_wait(win, msg, config.END_TEXT)
    win.close()
    core.quit()


if __name__ == "__main__":
    main()
