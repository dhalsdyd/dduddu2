# ui/title_state.py
import pygame
import os
from dataclasses import dataclass
from typing import Optional, List, Dict

import config as cfg
from core.viewport import Viewport
from core.fonts import FontPack
from core.leaderboard import load_scores, get_fast_board, get_close_board, save_current_player
from ui.components import draw_card, draw_table, draw_input_box
from core.path_utils import get_asset_path, safe_image_load

@dataclass
class TitleResult:
    submitted: bool
    name: Optional[str] = None

class TitleState:
    def __init__(self) -> None:
        data: List[Dict] = load_scores()
        self.fast = get_fast_board(data)
        self.close = get_close_board(data)

        self.name = ""
        self.composing = ""      # IME 조합 중 문자열
        self.cursor_on = True
        self.cursor_timer = 0.0

        self.result = TitleResult(False, None)
        self.next: Optional[tuple[str, dict]] = None  # ('result', {'name': ...}) 로 세팅

        self.input_rect = pygame.Rect(40, 540, 760, 80)
        self.left_rect  = (40, 150, 460, 360)
        self.right_rect = (500,150, 460, 360)

        self._ime_started = False
        
        # 이미지 로딩
        self._load_images()

    def _load_images(self):
        """이미지 리소스들을 로딩합니다."""
        base_path = get_asset_path("images", "title_state")
        
        try:
            # 배경 이미지
            self.bg_image = safe_image_load(os.path.join(base_path, "background.jpg"))
            
            # 타이틀 로고
            self.title_logo = safe_image_load(os.path.join(base_path, "title_adventure.png"))
            
            # 순위 아이콘들 (1-5위)
            self.rank_icons = {}
            for i in range(1, 6):
                self.rank_icons[i] = safe_image_load(os.path.join(base_path, f"rank_{i}.png"))
            
            # 캐릭터 이미지들
            self.character_left = safe_image_load(os.path.join(base_path, "carrot_character.png"))  # 당근
            self.character_right = safe_image_load(os.path.join(base_path, "tomato_character.png"))  # 양
            
            # 점수판 배경
            self.board_background = safe_image_load(os.path.join(base_path, "board_background.png"))

            self.gwangmyeong_image = safe_image_load(os.path.join(base_path, "gwangmyeong_x_ssulmo.png"))
            
        except Exception as e:
            print(f"이미지 로딩 실패: {e}")
            # 기본값으로 None 설정
            self.bg_image = None
            self.title_logo = None
            self.rank_icons = {}
            self.character_left = None
            self.character_right = None
            self.board_background = None
            self.gwangmyeong_image = None

    # --- 라이프사이클 ---
    def enter(self):
        if not self._ime_started:
            pygame.key.start_text_input()
            pygame.key.set_text_input_rect(self.input_rect)
            self._ime_started = True

    def exit(self):
        if self._ime_started:
            pygame.key.stop_text_input()
            self._ime_started = False

    # --- 이벤트 처리 ---
    def handle_event(self, e: pygame.event.Event):
        if e.type == pygame.KEYDOWN:
            # 관리자 모드 진입: Ctrl+Shift+A
            mods = e.mod
            has_shift = bool(mods & pygame.KMOD_SHIFT)
            has_ctrl = bool(mods & pygame.KMOD_CTRL)
            has_cmd = bool(mods & (pygame.KMOD_META | pygame.KMOD_LMETA | pygame.KMOD_RMETA))
            
            if e.key == pygame.K_a and has_shift and (has_ctrl or has_cmd):
                print("[ADMIN] 관리자 페이지로 진입")
                self.exit()
                self.next = ("admin", {})
                return
            
            # 1) ESC: 종료
            if e.key == pygame.K_ESCAPE:
                self.exit()
                self.result = TitleResult(False, None)

            # 2) 백스페이스: 조합 중이 아닐 때만 삭제
            elif e.key == pygame.K_BACKSPACE:
                if not self.composing and self.name:
                    self.name = self.name[:-1]

            # 3) Enter: 메인 엔터 + 키패드 엔터 모두 허용
            # ui/title_state.py (핵심 부분만 발췌)
            # ...
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                candidate = (self.name + self.composing).strip()
                if len(candidate) >= 1:
                    if self.composing:
                        self.name += self.composing
                        self.composing = ""
                    save_current_player(self.name.strip())
                    self.exit()
                    self.result = TitleResult(True, self.name.strip())
                    # ↓↓↓ 결과 대신 게임으로 진입
                    self.next = ("game", {"name": self.name.strip()})


        elif e.type == pygame.TEXTEDITING:
            # 한글 조합 중(아직 확정되지 않은 글자)
            self.composing = e.text

        elif e.type == pygame.TEXTINPUT:
            # 조합이 확정된 글자
            self.name += e.text
            self.composing = ""


    # --- 업데이트 ---
    def update(self, dt: float):
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_on = not self.cursor_on
            self.cursor_timer = 0.0

    # --- 렌더 ---

    def render(self, viewport: Viewport, fonts: FontPack):
        S = viewport.S               # 스케일 헬퍼
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

        # 타이틀 로고 (5배 크기)
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
        
        if self.gwangmyeong_image:
            gwang_scaled = pygame.transform.scale(self.gwangmyeong_image, (S(240), S(160)))
            gwang_x = viewport.scaled_w - S(280)
            gwang_y = S(0)
            canvas.blit(gwang_scaled, (gwang_x, gwang_y))

        # 리더보드 배경 영역 (크게)
        bg_width = min(S(1000), int(viewport.scaled_w * 0.9))
        bg_height = min(S(600), int(viewport.scaled_h * 0.9))
        bg_x = (viewport.scaled_w - bg_width) // 2
        bg_y = max(S(10), int(viewport.scaled_h * 0.1))
        bg_rect = pygame.Rect(bg_x, bg_y, bg_width, bg_height)
        
        # 리더보드 콘텐츠 영역 (배경보다 작게)
        content_width = min(S(800), int(bg_width * 0.7))
        content_height = min(S(500), int(bg_height * 0.7))  # 높이 증가
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

        # 리더보드 내용 (콘텐츠 영역에 맞춰서)
        self._draw_leaderboard(canvas, content_rect, fonts, S)

        # 캐릭터들 (리더보드 배경 양옆에 배치)
        if self.character_left:
            char_left_scaled = pygame.transform.scale(self.character_left, (S(150), S(200)))
            char_left_x = bg_x - S(10)  # 배경 왼쪽
            char_left_y = bg_y + S(100)
            canvas.blit(char_left_scaled, (char_left_x, char_left_y))
            
        if self.character_right:
            char_right_scaled = pygame.transform.scale(self.character_right, (S(150), S(200)))
            char_right_x = bg_x + bg_width + S(-100)  # 배경 오른쪽
            char_right_y = bg_y + S(100)
            canvas.blit(char_right_scaled, (char_right_x, char_right_y))

        # 이름 입력 박스 (리더보드 배경 아래 중앙, 리더보드 너비에 맞춤)
        input_y = bg_rect.bottom + S(-80)
        input_width = int(bg_rect.width * 0.6)  # 리더보드 너비의 60%
        input_x = (viewport.scaled_w - input_width) // 2
        input_rect = pygame.Rect(input_x, input_y, input_width, S(60))
        
        # 입력 박스 배경 (테두리 제거)
        input_surface = pygame.Surface((input_rect.width, input_rect.height), pygame.SRCALPHA)
        input_surface.fill((255, 255, 255, 200))
        canvas.blit(input_surface, input_rect)
        
        # IME 좌표 업데이트
        self.input_rect = pygame.Rect(int(input_rect.x/viewport.scale),
                                    int(input_rect.y/viewport.scale),
                                    int(input_rect.w/viewport.scale),
                                    int(input_rect.h/viewport.scale))
        
        # 입력 텍스트
        display_text = self.name + self.composing
        if not display_text:
            # 플레이스홀더
            placeholder = fonts.h3.render("닉네임 :", True, (150, 150, 150))
            canvas.blit(placeholder, (input_rect.x + S(20), input_rect.y + S(15)))
        else:
            text_surface = fonts.h3.render(display_text, True, (50, 50, 50))
            canvas.blit(text_surface, (input_rect.x + S(20), input_rect.y + S(15)))
            
            # 커서
            if self.cursor_on and not self.composing:
                cursor_x = input_rect.x + S(20) + text_surface.get_width()
                cursor_y = input_rect.y + S(15)
                pygame.draw.line(canvas, (50, 50, 50), 
                               (cursor_x, cursor_y), 
                               (cursor_x, cursor_y + fonts.h3.get_height()), S(2))

    def _draw_leaderboard(self, canvas, board_rect, fonts, S):
        """리더보드를 그립니다."""
        # 5개 행의 높이 계산
        num_rows = 5
        row_spacing = S(15)  # 행 간격
        
        # 아이콘과 박스 크기 설정 (더 큰 콘텐츠 영역에 맞춰 조정)
        icon_size = min(S(100), board_rect.height // 7)  # 크기 증가
        box_height = min(S(80), board_rect.height // 8)  # 크기 증가
        
        # 전체 콘텐츠 높이 계산 (세로 정렬을 위해 - 조금 아래로)
        total_content_height = num_rows * max(icon_size, box_height) + (num_rows - 1) * row_spacing
        start_y = board_rect.y + (board_rect.height - total_content_height) // 2 + S(15)  # 30px 아래로
        
        # 박스 너비를 리더보드 너비에 맞춰 조정
        name_box_width = int(board_rect.width * 0.35)  # 전체 너비의 35%
        score_box_width = int(board_rect.width * 0.25)  # 전체 너비의 25%
        gap = S(20)  # 요소들 간의 간격
        
        # 전체 행 너비 계산 (가로 중앙 정렬을 위해)
        total_row_width = icon_size + gap + name_box_width + gap + score_box_width
        start_x = board_rect.x + (board_rect.width - total_row_width) // 2
        
        for i, (rank, player_data) in enumerate(zip([1, 2, 3, 4, 5], self.fast[:5])):
            # 각 행의 Y 위치 (세로 중앙 정렬)
            row_height = max(icon_size, box_height)
            y_pos = start_y + i * (row_height + row_spacing)
            
            # 순위 아이콘 (가로/세로 중앙 정렬)
            if rank in self.rank_icons and self.rank_icons[rank]:
                rank_icon = pygame.transform.scale(self.rank_icons[rank], (icon_size, icon_size))
                icon_x = start_x
                icon_y = y_pos + (row_height - icon_size) // 2
                canvas.blit(rank_icon, (icon_x, icon_y))
            else:
                # 순위 아이콘이 없을 때 기본 원형 아이콘 그리기
                icon_x = start_x
                icon_y = y_pos + (row_height - icon_size) // 2
                icon_center = (icon_x + icon_size // 2, icon_y + icon_size // 2)
                pygame.draw.circle(canvas, (100, 100, 100), icon_center, icon_size // 2)
                # 순위 숫자 그리기
                rank_text = fonts.h2.render(str(rank), True, (255, 255, 255))
                rank_text_x = icon_center[0] - rank_text.get_width() // 2
                rank_text_y = icon_center[1] - rank_text.get_height() // 2
                canvas.blit(rank_text, (rank_text_x, rank_text_y))
            
            # 이름과 점수를 위한 흰색 박스들 (가로/세로 중앙 정렬)
            name_x = start_x + icon_size + gap
            score_x = name_x + name_box_width + gap
            box_y = y_pos + (row_height - box_height) // 2
            
            name_rect = pygame.Rect(name_x, box_y, name_box_width, box_height)
            score_rect = pygame.Rect(score_x, box_y, score_box_width, box_height)
            
            # 박스 그리기
            pygame.draw.rect(canvas, (255, 255, 255), name_rect)
            pygame.draw.rect(canvas, (220, 220, 220), name_rect, max(1, S(1)))
            pygame.draw.rect(canvas, (255, 255, 255), score_rect)
            pygame.draw.rect(canvas, (220, 220, 220), score_rect, max(1, S(1)))
            
            # 텍스트 (폰트 크기도 조정)
            if player_data:
                # 박스 크기에 맞는 폰트 선택
                font_to_use = fonts.txt if box_height < S(35) else fonts.h3
                
                name_text = font_to_use.render(player_data.get('name', ''), True, (50, 50, 50))
                fast_ms = player_data.get('best_fast_ms', 0)
                fast_sec = fast_ms / 1000.0 if fast_ms > 0 else 0
                score_text = font_to_use.render(f"{fast_sec:.2f}초", True, (50, 50, 50))
                
                # 중앙 정렬
                name_x_center = name_rect.x + (name_rect.width - name_text.get_width()) // 2
                name_y_center = name_rect.y + (name_rect.height - name_text.get_height()) // 2
                score_x_center = score_rect.x + (score_rect.width - score_text.get_width()) // 2
                score_y_center = score_rect.y + (score_rect.height - score_text.get_height()) // 2
                
                canvas.blit(name_text, (name_x_center, name_y_center))
                canvas.blit(score_text, (score_x_center, score_y_center))

