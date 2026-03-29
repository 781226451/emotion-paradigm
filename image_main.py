"""
Emotion Image Paradigm
======================
每个 block 包含 3 个 trial，顺序固定：
  Trial 1: 随机显示 assets/images/positive/ 中的一张图片
  Trial 2: 随机显示 assets/images/negative/ 中的一张图片
  Trial 3: 随机显示 assets/images/neutral/  中的一张图片

每个 trial 的流程：
  提示 → 注视点 → 图片展示（固定时长）→ 情绪评分（按键 1~9）→ ITI

Run:
    python image_main.py
"""

import os
import sys
import glob
import random
import csv
from datetime import datetime

from psychopy import visual, core, event, gui, logging
from pylsl import StreamInfo, StreamOutlet, cf_int8

import image_config as config


# ── Event Logger ────────────────────────────────────────────────────────────

class EventLogger:
    """CSV event logger: event_type, timestamp_ms, content."""

    FIELDNAMES = ["event_type", "timestamp_ms", "content"]

    def __init__(self, filepath: str):
        self._filepath = filepath
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=self.FIELDNAMES).writeheader()

    def log(self, event_type: str, content: str = ""):
        ts_ms = int(datetime.now().timestamp() * 1000)
        with open(self._filepath, "a", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=self.FIELDNAMES).writerow(
                {"event_type": event_type, "timestamp_ms": ts_ms, "content": content}
            )


# 评分按键 → LSL marker 值
_RATING_MARKER = {
    "1": config.LSL_MARKER_RATING_1,
    "2": config.LSL_MARKER_RATING_2,
    "3": config.LSL_MARKER_RATING_3,
    "4": config.LSL_MARKER_RATING_4,
    "5": config.LSL_MARKER_RATING_5,
    "6": config.LSL_MARKER_RATING_6,
    "7": config.LSL_MARKER_RATING_7,
    "8": config.LSL_MARKER_RATING_8,
    "9": config.LSL_MARKER_RATING_9,
}


# ── Helpers ────────────────────────────────────────────────────────────────

def get_participant_info() -> dict:
    """Show a dialog to collect participant info."""
    dlg_fields = {
        "participant_id": "",
        "num_blocks": "1",
    }
    dlg = gui.DlgFromDict(
        dictionary=dlg_fields,
        title="Participant Info",
        order=["participant_id", "num_blocks"],
    )
    if not dlg.OK:
        core.quit()
    dlg_fields["date"] = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return dlg_fields


def pick_random_image(folder: str) -> str:
    """Pick one random image file from a folder."""
    extensions = ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tif", "*.tiff")
    images = []
    for ext in extensions:
        images.extend(glob.glob(os.path.join(folder, ext)))
        images.extend(glob.glob(os.path.join(folder, ext.upper())))
    # deduplicate (case-insensitive filesystems may double-count)
    images = list(dict.fromkeys(images))
    if not images:
        raise FileNotFoundError(
            f"No image files found in '{folder}'.\n"
            "Place .jpg/.jpeg/.png/.bmp/.tif files there before running."
        )
    return random.choice(images)


