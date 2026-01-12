# ui/admin_state.py
# 관리자 페이지 - 시스템 설정 및 관리
import pygame
import os
import time
import json
from typing import Optional, List, Dict
import config as cfg
from core.viewport import Viewport
from core.fonts import FontPack
from core.leaderboard import load_scores, save_score, DATA_FILE
from core.path_utils import get_asset_path, safe_image_load
from core.settings import get_camera_index, set_camera_index, get_serial_port, set_serial_port

try:
    from serial import Serial
    from serial.tools import list_ports
    import glob
except Exception:
    Serial = None
    list_ports = None
    glob = None

try:
    import cv2 as cv
except Exception:
    cv = None

class AdminState:
    def __init__(self):
        # 시리얼/센서 (저장된 포트 로드)
        self.ser = None
        saved_port = get_serial_port()
        self.serial_port = saved_port if saved_port else cfg.SERIAL_DEFAULT_PORT
        self.serial_baud = cfg.SERIAL_BAUD
        self.serial_connected = False
        self.serial_error = ""
        self.latest_distance = None
        self.distance_history: List[float] = []
        self._rx_buf = ""
        
        # 카메라 (저장된 인덱스 로드)
        self.camera_index = get_camera_index()
        self.camera_connected = False
        self.camera_error = ""
        self.camera_frame = None
        self.cap = None
        
        # 리더보드
        self.leaderboard_data: List[Dict] = []
        self.selected_row = 0
        self.scroll_offset = 0
        self.edit_mode = False
        self.edit_field = None  # 'name', 'score', etc.
        self.edit_value = ""
        
        # UI 상태
        self.tab = "serial"  # 'serial', 'camera', 'leaderboard'
        self.next: Optional[tuple[str, dict]] = None
        
        # 배경 이미지
        self._load_images()
        
        # 자동 연결 시도
        self._try_connect_serial()
        self._try_connect_camera()
        self._load_leaderboard()
    
    def _load_images(self):
        """배경 이미지 로딩"""
        base_path = get_asset_path("images", "title_state")
        try:
            self.bg_image = safe_image_load(os.path.join(base_path, "background.jpg"))
            self.board_background = safe_image_load(os.path.join(base_path, "board_background.png"))
        except Exception as e:
            print(f"관리자 페이지 이미지 로딩 실패: {e}")
            self.bg_image = None
            self.board_background = None
    
    # ========== 시리얼/센서 ==========
    def _candidate_ports(self) -> List[str]:
        """사용 가능한 시리얼 포트 찾기"""
        if list_ports is None:
            return []
        
        ports = []
        
        # macOS에서 USB 시리얼 포트 찾기
        if glob is not None:
            try:
                usb_ports = glob.glob('/dev/tty.usbmodem*')
                usb_ports.extend(glob.glob('/dev/tty.usbserial*'))
                ports.extend(usb_ports)
            except Exception:
                pass
        
        # Windows/Linux에서 포트 찾기
        for p in list_ports.comports():
            name = p.device
            if "usbmodem" in name or "usbserial" in name or name.startswith("COM"):
                if name not in ports:
                    ports.append(name)
        
        return sorted(set(ports))
    
    def _try_connect_serial(self):
        """시리얼 포트 연결 시도"""
        if Serial is None:
            self.serial_error = "pyserial이 설치되지 않았습니다"
            return False
        
        # 이미 연결되어 있으면 해제
        if self.ser:
            try:
                self.ser.close()
            except:
                pass
            self.ser = None
        
        # 포트 자동 찾기
        if self.serial_port is None:
            ports = self._candidate_ports()
            if ports:
                self.serial_port = ports[0]
            else:
                self.serial_error = "시리얼 포트를 찾을 수 없습니다"
                self.serial_connected = False
                return False
        
        # 연결 시도
        try:
            self.ser = Serial(self.serial_port, self.serial_baud, timeout=1)
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            time.sleep(0.5)
            self.serial_connected = True
            self.serial_error = ""
            set_serial_port(self.serial_port)  # 포트 저장
            print(f"[ADMIN] 시리얼 연결 성공: {self.serial_port}")
            return True
        except Exception as e:
            self.serial_connected = False
            self.serial_error = f"연결 실패: {e}"
            print(f"[ADMIN] 시리얼 연결 실패: {e}")
            return False
    
    def _disconnect_serial(self):
        """시리얼 포트 연결 해제"""
        if self.ser:
            try:
                self.ser.close()
            except:
                pass
            self.ser = None
        self.serial_connected = False
        self.serial_error = ""
    
    def _read_serial(self):
        """시리얼 데이터 읽기"""
        if not self.serial_connected or not self.ser:
            return
        
        try:
            if self.ser.in_waiting > 0:
                try:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        self._handle_serial_line(line)
                except Exception as e:
                    print(f"[ADMIN] 시리얼 읽기 오류: {e}")
        except Exception as e:
            print(f"[ADMIN] 시리얼 연결 오류: {e}")
            self.serial_connected = False
            self.serial_error = str(e)
    
    def _handle_serial_line(self, line: str):
        """시리얼 데이터 파싱"""
        try:
            # JSON 형식 파싱
            obj = json.loads(line)
            
            if "distance" in obj:
                distance = float(obj["distance"])
                self.latest_distance = distance
                self.distance_history.append(distance)
                if len(self.distance_history) > 50:
                    self.distance_history.pop(0)
            elif "cm" in obj:
                distance = float(obj["cm"])
                self.latest_distance = distance
                self.distance_history.append(distance)
                if len(self.distance_history) > 50:
                    self.distance_history.pop(0)
        except json.JSONDecodeError:
            # 텍스트 형식
            if "cm=" in line:
                try:
                    distance = float(line.split("=", 1)[1])
                    self.latest_distance = distance
                    self.distance_history.append(distance)
                    if len(self.distance_history) > 50:
                        self.distance_history.pop(0)
                except:
                    pass
        except Exception as e:
            print(f"[ADMIN] 데이터 파싱 오류: {e}")
    
    # ========== 카메라 ==========
    def _try_connect_camera(self):
        """카메라 연결 시도"""
        if cv is None:
            self.camera_error = "opencv-python이 설치되지 않았습니다"
            return False
        
        # 이미 연결되어 있으면 해제
        if self.cap:
            try:
                self.cap.release()
            except:
                pass
            self.cap = None
        
        # 연결 시도
        try:
            if os.name == 'nt':
                backends = [cv.CAP_DSHOW, cv.CAP_MSMF, cv.CAP_ANY]
            else:
                backends = [cv.CAP_AVFOUNDATION, cv.CAP_V4L2, cv.CAP_ANY]
            
            for backend in backends:
                try:
                    self.cap = cv.VideoCapture(self.camera_index, backend)
                    if self.cap and self.cap.isOpened():
                        self.camera_connected = True
                        self.camera_error = ""
                        set_camera_index(self.camera_index)  # 인덱스 저장
                        print(f"[ADMIN] 카메라 연결 성공: 인덱스 {self.camera_index}")
                        return True
                    else:
                        if self.cap:
                            self.cap.release()
                        self.cap = None
                except Exception as e:
                    print(f"[ADMIN] 백엔드 {backend} 실패: {e}")
                    continue
            
            self.camera_connected = False
            self.camera_error = f"카메라 인덱스 {self.camera_index}에 연결할 수 없습니다"
            return False
            
        except Exception as e:
            self.camera_connected = False
            self.camera_error = f"연결 실패: {e}"
            print(f"[ADMIN] 카메라 연결 실패: {e}")
            return False
    
    def _disconnect_camera(self):
        """카메라 연결 해제"""
        if self.cap:
            try:
                self.cap.release()
            except:
                pass
            self.cap = None
        self.camera_connected = False
        self.camera_frame = None
        self.camera_error = ""
    
    def _read_camera(self):
        """카메라 프레임 읽기"""
        if not self.camera_connected or not self.cap:
            return
        
        try:
            ret, frame = self.cap.read()
            if ret:
                self.camera_frame = cv.flip(frame, 1)
            else:
                self.camera_frame = None
        except Exception as e:
            print(f"[ADMIN] 카메라 읽기 오류: {e}")
    
    # ========== 리더보드 ==========
    def _load_leaderboard(self):
        """리더보드 데이터 로드"""
        try:
            self.leaderboard_data = load_scores()
        except Exception as e:
            print(f"[ADMIN] 리더보드 로딩 실패: {e}")
            self.leaderboard_data = []
    
    def _save_leaderboard(self):
        """리더보드 데이터 저장"""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.leaderboard_data, f, ensure_ascii=False, indent=2)
            print("[ADMIN] 리더보드 저장 완료")
        except Exception as e:
            print(f"[ADMIN] 리더보드 저장 실패: {e}")
    
    def _delete_selected_row(self):
        """선택된 행 삭제"""
        if 0 <= self.selected_row < len(self.leaderboard_data):
            deleted = self.leaderboard_data.pop(self.selected_row)
            print(f"[ADMIN] 삭제됨: {deleted}")
            self._save_leaderboard()
            if self.selected_row >= len(self.leaderboard_data):
                self.selected_row = max(0, len(self.leaderboard_data) - 1)
    
    def _edit_selected_row(self, field: str):
        """선택된 행 편집 시작"""
        if 0 <= self.selected_row < len(self.leaderboard_data):
            self.edit_mode = True
            self.edit_field = field
            row = self.leaderboard_data[self.selected_row]
            if field == "name":
                self.edit_value = row.get("name", "")
            elif field == "score":
                self.edit_value = str(row.get("best_fast_ms", 0))
    
    def _save_edit(self):
        """편집 내용 저장"""
        if not self.edit_mode or self.edit_field is None:
            return
        
        if 0 <= self.selected_row < len(self.leaderboard_data):
            row = self.leaderboard_data[self.selected_row]
            
            if self.edit_field == "name":
                row["name"] = self.edit_value.strip()
            elif self.edit_field == "score":
                try:
                    row["best_fast_ms"] = int(self.edit_value)
                except ValueError:
                    print("[ADMIN] 잘못된 점수 형식")
            
            self._save_leaderboard()
        
        self.edit_mode = False
        self.edit_field = None
        self.edit_value = ""
    
    def _cancel_edit(self):
        """편집 취소"""
        self.edit_mode = False
        self.edit_field = None
        self.edit_value = ""
    
    # ========== 라이프사이클 ==========
    def enter(self):
        """상태 진입"""
        pygame.key.start_text_input()
        self._load_leaderboard()
    
    def exit(self):
        """상태 종료"""
        pygame.key.stop_text_input()
        self._disconnect_serial()
        self._disconnect_camera()
    
    # ========== 이벤트 처리 ==========
    def handle_event(self, e: pygame.event.Event):
        # 편집 모드일 때
        if self.edit_mode:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN or e.key == pygame.K_KP_ENTER:
                    self._save_edit()
                elif e.key == pygame.K_ESCAPE:
                    self._cancel_edit()
                elif e.key == pygame.K_BACKSPACE:
                    self.edit_value = self.edit_value[:-1]
            elif e.type == pygame.TEXTINPUT:
                self.edit_value += e.text
            return
        
        # 일반 모드
        if e.type == pygame.KEYDOWN:
            # ESC: 타이틀로 돌아가기
            if e.key == pygame.K_ESCAPE:
                self.next = ("title", {})
            
            # 화살표 키로 탭 전환 (← →)
            elif e.key == pygame.K_LEFT:
                # 왼쪽 화살표: 이전 탭
                if self.tab == "camera":
                    self.tab = "serial"
                elif self.tab == "leaderboard":
                    self.tab = "camera"
            elif e.key == pygame.K_RIGHT:
                # 오른쪽 화살표: 다음 탭
                if self.tab == "serial":
                    self.tab = "camera"
                elif self.tab == "camera":
                    self.tab = "leaderboard"
                    self._load_leaderboard()
            
            # 숫자 키로도 직접 탭 전환 가능 (기존 기능 유지)
            elif e.key == pygame.K_1:
                self.tab = "serial"
            elif e.key == pygame.K_2:
                self.tab = "camera"
            elif e.key == pygame.K_3:
                self.tab = "leaderboard"
                self._load_leaderboard()
            
            # 시리얼 탭
            elif self.tab == "serial":
                if e.key == pygame.K_c:  # Connect
                    self._try_connect_serial()
                elif e.key == pygame.K_d:  # Disconnect
                    self._disconnect_serial()
                elif e.key == pygame.K_p:  # Next Port
                    ports = self._candidate_ports()
                    if ports:
                        if self.serial_port in ports:
                            idx = (ports.index(self.serial_port) + 1) % len(ports)
                        else:
                            idx = 0
                        self.serial_port = ports[idx]
                        self._try_connect_serial()
            
            # 카메라 탭
            elif self.tab == "camera":
                if e.key == pygame.K_c:  # Connect
                    self._try_connect_camera()
                elif e.key == pygame.K_d:  # Disconnect
                    self._disconnect_camera()
                elif e.key == pygame.K_UP:  # Camera Index +1
                    self.camera_index = min(9, self.camera_index + 1)
                    self._try_connect_camera()
                elif e.key == pygame.K_DOWN:  # Camera Index -1
                    self.camera_index = max(0, self.camera_index - 1)
                    self._try_connect_camera()
                elif e.key in [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, 
                              pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7,
                              pygame.K_8, pygame.K_9]:
                    # 숫자 키로 직접 인덱스 선택
                    self.camera_index = e.key - pygame.K_0
                    self._try_connect_camera()
            
            # 리더보드 탭
            elif self.tab == "leaderboard":
                if e.key == pygame.K_UP:
                    self.selected_row = max(0, self.selected_row - 1)
                elif e.key == pygame.K_DOWN:
                    self.selected_row = min(len(self.leaderboard_data) - 1, self.selected_row + 1)
                elif e.key == pygame.K_DELETE or e.key == pygame.K_BACKSPACE:
                    self._delete_selected_row()
                elif e.key == pygame.K_n:  # Edit Name
                    self._edit_selected_row("name")
                elif e.key == pygame.K_s:  # Edit Score
                    self._edit_selected_row("score")
                elif e.key == pygame.K_r:  # Reload
                    self._load_leaderboard()
    
    # ========== 업데이트 ==========
    def update(self, dt: float):
        """상태 업데이트"""
        if self.tab == "serial" and self.serial_connected:
            self._read_serial()
        elif self.tab == "camera" and self.camera_connected:
            self._read_camera()
    
    # ========== 렌더 ==========
    def render(self, viewport: Viewport, fonts: FontPack):
        S = viewport.S
        canvas = viewport.canvas
        
        # 배경
        if self.bg_image:
            bg_scaled = pygame.transform.scale(self.bg_image, (viewport.scaled_w, viewport.scaled_h))
            canvas.blit(bg_scaled, (0, 0))
        else:
            canvas.fill((20, 25, 35))
        
        # 제목
        title_text = ""
        title_surf = fonts.h1.render(title_text, True, cfg.ACC)
        title_x = (viewport.scaled_w - title_surf.get_width()) // 2
        canvas.blit(title_surf, (title_x, S(20)))
        
        # 탭 버튼
        self._draw_tabs(canvas, viewport, fonts, S)
        
        # 메인 패널
        panel_y = S(150)
        panel_h = viewport.scaled_h - panel_y - S(100)
        
        if self.tab == "serial":
            self._render_serial_tab(canvas, viewport, fonts, S, panel_y, panel_h)
        elif self.tab == "camera":
            self._render_camera_tab(canvas, viewport, fonts, S, panel_y, panel_h)
        elif self.tab == "leaderboard":
            self._render_leaderboard_tab(canvas, viewport, fonts, S, panel_y, panel_h)
        
        # 하단 안내
        help_text = "ESC: 나가기"
        help_surf = fonts.txt.render(help_text, True, cfg.SUBT)
        help_x = (viewport.scaled_w - help_surf.get_width()) // 2
        canvas.blit(help_surf, (help_x, viewport.scaled_h - S(50)))
    
    def _draw_tabs(self, canvas, viewport, fonts, S):
        """탭 버튼 그리기"""
        tabs = [
            ("1. 시리얼/센서", "serial"),
            ("2. 카메라", "camera"),
            ("3. 리더보드", "leaderboard")
        ]
        
        tab_width = S(250)
        tab_height = S(50)
        total_width = tab_width * len(tabs) + S(20) * (len(tabs) - 1)
        start_x = (viewport.scaled_w - total_width) // 2
        y = S(80)
        
        for i, (label, tab_id) in enumerate(tabs):
            x = start_x + i * (tab_width + S(20))
            rect = pygame.Rect(x, y, tab_width, tab_height)
            
            # 활성 탭 강조
            if self.tab == tab_id:
                color = cfg.ACC
                text_color = (255, 255, 255)
            else:
                color = (60, 70, 90)
                text_color = cfg.TEXT
            
            pygame.draw.rect(canvas, color, rect, border_radius=S(10))
            
            text_surf = fonts.h3.render(label, True, text_color)
            text_x = x + (tab_width - text_surf.get_width()) // 2
            text_y = y + (tab_height - text_surf.get_height()) // 2
            canvas.blit(text_surf, (text_x, text_y))
    
    def _render_serial_tab(self, canvas, viewport, fonts, S, panel_y, panel_h):
        """시리얼/센서 탭 렌더링"""
        panel_w = min(S(900), int(viewport.scaled_w * 0.85))
        panel_x = (viewport.scaled_w - panel_w) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        
        # 패널 배경
        if not self.board_background:
            bg_scaled = pygame.transform.scale(self.board_background, (panel_w, panel_h))
            canvas.blit(bg_scaled, (panel_x, panel_y))
        else:
            panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel_surf.fill((255, 255, 255, 230))
            canvas.blit(panel_surf, panel_rect)
        
        y = panel_y + S(30)
        x = panel_x + S(50)
        
        # 연결 상태
        status_text = f"상태: {'연결됨' if self.serial_connected else '연결 안 됨'}"
        status_color = cfg.OK if self.serial_connected else cfg.WARN
        status_surf = fonts.h2.render(status_text, True, status_color)
        canvas.blit(status_surf, (x, y))
        y += S(60)
        
        # 포트 정보
        port_text = f"포트: {self.serial_port if self.serial_port else '없음'}"
        port_surf = fonts.h3.render(port_text, True, cfg.TEXT)
        canvas.blit(port_surf, (x, y))
        y += S(50)
        
        # 에러 메시지
        if self.serial_error:
            error_surf = fonts.txt.render(f"오류: {self.serial_error}", True, cfg.WARN)
            canvas.blit(error_surf, (x, y))
            y += S(50)
        
        # 현재 거리
        if self.latest_distance is not None:
            distance_text = f"현재 거리: {self.latest_distance:.1f} cm"
            distance_surf = fonts.h2.render(distance_text, True, cfg.ACC)
            canvas.blit(distance_surf, (x, y))
            y += S(80)
            
            # 거리 히스토리 그래프
            if len(self.distance_history) > 1:
                graph_w = panel_w - S(100)
                graph_h = S(150)
                graph_x = x
                graph_y = y
                
                # 그래프 배경
                graph_rect = pygame.Rect(graph_x, graph_y, graph_w, graph_h)
                pygame.draw.rect(canvas, (240, 240, 240), graph_rect)
                pygame.draw.rect(canvas, (200, 200, 200), graph_rect, S(2))
                
                # 데이터 포인트
                max_val = max(self.distance_history) if self.distance_history else 100
                min_val = min(self.distance_history) if self.distance_history else 0
                range_val = max_val - min_val if max_val > min_val else 1
                
                points = []
                for i, val in enumerate(self.distance_history):
                    px = graph_x + int((i / len(self.distance_history)) * graph_w)
                    py = graph_y + graph_h - int(((val - min_val) / range_val) * graph_h)
                    points.append((px, py))
                
                if len(points) > 1:
                    pygame.draw.lines(canvas, cfg.ACC, False, points, S(3))
                
                y += graph_h + S(20)
        
        y += S(50)
        
        # 버튼 안내
        help_lines = [
            "C: 연결 시도",
            "D: 연결 해제",
            "P: 다음 포트"
        ]
        
        for line in help_lines:
            help_surf = fonts.txt.render(line, True, cfg.SUBT)
            canvas.blit(help_surf, (x, y))
            y += S(35)
    
    def _render_camera_tab(self, canvas, viewport, fonts, S, panel_y, panel_h):
        """카메라 탭 렌더링"""
        panel_w = min(S(900), int(viewport.scaled_w * 0.85))
        panel_x = (viewport.scaled_w - panel_w) // 2
        
        # 패널 배경
        if not self.board_background:
            bg_scaled = pygame.transform.scale(self.board_background, (panel_w, panel_h))
            canvas.blit(bg_scaled, (panel_x, panel_y))
        else:
            panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel_surf.fill((255, 255, 255, 230))
            canvas.blit(panel_surf, (panel_x, panel_y))
        
        y = panel_y + S(30)
        x = panel_x + S(50)
        
        # 연결 상태
        status_text = f"상태: {'연결됨' if self.camera_connected else '연결 안 됨'}"
        status_color = cfg.OK if self.camera_connected else cfg.WARN
        status_surf = fonts.h2.render(status_text, True, status_color)
        canvas.blit(status_surf, (x, y))
        y += S(60)
        
        # 카메라 인덱스
        index_text = f"카메라 인덱스: {self.camera_index}"
        index_surf = fonts.h3.render(index_text, True, cfg.TEXT)
        canvas.blit(index_surf, (x, y))
        y += S(50)
        
        # 에러 메시지
        if self.camera_error:
            error_surf = fonts.txt.render(f"오류: {self.camera_error}", True, cfg.WARN)
            canvas.blit(error_surf, (x, y))
            y += S(50)
        
        # 카메라 프리뷰
        if self.camera_frame is not None:
            y += S(20)
            preview_w = panel_w - S(100)
            preview_h = int(preview_w * 9 / 16)  # 16:9 비율
            
            fh, fw = self.camera_frame.shape[:2]
            scale = min(preview_w / fw, preview_h / fh)
            tw, th = int(fw * scale), int(fh * scale)
            
            preview_x = x + (preview_w - tw) // 2
            preview_y = y
            
            rgb = cv.cvtColor(self.camera_frame, cv.COLOR_BGR2RGB)
            surf = pygame.image.frombuffer(rgb.tobytes(), (fw, fh), "RGB")
            if (fw, fh) != (tw, th):
                surf = pygame.transform.smoothscale(surf, (tw, th))
            
            canvas.blit(surf, (preview_x, preview_y))
            y += th + S(30)
        
        # 버튼 안내
        help_lines = [
            "C: 연결 시도",
            "D: 연결 해제",
            "↑/↓: 인덱스 변경",
            "0-9: 인덱스 직접 선택"
        ]
        
        for line in help_lines:
            help_surf = fonts.txt.render(line, True, cfg.SUBT)
            canvas.blit(help_surf, (x, y))
            y += S(35)
    
    def _render_leaderboard_tab(self, canvas, viewport, fonts, S, panel_y, panel_h):
        """리더보드 탭 렌더링"""
        panel_w = min(S(900), int(viewport.scaled_w * 0.85))
        panel_x = (viewport.scaled_w - panel_w) // 2
        
        # 패널 배경
        if not self.board_background:
            bg_scaled = pygame.transform.scale(self.board_background, (panel_w, panel_h))
            canvas.blit(bg_scaled, (panel_x, panel_y))
        else:
            panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel_surf.fill((255, 255, 255, 230))
            canvas.blit(panel_surf, (panel_x, panel_y))
        
        y = panel_y + S(30)
        x = panel_x + S(50)
        
        # 제목
        title_surf = fonts.h2.render("리더보드 데이터", True, cfg.TEXT)
        canvas.blit(title_surf, (x, y))
        y += S(60)
        
        # 테이블 헤더
        col_w = [S(60), S(250), S(150), S(150)]
        col_x = [x, x + col_w[0], x + col_w[0] + col_w[1], x + col_w[0] + col_w[1] + col_w[2]]
        headers = ["순위", "이름", "시간(ms)", "점수"]
        
        for i, header in enumerate(headers):
            header_surf = fonts.h3.render(header, True, cfg.ACC)
            canvas.blit(header_surf, (col_x[i], y))
        y += S(50)
        
        # 구분선
        pygame.draw.line(canvas, cfg.LINE, (x, y), (x + sum(col_w), y), S(2))
        y += S(10)
        
        # 데이터 행들
        visible_rows = min(8, len(self.leaderboard_data))
        for i in range(visible_rows):
            idx = i + self.scroll_offset
            if idx >= len(self.leaderboard_data):
                break
            
            row = self.leaderboard_data[idx]
            
            # 선택된 행 강조
            if idx == self.selected_row:
                highlight_rect = pygame.Rect(x - S(10), y - S(5), sum(col_w) + S(20), S(40))
                pygame.draw.rect(canvas, (255, 255, 200, 100), highlight_rect)
            
            # 순위
            rank_text = str(idx + 1)
            rank_surf = fonts.txt.render(rank_text, True, cfg.TEXT)
            canvas.blit(rank_surf, (col_x[0], y))
            
            # 이름
            name = row.get("name", "")
            if self.edit_mode and idx == self.selected_row and self.edit_field == "name":
                name_text = f"> {self.edit_value}_"
                name_color = cfg.ACC
            else:
                name_text = name
                name_color = cfg.TEXT
            name_surf = fonts.txt.render(name_text, True, name_color)
            canvas.blit(name_surf, (col_x[1], y))
            
            # 시간
            time_ms = row.get("best_fast_ms", 0)
            if self.edit_mode and idx == self.selected_row and self.edit_field == "score":
                time_text = f"> {self.edit_value}_"
                time_color = cfg.ACC
            else:
                time_text = str(time_ms)
                time_color = cfg.TEXT
            time_surf = fonts.txt.render(time_text, True, time_color)
            canvas.blit(time_surf, (col_x[2], y))
            
            # 점수
            score = row.get("best_score", 0)
            score_surf = fonts.txt.render(str(score), True, cfg.TEXT)
            canvas.blit(score_surf, (col_x[3], y))
            
            y += S(45)
        
        y += S(30)
        
        # 버튼 안내
        if self.edit_mode:
            help_lines = [
                "Enter: 저장",
                "ESC: 취소"
            ]
        else:
            help_lines = [
                "↑/↓: 선택",
                "N: 이름 편집",
                "S: 점수 편집",
                "Delete: 삭제",
                "R: 새로고침"
            ]
        
        for line in help_lines:
            help_surf = fonts.txt.render(line, True, cfg.SUBT)
            canvas.blit(help_surf, (x, y))
            y += S(35)
