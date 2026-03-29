# Experiment configuration
import os

# ── Window ─────────────────────────────────────────────────────────────────
SCREEN_SIZE = (3840, 2160)   # pixels
FULL_SCREEN = True
BACKGROUND_COLOR = (-1, -1, -1)  # black, PsychoPy [-1, 1] range
FRAME_RATE = 60              # Hz

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
ASSETS_VIDEO_DIR = os.path.join(BASE_DIR, "assets", "videos")
POSITIVE_VIDEO_DIR = os.path.join(ASSETS_VIDEO_DIR, "positive")
NEGATIVE_VIDEO_DIR = os.path.join(ASSETS_VIDEO_DIR, "negative")
NEUTRAL_VIDEO_DIR  = os.path.join(ASSETS_VIDEO_DIR, "neutral")
DATA_DIR        = os.path.join(BASE_DIR, "data")
FONT_NAME = "Noto Sans SC"
FONT_PATH = os.path.join(BASE_DIR, "assets", "fonts","NotoSansSC-Regular.ttf")

# ── Session structure ──────────────────────────────────────────────────────
# Each session has exactly 3 trials in this fixed order:
#   Trial 1: random video from positive/
#   Trial 2: random video from negative/
#   Trial 3: random video from neutral/
TRIAL_ORDER = ["positive", "negative", "neutral"]

# ── Trial timing (seconds) ─────────────────────────────────────────────────
ITI_DURATION        = 1.5    # inter-trial interval after rating
RATING_TIMEOUT      = None   # max time for rating response (None = unlimited)
RESPONSE_KEYS       = ["1", "2", "3"]  # keyboard rating keys

# ── Instructions text ──────────────────────────────────────────────────────
INSTRUCTION_TEXT = """\
欢迎参加本实验。

您将观看三段视频片段，请专心观看每个视频。

视频结束后，请对您的情绪体验进行评分：
  按键盘上的  1、2 或 3

按 空格键 开始实验。
"""

PRE_VIDEO_TEXT = """\
请准备好观看视频。

按 空格键 开始播放。
"""

RATING_TEXT = """\
请对您刚才的情绪体验进行评分：

  1 = 消极
  2 = 中性
  3 = 积极

请按键盘上的 1、2 或 3。
"""

END_TEXT = """\
实验结束，感谢您的参与！

按 空格键 退出。
"""

# ── LSL ────────────────────────────────────────────────────────────────────
LSL_STREAM_NAME = "EmotionParadigm"
LSL_STREAM_TYPE = "Markers"
LSL_SOURCE_ID   = "emotion_paradigm_marker"

# LSL marker 常量
LSL_MARKER_VIDEO_POSITIVE = 1   # 正性视频开始
LSL_MARKER_VIDEO_NEGATIVE = 2   # 负性视频开始
LSL_MARKER_VIDEO_NEUTRAL  = 3   # 中性视频开始
LSL_MARKER_RATING_1       = 11  # 按键 1（消极）
LSL_MARKER_RATING_2       = 12  # 按键 2（中性）
LSL_MARKER_RATING_3       = 13  # 按键 3（积极）