def build_block_trials() -> list[dict]:
    """
    Build a 3-trial list for one block:
      Trial 1: random positive image
      Trial 2: random negative image
      Trial 3: random neutral image
    """
    dir_map = {
        "positive": config.POSITIVE_IMAGE_DIR,
        "negative": config.NEGATIVE_IMAGE_DIR,
        "neutral":  config.NEUTRAL_IMAGE_DIR,
    }
    trials = []
    for condition in config.TRIAL_ORDER:
        folder = dir_map[condition]
        filepath = pick_random_image(folder)
        trials.append({
            "condition":  condition,
            "image_file": filepath,
            "image_name": os.path.basename(filepath),
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
    event.clearEvents()
    event.waitKeys(keyList=list(wait_keys))



def show_image(win: visual.Window, filepath: str) -> float:
    """
    Display an image for IMAGE_DISPLAY_DURATION seconds.
    Supports early abort with Escape.
    Returns the actual display duration (s).
    """
    img = visual.ImageStim(win, image=filepath, units="pix", size=config.EXPECTED_IMAGE_SIZE)
    onset = core.getTime()
    deadline = onset + config.IMAGE_DISPLAY_DURATION

    while core.getTime() < deadline:
        if event.getKeys(["escape"]):
            win.close()
            core.quit()
        img.draw()
        win.flip()

    duration = core.getTime() - onset
    return duration


def collect_rating(
    win: visual.Window,
    msg_stim: visual.TextStim,
    timeout: float | None = None,
) -> tuple[str | None, float]:
    """
    Show rating prompt and wait for key 1~9.
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


# ── Main ───────────────────────────────────────────────────────────────────

def run_block(
    win: visual.Window,
    trials: list[dict],
    participant_info: dict,
    marker_outlet: StreamOutlet,
    logger: EventLogger,
):
    """Run one block (3 trials)."""

    block_num = participant_info["block"]
    marker_outlet.push_sample([config.LSL_MARKER_BLOCK_ON])
    logger.log("BLOCK_START", f"block={block_num}")

    msg = visual.TextStim(
        win, text="", color="white", height=config.TEXT_HEIGHT,
        font=config.FONT_NAME, fontFiles=[config.FONT_PATH],
        wrapWidth=1.6, pos=(0, 0),
    )

    for trial_idx, trial in enumerate(trials):

        logger.log("TRIAL_START", f"block={block_num} trial={trial_idx + 1} condition={trial['condition']}")

        # ── Pre-image prompt (auto-advance after 3 s) ─────────────────────
        msg.text = config.PRE_IMAGE_TEXT
        msg.draw()
        win.flip()
        logger.log("PRE_IMAGE_SHOWN", f"block={block_num} trial={trial_idx + 1}")
        core.wait(3.0)

        # ── Image ─────────────────────────────────────────────────────────
        marker_outlet.push_sample([config.LSL_MARKER_TRIAL_ON])
        logger.log("IMAGE_ONSET", f"block={block_num} trial={trial_idx + 1} type={trial['condition']} image={trial['image_name']}")
        print(f"image to show: {trial['image_file']}")
        image_duration = show_image(win, trial["image_file"])
        logger.log("IMAGE_OFFSET", f"block={block_num} trial={trial_idx + 1} duration={round(image_duration, 4)}s")

        # ── Rating (1~9) ──────────────────────────────────────────────────
        event.clearEvents()
        logger.log("RATING_SHOWN", f"block={block_num} trial={trial_idx + 1}")
        rating, rt = collect_rating(win, msg, timeout=config.RATING_TIMEOUT)
        rating_marker = _RATING_MARKER.get(rating)
        if rating_marker is not None:
            marker_outlet.push_sample([rating_marker])
        logger.log("RATING_RESPONSE", f"block={block_num} trial={trial_idx + 1} score={rating} marker={rating_marker} rt={round(rt, 4) if rt is not None else None}s")

        # ── ITI ───────────────────────────────────────────────────────────
        win.flip()
        logger.log("ITI_START", f"block={block_num} trial={trial_idx + 1} duration={config.ITI_DURATION}s")
        core.wait(config.ITI_DURATION)

    logger.log("BLOCK_END", f"block={block_num}")


def main():
    # ── LSL outlet（在输入框之前创建，确保不错过任何早期事件）──────────
    marker_info = StreamInfo(
        name=config.LSL_STREAM_NAME,
        type=config.LSL_STREAM_TYPE,
        channel_count=1,
        nominal_srate=0.0,
        channel_format=cf_int8,
        source_id=config.LSL_SOURCE_ID,
    )
    marker_outlet = StreamOutlet(marker_info)

    # ── Participant info ────────────────────────────────────────────────
    participant_info = get_participant_info()

    # ── Event logger ─────────────────────────────────────────────────────
    log_filename = os.path.join(
        config.DATA_DIR,
        f"log_sub-{participant_info['participant_id']}"
        f"_{participant_info['date']}.csv",
    )
    logger = EventLogger(log_filename)
    logger.log("EXPERIMENT_START", f"participant={participant_info['participant_id']} num_blocks={participant_info['num_blocks']}")

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

    # ── Instructions ────────────────────────────────────────────────────
    msg = visual.TextStim(
        win, text="", color="white", height=config.TEXT_HEIGHT,
        font=config.FONT_NAME, fontFiles=[config.FONT_PATH], wrapWidth=1.6,
    )
    logger.log("INSTRUCTION_SHOWN", "")
    show_text_and_wait(win, msg, config.INSTRUCTION_TEXT)
    logger.log("INSTRUCTION_ACKNOWLEDGED", "")

    # ── Blocks loop ──────────────────────────────────────────────────────
    num_blocks = int(participant_info["num_blocks"])
    for blk_offset in range(num_blocks):
        block_info = dict(participant_info)
        block_info["block"] = str(blk_offset + 1)
        try:
            trials = build_block_trials()
        except FileNotFoundError as e:
            win.close()
            print(f"\nERROR: {e}")
            sys.exit(1)
        run_block(win, trials, block_info, marker_outlet, logger)

        # ── Inter-block interval ──────────────────────────────────────────
        if blk_offset < num_blocks - 1:
            msg.text = config.IBI_TEXT
            msg.draw()
            win.flip()
            logger.log("IBI_START", f"after_block={blk_offset + 1} duration={config.IBI_DURATION}s")
            core.wait(config.IBI_DURATION)

    # ── End ──────────────────────────────────────────────────────────────
    logger.log("EXPERIMENT_END", f"participant={participant_info['participant_id']}")
    show_text_and_wait(win, msg, config.END_TEXT)
    win.close()
    core.quit()


if __name__ == "__main__":
    main()
