# Image Paradigm Configuration
import os

# ── Window ─────────────────────────────────────────────────────────────────
SCREEN_SIZE      = (3840, 2160)
FULL_SCREEN      = True
BACKGROUND_COLOR = (0, 0, 0)     # gray, PsychoPy [-1, 1] range

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR           = os.path.dirname(os.path.abspath(__file__))
ASSETS_IMAGE_DIR   = os.path.join(BASE_DIR, "assets", "images")
POSITIVE_IMAGE_DIR = os.path.join(ASSETS_IMAGE_DIR, "positive")
NEGATIVE_IMAGE_DIR = os.path.join(ASSETS_IMAGE_DIR, "negative")
NEUTRAL_IMAGE_DIR  = os.path.join(ASSETS_IMAGE_DIR, "neutral")
DATA_DIR           = os.path.join(BASE_DIR, "data")
FONT_NAME          = "Noto Sans SC"
FONT_PATH          = os.path.join(BASE_DIR, "assets", "fonts", "NotoSansSC-Regular.ttf")

# ── Block structure ────────────────────────────────────────────────────────
# Each block has exactly 3 trials in this fixed order:
#   Trial 1: random image from positive/
#   Trial 2: random image from negative/
#   Trial 3: random image from neutral/
TRIAL_ORDER = ["positive", "negative", "neutral"]

# ── Trial timing (seconds) ─────────────────────────────────────────────────
IMAGE_DISPLAY_DURATION = 3.0   # how long each image stays on screen
ITI_DURATION           = 1.5   # inter-trial interval after rating
IBI_DURATION           = 3.0   # inter-block interval (blank screen)
RATING_TIMEOUT         = None  # max wait for rating (None = unlimited)
RESPONSE_KEYS          = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

# ── Text ───────────────────────────────────────────────────────────────────
INSTRUCTION_TEXT = """\
欢迎参加本实验。

您将依次观看一系列图片，请专注地观看每张图片。

图片消失后，请对您的情绪体验进行评分：
  按键盘上的  1 ~ 9（1 = 最积极，5 = 中性，9 = 最消极）

按 空格键 开始实验。
"""

PRE_IMAGE_TEXT = """\
请准备好观看图片
"""

RATING_TEXT = """\
请对您刚才的情绪体验进行评分：

  1 = 最积极   5 = 中性    9 = 最消极
    
请按键盘上的 1 ~ 9。
"""

END_TEXT = """\
实验结束，感谢您的参与！

按 空格键 退出。
"""

# ── LSL ────────────────────────────────────────────────────────────────────
LSL_STREAM_NAME = "ImageEmotionParadigm"
LSL_STREAM_TYPE = "Markers"
LSL_SOURCE_ID   = "image_emotion_paradigm_marker"

# LSL marker 常量
LSL_MARKER_IMAGE_POSITIVE = 1   # 正性图片出现
LSL_MARKER_IMAGE_NEGATIVE = 2   # 负性图片出现
LSL_MARKER_IMAGE_NEUTRAL  = 3   # 中性图片出现
LSL_MARKER_IMAGE_OFFSET   = 9   # 图片消失
LSL_MARKER_RATING_1       = 11  # 按键 1（最积极）
LSL_MARKER_RATING_2       = 12  # 按键 2
LSL_MARKER_RATING_3       = 13  # 按键 3
LSL_MARKER_RATING_4       = 14  # 按键 4
LSL_MARKER_RATING_5       = 15  # 按键 5（中性）
LSL_MARKER_RATING_6       = 16  # 按键 6
LSL_MARKER_RATING_7       = 17  # 按键 7
LSL_MARKER_RATING_8       = 18  # 按键 8
LSL_MARKER_RATING_9       = 19  # 按键 9（最消极）
