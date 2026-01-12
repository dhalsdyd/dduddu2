# main.py
# pip install pygame==2.5.2 opencv-python
import pygame, sys
import config as cfg
from core.viewport import Viewport
from core.fonts import make_fonts
from core.path_utils import debug_paths
from ui.title_state import TitleState
from ui.game_state import GameState
from ui.result_state import ResultState
from ui.admin_state import AdminState

def main():
    # Windows에서 경로 문제 디버깅
    if sys.platform.startswith('win'):
        debug_paths()
    
    pygame.init()

    # 창 생성 (리사이즈 가능)
    window = pygame.display.set_mode((cfg.BASE_W, cfg.BASE_H), pygame.RESIZABLE)
    pygame.display.set_caption("뚜뚜의 어드벤처")

    # 뷰포트/폰트
    viewport = Viewport(cfg.BASE_W, cfg.BASE_H)
    viewport.update_layout(*window.get_size())
    fonts = make_fonts(max(0.7, viewport.scale), cfg)
    

    # 초기 상태: 타이틀
    state = TitleState()
    state.enter()

    clock = pygame.time.Clock()
    fullscreen = False
    running = True

    while running:
        dt = clock.tick(60) / 1000.0

        # 공통 이벤트(창 제어)
    
        for e in pygame.event.get():
            handled = False
            if e.type == pygame.QUIT:
                if hasattr(state, "exit"): state.exit()
                running = False
                handled = True
            elif e.type == pygame.VIDEORESIZE:
                w = max(cfg.MIN_W, e.w); h = max(cfg.MIN_H, e.h)
                window = pygame.display.set_mode((w, h), pygame.RESIZABLE)
                viewport.update_layout(w, h)
                fonts = make_fonts(max(0.7, viewport.scale), cfg)
                handled = True
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_1:
                fullscreen = not fullscreen
                window = pygame.display.set_mode((0,0), pygame.FULLSCREEN) if fullscreen \
                        else pygame.display.set_mode((cfg.BASE_W, cfg.BASE_H), pygame.RESIZABLE)
                viewport.update_layout(*window.get_size())
                fonts = make_fonts(max(0.7, viewport.scale), cfg)
                handled = True

            if not handled:
                state.handle_event(e)   # ← 이게 핵심



        # 상태 업데이트/렌더
        state.update(dt)
        state.render(viewport, fonts)

        # --- 상태 전환 ---
        if getattr(state, "next", None):
            tag, payload = state.next
            if isinstance(state, TitleState) and tag == "game":
                player_name = payload.get("name", "")
                state.exit()
                # 카메라 인덱스는 자동으로 저장된 값 사용
                state = GameState(target_fps=30, prefer_size=(1280, 720), player_name=player_name)
                state.enter()
            elif isinstance(state, TitleState) and tag == "admin":
                state.exit()
                state = AdminState()
                state.enter()
            elif isinstance(state, GameState) and tag == "result":                
                state.exit()
                state = ResultState(
                    player_name = payload.get("name",""),
                    best_fast_ms = payload.get("best_fast_ms"),
                    best_close_cm = payload.get("best_close_cm"),
                )
                state.enter()
            elif isinstance(state, GameState) and tag == "title":
                state.exit()
                state = TitleState()
                state.enter()
            elif isinstance(state, AdminState) and tag == "title":
                state.exit()
                state = TitleState()
                state.enter()
            elif isinstance(state, ResultState) and tag == "title":
                state.exit()
                state = TitleState()
                state.enter()

        # 창에 출력 (배경색 없이)
        viewport.blit_to_window(window, bg=None)
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
