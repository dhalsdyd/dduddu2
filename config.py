# config.py
BASE_W, BASE_H = 1000, 700   # 논리 캔버스 기준
MIN_W, MIN_H   = 800,  560   # 너무 작게 줄였을 때 하한(선택)

# 파일 경로 (사용자 데이터 디렉토리 사용)
from core.settings import get_user_data_dir
_user_data_dir = get_user_data_dir()
DATA_FILE = str(_user_data_dir / "leaderboard.json")
SESSION_FILE = str(_user_data_dir / "session.json")

# 컬러 팔레트
BG   = (16, 18, 24)
CARD = (28, 32, 40)
TEXT = (235, 238, 243)
SUBT = (170, 178, 189)
ACC  = (90, 190, 255)
LINE = (60, 66, 80)
OK   = (100, 220, 160)
WARN = (240, 120, 120)

# 폰트 크기
H1 = 68
H2 = 44
H3 = 36
TXT = 30

# --- Serial / 초음파 ---
SERIAL_DEFAULT_PORT = None      # None이면 자동탐색 시도 (예: "/dev/tty.usbmodem1101")
SERIAL_BAUD = 9600              # 테스트 코드와 일치하도록 9600으로 변경
NEAR_THRESHOLD_CM = 5
NEAR_COOLDOWN_S = 0.6

ARM_ZONE_CM = 28.0     # SPEED 모드: 이 거리 이하로 들어오면 무장(스타트)
ATTEMPT_GAP_S = 0.7    # 시도 종료 간격(센서 업데이트 끊긴 시간)

