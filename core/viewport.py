# core/viewport.py
import pygame

class Viewport:
    def __init__(self, base_w, base_h):
        self.base_w = base_w
        self.base_h = base_h
        self.scale = 1.0
        self.scaled_w = base_w
        self.scaled_h = base_h
        self.offset = (0, 0)
        self.canvas = pygame.Surface((self.scaled_w, self.scaled_h)).convert_alpha()

    def update_layout(self, win_w, win_h):
        # 전체 화면 사용 (종횡비 제한 없음)
        self.scaled_w = win_w
        self.scaled_h = win_h
        self.scale = min(win_w / self.base_w, win_h / self.base_h)
        self.offset = (0, 0)  # 전체 화면 사용

        # ★ 전체 화면 크기로 캔버스 재생성
        self.canvas = pygame.Surface((self.scaled_w, self.scaled_h)).convert_alpha()

    # Flutter의 SizedBox처럼 쓰는 헬퍼
    def S(self, v: float) -> int:
        return int(round(v * self.scale))

    def rect(self, x, y, w, h) -> pygame.Rect:
        return pygame.Rect(self.S(x), self.S(y), self.S(w), self.S(h))

    def blit_to_window(self, window, bg=None):
        if bg:
            window.fill(bg)
        window.blit(self.canvas, self.offset)
