# ui/result_state.py
import pygame
import os
from typing import Optional
import config as cfg
from core.viewport import Viewport
from core.fonts import FontPack
from ui.components import draw_card
from core.path_utils import get_asset_path, safe_image_load

class ResultState:
    def __init__(
        self,
        player_name: str,
        best_fast_ms: Optional[int] = None,
        best_close_cm: Optional[float] = None,
    ):
        self.player_name = player_name
        self.best_fast_ms = best_fast_ms
        self.best_close_cm = best_close_cm

        self.next: Optional[tuple[str, dict]] = None  # ('title', {}) 로 세팅
        self.timer = 0.0
        
        # 이미지 로딩
        self._load_images()

    def _load_images(self):
        """결과 화면용 이미지들을 로딩합니다."""
        base_path = get_asset_path("images", "result_state")
        
        try:
            # 배경 이미지
            self.bg_image = safe_image_load(os.path.join(base_path, "background.jpg"))
            
            # 타이틀 로고
            self.title_logo = safe_image_load(os.path.join(base_path, "title_adventure.png"))
            
            # 리더보드 배경
            self.board_background = safe_image_load(os.path.join(base_path, "board_background.png"))
            
            # 캐릭터 이미지들
            self.character_left = safe_image_load(os.path.join(base_path, "dntxh.png"))  # 당근
            self.character_right = safe_image_load(os.path.join(base_path, "dntEKd.png"))  # 양
            
            # 말풍선 이미지들
            self.speech_left = safe_image_load(os.path.join(base_path, "amazing.png"))
            self.speech_right = safe_image_load(os.path.join(base_path, "wow.png"))
            
            # 기타 이미지들
            self.gwangmyeong_image = safe_image_load(os.path.join(base_path, "gwangmyeong_x_ssulmo.png"))
            
        except Exception as e:
            print(f"결과 화면 이미지 로딩 실패: {e}")
            # 기본값으로 None 설정
            self.bg_image = None
            self.title_logo = None
            self.board_background = None
            self.character_left = None
            self.character_right = None
            self.speech_left = None
            self.speech_right = None
            self.gwangmyeong_image = None

    def enter(self):  # 스타일 통일용 훅
        pass

    def exit(self):
        pass

    # ui/result_state.py (handle_event 부분 교체)
    def handle_event(self, e: pygame.event.Event):
        if e.type != pygame.KEYDOWN:
            return
        # Enter / Keypad Enter / Space / Esc 모두 허용
        if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_ESCAPE):        
            self.next = ("title", {})
            return
        # 백업(디버그): F12 눌러도 돌아가게
        if e.key == pygame.K_F12:
            self.next = ("title", {})
            return


    def update(self, dt: float):
        self.timer += dt

    def render(self, viewport: Viewport, fonts: FontPack):
        S = viewport.S
        canvas = viewport.canvas
        
        # 배경 그리기 (화면을 완전히 채우도록 - 이미지 잘림 허용)
        if self.bg_image:
            # 원본 배경 이미지 크기
            bg_w, bg_h = self.bg_image.get_size()
            screen_w, screen_h = viewport.scaled_w, viewport.scaled_h
            
            # 화면을 완전히 채우기 위한 스케일 계산 (큰 스케일 사용)
            scale_x = screen_w / bg_w
            scale_y = screen_h / bg_h
            scale = max(scale_x, scale_y)  # 화면을 꽉 채우기 위해 큰 스케일 사용
            
            # 스케일링된 크기
            scaled_w = int(bg_w * scale)
            scaled_h = int(bg_h * scale)
            
            # 중앙 정렬을 위한 오프셋 계산
            offset_x = (screen_w - scaled_w) // 2
            offset_y = (screen_h - scaled_h) // 2
            
            # 배경 이미지 스케일링 및 그리기
            bg_scaled = pygame.transform.scale(self.bg_image, (scaled_w, scaled_h))
            canvas.blit(bg_scaled, (offset_x, offset_y))
        else:
            canvas.fill((135, 206, 235))  # 하늘색 기본 배경

        # 타이틀 로고 (8배 크기)
        if self.title_logo:
            # 원본 로고 크기
            orig_logo_w, orig_logo_h = self.title_logo.get_size()
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
            
            logo_scaled = pygame.transform.scale(self.title_logo, (logo_width, logo_height))
            logo_x = (viewport.scaled_w - logo_scaled.get_width()) // 2
            logo_y = S(-30)
            canvas.blit(logo_scaled, (logo_x, logo_y))

        # 리더보드 배경 영역 (크게)
        bg_width = min(S(1000), int(viewport.scaled_w * 0.9))
        bg_height = min(S(600), int(viewport.scaled_h * 0.9))
        bg_x = (viewport.scaled_w - bg_width) // 2
        bg_y = max(S(10), int(viewport.scaled_h * 0.1))
        bg_rect = pygame.Rect(bg_x, bg_y, bg_width, bg_height)
        
        # 리더보드 콘텐츠 영역 (배경보다 작게)
        content_width = min(S(800), int(bg_width * 0.7))
        content_height = min(S(500), int(bg_height * 0.7))
        content_x = bg_x + (bg_width - content_width) // 2
        content_y = bg_y + (bg_height - content_height) // 2
        content_rect = pygame.Rect(content_x, content_y, content_width, content_height)
        
        # 배경 그리기 (크게)
        if self.board_background:
            board_bg_scaled = pygame.transform.scale(self.board_background, (bg_rect.width, bg_rect.height))
            canvas.blit(board_bg_scaled, bg_rect)
        else:
            # 백업용 배경 (이미지 로딩 실패시)
            board_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            board_surface.fill((255, 255, 255, 230))  # 흰색 반투명
            pygame.draw.rect(board_surface, (200, 200, 200), board_surface.get_rect(), S(3))
            canvas.blit(board_surface, bg_rect)

        # 결과 내용 (콘텐츠 영역 중앙에)
        self._draw_result_content(canvas, content_rect, fonts, S)

        # 캐릭터들 (리더보드 배경 양옆에 배치)
        if self.character_left:
            char_left_scaled = pygame.transform.scale(self.character_left, (S(150), S(200)))
            char_left_x = bg_x - S(10)  # 배경 왼쪽
            char_left_y = bg_y + S(100)
            canvas.blit(char_left_scaled, (char_left_x, char_left_y))
            
            # 말풍선 이미지
            if self.speech_left:
                speech_scaled = pygame.transform.scale(self.speech_left, (S(120), S(80)))
                speech_x = char_left_x + S(130)
                speech_y = char_left_y - S(20)
                canvas.blit(speech_scaled, (speech_x, speech_y))
            
        if self.character_right:
            char_right_scaled = pygame.transform.scale(self.character_right, (S(150), S(200)))
            char_right_x = bg_x + bg_width + S(-100)  # 배경 오른쪽
            char_right_y = bg_y + S(100)
            canvas.blit(char_right_scaled, (char_right_x, char_right_y))
            
            # 말풍선 이미지
            if self.speech_right:
                speech_scaled = pygame.transform.scale(self.speech_right, (S(100), S(80)))
                speech_x = char_right_x - S(120)
                speech_y = char_right_y - S(20)
                canvas.blit(speech_scaled, (speech_x, speech_y))

        # 광명x쓸모 이미지 (오른쪽 상단)
        if self.gwangmyeong_image:
            gwang_scaled = pygame.transform.scale(self.gwangmyeong_image, (S(240), S(160)))
            gwang_x = viewport.scaled_w - S(280)
            gwang_y = S(0)
            canvas.blit(gwang_scaled, (gwang_x, gwang_y))

    def _draw_result_content(self, canvas, content_rect, fonts, S):
        """결과 내용을 그립니다."""
        # 세로 중앙 정렬을 위한 계산
        total_height = S(200)  # 대략적인 내용 높이
        start_y = content_rect.y + (content_rect.height - total_height) // 2
        
        x = content_rect.x + S(50)
        y = start_y + S(40)
        
        # 인사말
        greet_text = f"{self.player_name} 님의 결과!"
        greet_surface = fonts.h1.render(greet_text, True, (50, 50, 50))
        text_x = content_rect.x + (content_rect.width - greet_surface.get_width()) // 2
        canvas.blit(greet_surface, (text_x, y))
        y += S(80)
        
        # 기록 표시
        if self.best_fast_ms is not None:
            fast_sec = self.best_fast_ms / 1000.0
            fast_text = f"걸린 시간: {fast_sec:.2f}초"
        else:
            fast_text = "걸린 시간: 기록 없음"
        close_text = (
            "" #f"최단 거리: {self.best_close_cm:.1f} cm"
            if isinstance(self.best_close_cm, (int, float))
            else "" #"최단 거리: 기록 없음"
        )
        
        fast_surface = fonts.h2.render(fast_text, True, (50, 50, 50))
        close_surface = fonts.h2.render(close_text, True, (50, 50, 50))
        
        # 중앙 정렬
        fast_x = content_rect.x + (content_rect.width - fast_surface.get_width()) // 2
        close_x = content_rect.x + (content_rect.width - close_surface.get_width()) // 2
        
        canvas.blit(fast_surface, (fast_x, y)); y += S(50)
        canvas.blit(close_surface, (close_x, y)); y += S(60)
        
        # 안내 문구
        instruction = ""
        instruction_surface = fonts.h3.render(instruction, True, (100, 100, 100))
        instruction_x = content_rect.x + (content_rect.width - instruction_surface.get_width()) // 2
        canvas.blit(instruction_surface, (instruction_x, y))
