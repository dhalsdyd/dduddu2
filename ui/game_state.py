# ui/game_state.py
# 웹캠 + 아두이노(초음파) + 판정(SPEED/CLOSEST) GameState
import time
import os
from typing import Optional, List

import pygame
import cv2 as cv
import json
import config as cfg
from core.viewport import Viewport
from core.fonts import FontPack
from core.leaderboard import save_score
from core.path_utils import get_asset_path, safe_image_load
from core.settings import get_camera_index, get_serial_port

try:
    from serial import Serial
    from serial.tools import list_ports
    import glob
except Exception:
    Serial = None
    list_ports = None
    glob = None


class GameState:
    def __init__(self, cam_index: int = None, target_fps: int = 30, prefer_size=(1280, 720), player_name: str = ""):
        # 카메라 (저장된 인덱스 사용)
        if cam_index is None:
            cam_index = get_camera_index()
        self.cam_index = cam_index
        self.target_fps = target_fps
        self.prefer_size = prefer_size
        self.cap: Optional[cv.VideoCapture] = None
        self.frame = None
        self.mirror = True
        self.ok_cam = False
        self.err_cam = ""
        self.player_name = player_name

        # 직렬
        self.ser = None
        saved_port = get_serial_port()
        self.serial_port = saved_port if saved_port else cfg.SERIAL_DEFAULT_PORT  # 저장된 포트 사용
        self.serial_baud = cfg.SERIAL_BAUD
        self.ok_ser = False
        self.err_ser = ""
        self._rx_buf = ""

        # 센서/판정 상태
        self.latest_cm: Optional[float] = None
        self.near_count = 0
        self.last_near_ts: Optional[float] = None
        self.near_cooldown_s = cfg.NEAR_COOLDOWN_S

        # 모드 & 기록 (속도 모드로 고정)
        self.mode = "SPEED"                 # SPEED 모드로 고정
        self.best_fast_ms: Optional[int] = None
        self.best_close_cm: Optional[float] = None

        # 시도/무장 상태
        self.in_attempt = False
        self.armed = False
        self.t_arm: Optional[float] = None
        self.min_dist_cm = float("inf")
        self.last_update_ts: float = 0.0
        self.game_completed = False  # 게임 완료 상태 추가
        self.game_start_time: Optional[float] = None  # 게임 시작 시간 추가

        # 전환
        self.next: Optional[tuple[str, dict]] = None
        
        # 이미지 로딩
        self._load_images()

    def _load_images(self):
        """게임 화면용 이미지들을 로딩합니다."""
        base_path = get_asset_path("images", "game_state")
        
        try:
            # 배경 이미지
            self.bg_image = safe_image_load(os.path.join(base_path, "background.jpg"))
            
            # 타이틀 이미지
            self.title_image = safe_image_load(os.path.join(base_path, "way_to_ssulmo_center.png"))
            
            # 캐릭터 이미지들
            self.character_left = safe_image_load(os.path.join(base_path, "smile_book.png"))  # 왼쪽 캐릭터
            self.character_right = safe_image_load(os.path.join(base_path, "smile_dduddu.png"))  # 오른쪽 캐릭터
            self.character_top_right = safe_image_load(os.path.join(base_path, "ssulmon.png"))  # 오른쪽 상단 캐릭터
            
            # 기타 이미지들
            self.gwangmyeong_image = safe_image_load(os.path.join(base_path, "gwangmyeong_x_ssulmo_white.png"))
            
        except Exception as e:
            print(f"게임 이미지 로딩 실패: {e}")
            # 기본값으로 None 설정
            self.bg_image = None
            self.title_image = None
            self.character_left = None
            self.character_right = None
            self.character_top_right = None
            self.gwangmyeong_image = None

    # ---------- 라이프사이클 ----------
    def enter(self):
        self._open_camera()
        self._open_serial()
        
        # 게임 시작 시간 설정 (게임 진입 시점)
        self.game_start_time = time.time()
        print(f"[GAME] 게임 시작! 시작 시간: {time.strftime('%H:%M:%S')}")

    def exit(self):
        if self.cap:
            self.cap.release()
            self.cap = None
        if self.ser:
            try: self.ser.close()
            except Exception: pass
            self.ser = None

    # ---------- 내부 유틸 ----------
    def _open_camera(self):
        try:
            # Windows와 macOS/Linux에서 다른 백엔드 사용
            if os.name == 'nt':  # Windows
                backends = [cv.CAP_DSHOW, cv.CAP_MSMF, cv.CAP_ANY]
                print("Windows 환경에서 웹캠 연결 시도...")
                print("Windows 웹캠 문제 해결 방법:")
                print("1. 웹캠이 다른 프로그램에서 사용 중인지 확인")
                print("2. 웹캠 드라이버 업데이트")
                print("3. Windows 카메라 앱에서 웹캠 권한 확인")
            else:  # macOS/Linux
                backends = [cv.CAP_AVFOUNDATION, cv.CAP_V4L2, cv.CAP_ANY]
                print("macOS/Linux 환경에서 웹캠 연결 시도...")
            
            self.cap = None
            
            # 먼저 기본 인덱스로 시도
            for backend in backends:
                try:
                    print(f"백엔드 {backend}로 카메라 {self.cam_index} 연결 시도...")
                    self.cap = cv.VideoCapture(self.cam_index, backend)
                    if self.cap and self.cap.isOpened():
                        print(f"웹캠 연결 성공 (백엔드: {backend})")
                        break
                    else:
                        if self.cap:
                            self.cap.release()
                        self.cap = None
                except Exception as e:
                    print(f"백엔드 {backend} 실패: {e}")
                    continue
            
            # 기본 인덱스로 실패한 경우 다른 인덱스 시도
            if not self.cap or not self.cap.isOpened():
                print("기본 카메라 인덱스로 연결 실패, 다른 인덱스 시도...")
                
                # Windows에서는 더 많은 인덱스 시도
                if os.name == 'nt':
                    indices_to_try = [1, 2, 3, 0]  # Windows에서는 1,2,3번도 시도
                else:
                    indices_to_try = [1, 2, 0]
                
                for idx in indices_to_try:
                    if idx == self.cam_index:
                        continue
                    print(f"카메라 인덱스 {idx} 시도...")
                    
                    for backend in backends:
                        try:
                            self.cap = cv.VideoCapture(idx, backend)
                            if self.cap and self.cap.isOpened():
                                self.cam_index = idx
                                print(f"웹캠 연결 성공 (인덱스: {idx}, 백엔드: {backend})")
                                break
                            else:
                                if self.cap:
                                    self.cap.release()
                                self.cap = None
                        except Exception as e:
                            print(f"인덱스 {idx}, 백엔드 {backend} 실패: {e}")
                            continue
                    if self.cap and self.cap.isOpened():
                        break
                
                if not self.cap or not self.cap.isOpened():
                    self.ok_cam = False
                    error_msg = "웹캠을 찾을 수 없습니다."
                    
                    if os.name == 'nt':
                        error_msg += "\n\nWindows 웹캠 문제 해결 방법:"
                        error_msg += "\n1. 웹캠이 다른 프로그램에서 사용 중인지 확인"
                        error_msg += "\n2. 웹캠 드라이버 업데이트"
                        error_msg += "\n3. Windows 설정 > 개인정보 > 카메라 권한 확인"
                        error_msg += "\n4. 웹캠을 물리적으로 연결/재연결"
                        error_msg += "\n5. webcam_test.py 스크립트로 진단 실행"
                    else:
                        error_msg += "\n\nmacOS/Linux 웹캠 문제 해결 방법:"
                        error_msg += "\n1. 웹캠 권한 확인"
                        error_msg += "\n2. 다른 프로그램에서 웹캠 사용 중인지 확인"
                        error_msg += "\n3. webcam_test.py 스크립트로 진단 실행"
                    
                    self.err_cam = error_msg
                    print("모든 카메라 인덱스와 백엔드 시도 실패")
                    print("webcam_test.py 스크립트를 실행하여 웹캠 상태를 진단하세요.")
                    return
            
            # 카메라 설정
            w, h = self.prefer_size
            print(f"카메라 해상도 설정: {w}x{h}, FPS: {self.target_fps}")
            
            # Windows에서는 설정 순서가 중요할 수 있음
            if os.name == 'nt':
                # Windows: FPS 먼저 설정
                self.cap.set(cv.CAP_PROP_FPS, self.target_fps)
                self.cap.set(cv.CAP_PROP_FRAME_WIDTH, w)
                self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, h)
            else:
                # macOS/Linux: 해상도 먼저 설정
                self.cap.set(cv.CAP_PROP_FRAME_WIDTH, w)
                self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, h)
                self.cap.set(cv.CAP_PROP_FPS, self.target_fps)
            
            # 실제 설정된 값 확인
            actual_width = int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.cap.get(cv.CAP_PROP_FPS)
            
            print(f"실제 카메라 설정: {actual_width}x{actual_height}, FPS: {actual_fps}")
            
            # 로깅 레벨 설정
            try:
                cv.utils.logging.setLogLevel(cv.utils.logging.LOG_LEVEL_ERROR)
            except Exception:
                pass
                
            self.ok_cam = True
            print(f"웹캠 초기화 완료: 인덱스 {self.cam_index}, 해상도 {actual_width}x{actual_height}, FPS {actual_fps}")
            
        except Exception as e:
            self.ok_cam = False
            error_msg = f"카메라 초기화 실패: {e}"
            
            if os.name == 'nt':
                error_msg += "\n\nWindows 특정 해결 방법:"
                error_msg += "\n1. 관리자 권한으로 실행"
                error_msg += "\n2. DirectShow 필터 확인"
                error_msg += "\n3. webcam_test.py로 진단"
            
            self.err_cam = error_msg
            print(f"카메라 초기화 오류: {e}")
            import traceback
            traceback.print_exc()

    def _candidate_ports(self) -> List[str]:
        if list_ports is None:
            return []
        
        ports = []
        
        # macOS에서 glob 패턴으로 USB 시리얼 포트 찾기 (테스트 코드 방식)
        if glob is not None:
            try:
                usb_ports = glob.glob('/dev/tty.usbmodem*')
                usb_ports.extend(glob.glob('/dev/tty.usbserial*'))
                ports.extend(usb_ports)
            except Exception:
                pass
        
        # 기존 방식으로도 찾기
        for p in list_ports.comports():
            name = p.device
            if "usbmodem" in name or "usbserial" in name or name.startswith("COM"):
                if name not in ports:  # 중복 방지
                    ports.append(name)
        
        return sorted(set(ports))

    def _open_serial(self):
        if Serial is None:
            self.ok_ser = False
            self.err_ser = "pyserial 미설치: pip install pyserial"
            return

        port = self.serial_port
        if port is None:
            cands = self._candidate_ports()
            if cands:
                port = cands[0]
                print(f"자동 포트 감지: {port}")
            else:
                self.ok_ser = False
                self.err_ser = "직렬 포트를 찾지 못했습니다. 연결/드라이버 확인"
                return

        try:
            self.ser = Serial(port, self.serial_baud, timeout=1)  # 타임아웃 1초로 변경
            # 연결 후 버퍼 완전 클리어
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            time.sleep(0.5)  # 안정화 대기
            self.serial_port = port
            self.ok_ser = True
            self.err_ser = ""
            self._rx_buf = ""
            print(f"시리얼 연결 성공: {port} (baudrate: {self.serial_baud})")
        except Exception as e:
            self.ok_ser = False
            self.err_ser = f"직렬 포트 열기 실패: {e}"
            print(f"시리얼 연결 실패: {e}")

    def _serial_reconnect(self, next_port: Optional[str] = None):
        if self.ser:
            try: self.ser.close()
            except Exception: pass
            self.ser = None
        if next_port is not None:
            self.serial_port = next_port
        self._open_serial()

    def _consume_serial_lines(self):
        if not self.ok_ser or not self.ser:
            return
        try:
            # 테스트 코드와 동일한 방식으로 데이터 읽기
            if self.ser.in_waiting > 0:
                # UTF-8 디코딩 오류 방지를 위한 에러 처리 개선
                try:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        self._handle_serial_line(line)
                except UnicodeDecodeError as ude:
                    print(f"[SERIAL] UTF-8 디코딩 오류: {ude}")
                    # 버퍼 클리어
                    self.ser.reset_input_buffer()
                except Exception as decode_error:
                    print(f"[SERIAL] 디코딩 오류: {decode_error}")
                    # 버퍼 클리어
                    self.ser.reset_input_buffer()
        except Exception as e:
            print(f"[SERIAL] 읽기 오류: {e}")
            print(f"[SERIAL] 연결 상태: {self.ok_ser}, 포트: {self.serial_port}")
            # 연결이 끊어진 경우에만 연결 상태를 False로 변경
            if "device disconnected" in str(e).lower() or "permission denied" in str(e).lower():
                self.ok_ser = False
                self.err_ser = f"시리얼 연결 끊어짐: {e}"

    def _handle_serial_line(self, line: str):
        # 시리얼 데이터 수신 로그
        print(f"[SERIAL] 수신: {line}")
        
        # 테스트 코드와 동일한 JSON 파싱 방식
        try:
            # JSON 형식 파싱 시도
            obj = json.loads(line)
            
            # 새로운 Arduino 코드 형식 지원: {"distance": 25, "timestamp": 12345, "unit": "cm"}
            if "distance" in obj:
                try:
                    self._on_distance(float(obj["distance"]))
                except Exception as e:
                    print(f"거리 데이터 파싱 오류: {e}")
            
            # 기존 형식 지원: {"cm": 17}
            elif "cm" in obj:
                try:
                    self._on_distance(float(obj["cm"]))
                except Exception as e:
                    print(f"거리 데이터 파싱 오류: {e}")
            
            # 근접 감지: {"near": true}
            if obj.get("near"):
                self._on_near()
                
        except json.JSONDecodeError:
            # 일반 텍스트 형식 처리 (기존 호환성)
            if line.startswith("cm="):
                try:
                    self._on_distance(float(line.split("=",1)[1]))
                except Exception:
                    pass
            elif line.startswith("Distance:"):
                try:
                    # "Distance: 25 cm" 형식 처리
                    parts = line.split()
                    if len(parts) >= 2:
                        self._on_distance(float(parts[1]))
                except Exception:
                    pass
            else:
                print(f"알 수 없는 데이터 형식: {line}")
        except Exception as e:
            print(f"시리얼 데이터 처리 오류: {e}")

    # ---- 판정 로직 핵심 ----
    def _on_distance(self, d: float):
        self.latest_cm = d
        now = time.time()

        # 시리얼 로그 출력
        print(f"[SERIAL] 거리: {d:.1f}cm, 시간: {time.strftime('%H:%M:%S')}")

        # 시도 시작 조건 (공통): 거리 업데이트가 오면 "최근 업데이트 시각" 갱신
        self.last_update_ts = now

        # 최소거리 갱신(두 모드 공통)
        self.min_dist_cm = min(self.min_dist_cm, d)

        # SPEED 모드로 고정된 로직
        # 무장: ARM_ZONE_CM 이하로 처음 진입하면 기록 (시작 시간은 변경하지 않음)
        if (not self.armed) and d <= cfg.ARM_ZONE_CM:
            self.armed = True
            self.in_attempt = True
            print(f"[GAME] 무장! 거리: {d:.1f}cm, ARM_ZONE: {cfg.ARM_ZONE_CM}cm")

    def _on_near(self):
        now = time.time()
        # 쿨다운
        if (self.last_near_ts is not None) and (now - self.last_near_ts < self.near_cooldown_s):
            return
            
        # 이미 게임이 완료된 경우 무시
        if self.game_completed:
            return
            
        self.near_count += 1
        self.last_near_ts = now

        print(f"[SERIAL] 근접 감지! 거리: {self.latest_cm:.1f}cm, 시간: {time.strftime('%H:%M:%S')}")

        # SPEED 모드로 고정된 로직 (게임 시작부터 근접까지의 시간 측정)
        if self.armed and self.game_start_time is not None:
            elapsed_ms = int((now - self.game_start_time) * 1000)
            self.best_fast_ms = elapsed_ms if self.best_fast_ms is None else min(self.best_fast_ms, elapsed_ms)
            elapsed_sec = elapsed_ms / 1000.0
            print(f"[GAME] 기록! 소요시간: {elapsed_sec:.2f}초 (게임 시작부터 근접까지), 최고기록: {self.best_fast_ms}ms")
            
            # 리더보드에 기록 저장
            try:
                save_score(self.player_name, self.best_fast_ms, self.best_close_cm)
                elapsed_sec = self.best_fast_ms / 1000.0
                print(f"[GAME] 리더보드에 기록 저장됨: {self.player_name} - {elapsed_sec:.2f}초")
            except Exception as e:
                print(f"[GAME] 리더보드 저장 실패: {e}")
            
            # 게임 성공! 결과 화면으로 전환
            print(f"[GAME] 게임 성공! 결과 화면으로 전환합니다.")
            self.game_completed = True  # 게임 완료 상태 설정
            self.next = ("result", {
                "name": self.player_name,
                "best_fast_ms": self.best_fast_ms,
                "best_close_cm": self.best_close_cm,
            })
            return  # 즉시 전환
        
        # 시도 종료 (성공하지 못한 경우)
        self._reset_attempt()

    def _reset_attempt(self):
        self.in_attempt = False
        self.armed = False
        self.t_arm = None
        self.min_dist_cm = float("inf")
        self.last_update_ts = 0.0
        # 게임 시작 시간은 리셋하지 않음 (게임 전체 시간 측정)
        # 게임 완료 상태는 리셋하지 않음 (한 번 성공하면 계속 성공 상태 유지)

    # ---------- 입력 ----------
    def handle_event(self, e: pygame.event.Event):
        if e.type != pygame.KEYDOWN:
            return

        mods = e.mod
        has_shift = bool(mods & pygame.KMOD_SHIFT)
        has_ctrl  = bool(mods & pygame.KMOD_CTRL)
        has_cmd   = bool(mods & (pygame.KMOD_META | pygame.KMOD_LMETA | pygame.KMOD_RMETA))

        print(f"GameState: {e.key} pressed, mods={mods}, has_shift={has_shift}, has_ctrl={has_ctrl}, has_cmd={has_cmd}")
        # === HIDDEN WARP: Shift + (Ctrl or Cmd) + R → ResultState ===
        if e.key == pygame.K_r and has_shift and (has_ctrl or has_cmd):
            print("[warp] to ResultState (HIDDEN)")
            # 디버그 로그(원하면 지우세요)
            print("[warp] to ResultState",
                {"name": self.player_name, "best_fast_ms": self.best_fast_ms, "best_close_cm": self.best_close_cm})
            self.next = ("result", {
                "name": self.player_name,
                "best_fast_ms": 1000,
                "best_close_cm": self.best_close_cm,
            })
            return  # ← 중요! 아래 R(재연결) 분기로 내려가지 않도록 종료

        # === 일반 키 처리 ===
        if e.key == pygame.K_ESCAPE:
            self.next = ("title", {})

        elif e.key == pygame.K_m:
            self.mirror = not self.mirror

        elif e.key == pygame.K_r:
            # R 단독: 시리얼 재연결
            self._serial_reconnect()

        elif e.key == pygame.K_p:
            cands = self._candidate_ports()
            if cands:
                if self.serial_port in cands:
                    idx = (cands.index(self.serial_port) + 1) % len(cands)
                else:
                    idx = 0
                self._serial_reconnect(cands[idx])

        elif e.key == pygame.K_1:
            print("[GAME] 모드 변경 비활성화됨 (SPEED 모드로 고정)")

        elif e.key == pygame.K_2:
            print("[GAME] 모드 변경 비활성화됨 (SPEED 모드로 고정)")

        elif e.key == pygame.K_n:
            self._reset_attempt()
            self.in_attempt = True
            self.t_arm = time.time() if self.mode == "SPEED" else None
            self.armed = (self.mode == "SPEED")

        elif e.key == pygame.K_c:
            self.best_fast_ms = None
            self.best_close_cm = None
            self._reset_attempt()
            
        elif e.key == pygame.K_t:
            # 테스트용: 강제로 기록 생성
            print("[GAME] 테스트 기록 생성")
            if self.game_start_time is not None:
                test_time = int((time.time() - self.game_start_time) * 1000)
            else:
                test_time = 1500  # 기본값
            self.best_fast_ms = test_time
            try:
                save_score(self.player_name, self.best_fast_ms, self.best_close_cm)
                test_sec = test_time / 1000.0
                print(f"[GAME] 테스트 기록 저장됨: {self.player_name} - {test_sec:.2f}초 (게임 시작부터)")
            except Exception as e:
                print(f"[GAME] 테스트 기록 저장 실패: {e}")


    # ---------- 업데이트 ----------
    def update(self, dt: float):
        # 카메라
        if self.ok_cam and self.cap:
            ret, frame = self.cap.read()
            if ret:
                if self.mirror:
                    frame = cv.flip(frame, 1)
                self.frame = frame
            else:
                self.frame = None
                self.err_cam = "웹캠 프레임을 읽지 못했습니다."

        # 게임이 완료된 경우 업데이트 중단
        if self.game_completed:
            return
            
        # 시리얼
        self._consume_serial_lines()
        
        # 시리얼 상태 주기적 로깅 (5초마다)
        if hasattr(self, '_last_serial_log') and (time.time() - self._last_serial_log > 5):
            print(f"[SERIAL] 상태: {'연결됨' if self.ok_ser else '연결안됨'}, 포트: {self.serial_port}, 오류: {self.err_ser}")
            self._last_serial_log = time.time()
        elif not hasattr(self, '_last_serial_log'):
            self._last_serial_log = time.time()

        # 시도 종료 판정(타임아웃)
        if self.in_attempt and (time.time() - self.last_update_ts > cfg.ATTEMPT_GAP_S):
            # SPEED 모드로 고정된 로직
            # 실패(near 못 받음) → 참고용 최소거리 메시지로 끝
            # 기록은 갱신하지 않음
            print(f"[GAME] 시도 타임아웃! 최소거리: {self.min_dist_cm:.1f}cm")
            self._reset_attempt()

    # ---------- 렌더 ----------
    def render(self, viewport: Viewport, fonts: FontPack):
        S = viewport.S
        canvas = viewport.canvas
        
        # 배경 그리기 (화면을 꽉 채우도록)
        if self.bg_image:
            bg_scaled = pygame.transform.scale(self.bg_image, (viewport.scaled_w, viewport.scaled_h))
            canvas.blit(bg_scaled, (0, 0))
        else:
            canvas.fill((135, 206, 235))  # 하늘색 기본 배경

        # 타이틀 이미지 (상단 중앙)
        if self.title_image:
            # 원본 로고 크기
            orig_logo_w, orig_logo_h = self.title_image.get_size()
            orig_ratio = orig_logo_w / orig_logo_h
            
            # 기존 크기의 8배로 설정
            logo_width = S(500 * 8)  # 기존 500에서 8배
            logo_height = int(logo_width / orig_ratio)
            
            # 화면에 맞게 제한 (화면 너비의 90%, 높이의 40% 이하)
            max_logo_width = int(viewport.scaled_w * 0.9)
            max_logo_height = int(viewport.scaled_h * 0.4)
            
            if logo_width > max_logo_width:
                logo_width = max_logo_width
                logo_height = int(logo_width / orig_ratio)
                
            if logo_height > max_logo_height:
                logo_height = max_logo_height
                logo_width = int(logo_height * orig_ratio)
            
            logo_scaled = pygame.transform.scale(self.title_image, (logo_width, logo_height))
            logo_x = (viewport.scaled_w - logo_scaled.get_width()) // 2
            logo_y = S(-30)
            canvas.blit(logo_scaled, (logo_x, logo_y))

        # 광명x쓸모 이미지 (우상단)
        if self.gwangmyeong_image:
            gwang_scaled = pygame.transform.scale(self.gwangmyeong_image, (S(240), S(160)))
            gwang_x = viewport.scaled_w - S(280)
            gwang_y = S(0)
            canvas.blit(gwang_scaled, (gwang_x, gwang_y))

        # 중앙 웹캠 비디오 패널
        video_width = min(S(800), int(viewport.scaled_w * 0.7))
        video_height = int(viewport.scaled_h * 0.7)
        video_x = (viewport.scaled_w - video_width) // 2
        video_y = (viewport.scaled_h - video_height) // 2 + S(60)
        video_rect = pygame.Rect(video_x, video_y, video_width, video_height)
        
        # 비디오 패널 배경 (흰색)
        pygame.draw.rect(canvas, (255, 255, 255), video_rect)
        pygame.draw.rect(canvas, (200, 200, 200), video_rect, S(3))
        
        # 웹캠 영상 표시
        if self.frame is None:
            # 웹캠이 없을 때 메시지
            msg = self.err_cam or "웹캠 초기화 중..."
            text_surface = fonts.h2.render(msg, True, (100, 100, 100))
            text_x = video_x + (video_width - text_surface.get_width()) // 2
            text_y = video_y + (video_height - text_surface.get_height()) // 2
            canvas.blit(text_surface, (text_x, text_y))
        else:
            # 웹캠 영상 표시 (패널 내부에 맞춰서)
            fh, fw = self.frame.shape[:2]
            # 패널 내부 여백 고려
            inner_rect = pygame.Rect(video_x + S(10), video_y, 
                                   video_width - S(20), video_height )
            
            scale = min(inner_rect.w / fw, inner_rect.h / fh)
            tw, th = int(fw * scale), int(fh * scale)
            tx = inner_rect.x + (inner_rect.w - tw) // 2
            ty = inner_rect.y + (inner_rect.h - th) // 2
            
            rgb = cv.cvtColor(self.frame, cv.COLOR_BGR2RGB)
            surf = pygame.image.frombuffer(rgb.tobytes(), (fw, fh), "RGB")
            if (fw, fh) != (tw, th):
                surf = pygame.transform.smoothscale(surf, (tw, th))
            canvas.blit(surf, (tx, ty))

        # 캐릭터들 배치
        if self.character_left:
            char_left_scaled = pygame.transform.scale(self.character_left, (S(150), S(200)))
            char_left_x = S(50)
            char_left_y = viewport.scaled_h - char_left_scaled.get_height() - S(50)
            canvas.blit(char_left_scaled, (char_left_x, char_left_y))
            
        if self.character_right:
            char_right_scaled = pygame.transform.scale(self.character_right, (S(150), S(200)))
            char_right_x = viewport.scaled_w - char_right_scaled.get_width() - S(50)
            char_right_y = viewport.scaled_h - char_right_scaled.get_height() - S(50)
            canvas.blit(char_right_scaled, (char_right_x, char_right_y))
            
        # 상단 우측 캐릭터
        if self.character_top_right:
            char_top_scaled = pygame.transform.scale(self.character_top_right, (S(120), S(160)))
            char_top_x = viewport.scaled_w - char_top_scaled.get_width() - S(50)
            char_top_y = S(50)
            canvas.blit(char_top_scaled, (char_top_x, char_top_y))

        # 게임 완료 메시지 표시
        if self.game_completed:
            # 반투명 오버레이
            overlay = pygame.Surface((viewport.scaled_w, viewport.scaled_h))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            canvas.blit(overlay, (0, 0))
            
            # 성공 메시지
            elapsed_sec = self.best_fast_ms / 1000.0 if self.best_fast_ms is not None else 0
            success_text = f"성공! 소요시간: {elapsed_sec:.2f}초"
            text_surface = fonts.h1.render(success_text, True, cfg.OK)
            text_x = (viewport.scaled_w - text_surface.get_width()) // 2
            text_y = (viewport.scaled_h - text_surface.get_height()) // 2
            canvas.blit(text_surface, (text_x, text_y))
            
            # 결과 화면으로 전환 중 메시지
            transition_text = "결과 화면으로 전환 중..."
            trans_surface = fonts.h3.render(transition_text, True, cfg.TEXT)
            trans_x = (viewport.scaled_w - trans_surface.get_width()) // 2
            trans_y = text_y + text_surface.get_height() + S(20)
            canvas.blit(trans_surface, (trans_x, trans_y))
