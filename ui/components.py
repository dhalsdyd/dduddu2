# ui/components.py
# 반응형(스케일) 지원 UI 컴포넌트 모음
import pygame
from typing import List, Dict

import config as cfg

# ----- 유틸 -----
def _scale_from_rect(rect: pygame.Rect, base_h: int = 360) -> float:
    """카드/섹션 높이를 기준으로 대략적 스케일을 추정"""
    return max(0.5, min(2.5, rect.height / float(base_h)))

def _S(v: float, s: float) -> int:
    """길이 스케일 후 int로 스냅"""
    return int(round(v * s))

def _ellipsize(text: str, font: pygame.font.Font, max_w: int) -> str:
    if not text:
        return ""
    if font.size(text)[0] <= max_w:
        return text
    ell = "…"
    w_ell = font.size(ell)[0]
    lo, hi = 0, len(text)
    # 이진 탐색으로 잘라내기
    while lo < hi:
        mid = (lo + hi) // 2
        if font.size(text[:mid])[0] + w_ell <= max_w:
            lo = mid + 1
        else:
            hi = mid
    return text[:max(0, lo - 1)] + ell

# ----- 카드 -----
def draw_card(surf: pygame.Surface, rect: pygame.Rect, title: str, font_h2: pygame.font.Font):
    s = _scale_from_rect(rect)
    radius = _S(16, s)
    border = max(1, _S(2, s))
    pad_x = _S(20, s)
    pad_top = _S(16, s)
    title_rule_y = rect.y + _S(62, s)

    pygame.draw.rect(surf, cfg.CARD, rect, border_radius=radius)
    pygame.draw.rect(surf, cfg.LINE, rect, width=border, border_radius=radius)

    # Title
    title_surf = font_h2.render(title, True, cfg.TEXT)
    surf.blit(title_surf, (rect.x + pad_x, rect.y + pad_top))

    # Title underline
    pygame.draw.line(
        surf,
        cfg.LINE,
        (rect.x + _S(18, s), title_rule_y + _S(16, s)),
        (rect.right - _S(18, s), title_rule_y + _S(16, s)),
        border,
    )

# ----- 테이블 -----
def draw_table(
    surf: pygame.Surface,
    rect: pygame.Rect,
    headers: List[str],
    rows: List[Dict],
    col_w: List[int],
    font_h3: pygame.font.Font,
    font_txt: pygame.font.Font,
):
    s = _scale_from_rect(rect)
    pad_x = _S(20, s)
    head_top = rect.y + _S(78, s)      # 헤더 y
    row_top = rect.y + _S(112, s)      # 본문 시작 y
    row_gap = _S(34, s)
    # 컬럼 x 시작들
    col_x = [rect.x + pad_x]
    for i in range(1, len(col_w)):
        col_x.append(col_x[-1] + col_w[i - 1])

    # 헤더
    for i, head in enumerate(headers):
        surf.blit(font_h3.render(head, True, cfg.SUBT), (col_x[i], head_top))

    # 행들
    y = row_top
    for idx, r in enumerate(rows, start=1):
        if y > rect.bottom - _S(20, s):
            break

        # 값 준비
        if "Fast" in headers[-1]:
            fast_ms = r.get("best_fast_ms", "-")
            if fast_ms != "-" and fast_ms is not None:
                fast_sec = fast_ms / 1000.0
                last_str = f"{fast_sec:.2f}초"
            else:
                last_str = "-"
        else:
            val = r.get("best_close_cm", "-")
            last_str = f"{val} cm" if isinstance(val, (int, float)) else str(val)

        vals = [str(idx), r.get("name", "-"), str(last_str)]
        # 각 컬럼 그리기 (폭 내 말줄임)
        for i, val in enumerate(vals):
            txt = _ellipsize(val, font_txt, max(10, col_w[i] - _S(8, s)))
            surf.blit(font_txt.render(txt, True, cfg.TEXT), (col_x[i], y))

        y += row_gap

# ----- 입력 박스 -----
def draw_input_box(
    surf: pygame.Surface,
    rect: pygame.Rect,
    label: str,
    text: str,
    cursor_on: bool,
    composing: str,
    font_h2: pygame.font.Font,
    font_h3: pygame.font.Font,
    font_txt: pygame.font.Font,
    *,
    text_align: str = "left",
    placeholder_align: str = "center",
):
    s = _scale_from_rect(rect, base_h=84)
    radius = _S(12, s)
    border = max(1, _S(2, s))
    pad_x = _S(16, s)
    pad_y = _S(12, s)

    # 배경 (테두리 제거)
    pygame.draw.rect(surf, cfg.CARD, rect, border_radius=radius)

    # 라벨
    label_pos = (rect.x + pad_x, rect.y - _S(48, s))
    surf.blit(font_h3.render(label, True, cfg.SUBT), label_pos)

    # ===== 입력 텍스트 =====
    shown = text if text else ""
    text_surf = font_h2.render(shown, True, cfg.TEXT)

    # 정렬 계산
    def _aligned_x(w: int, align: str) -> int:
        if align == "center":
            return rect.x + (rect.w - w) // 2
        if align == "right":
            return rect.right - pad_x - w
        return rect.x + pad_x  # left

    text_x = _aligned_x(text_surf.get_width(), text_align)
    text_y = rect.y + pad_y

    # 본문 텍스트 렌더 (문자 있는 경우만)
    if shown:
        surf.blit(text_surf, (text_x, text_y))

    # ===== 조합(IME) 중 문자열 or 커서 =====
    if composing:
        comp_surf = font_h2.render(composing, True, cfg.ACC)
        cx = text_x + (text_surf.get_width() if shown else 0)
        cy = text_y
        surf.blit(comp_surf, (cx, cy))
        pygame.draw.line(
            surf, cfg.ACC,
            (cx, cy + text_surf.get_height()),
            (cx + comp_surf.get_width(), cy + text_surf.get_height()),
            max(1, _S(2, s)),
        )
    else:
        if cursor_on and shown:
            cx = text_x + text_surf.get_width() + _S(2, s)
            cy = text_y - _S(2, s)
            pygame.draw.rect(
                surf, cfg.ACC,
                (cx, cy, _S(3, s), text_surf.get_height() + _S(4, s)),
                border_radius=_S(2, s),
            )

    # ===== 플레이스홀더(힌트) – 비어 있을 때 중앙 정렬 =====
    if (not shown) and (not composing):
        hint = "이름을 입력하고 Enter를 누르세요"
        hint_surf = font_txt.render(hint, True, (140, 150, 160))

        if placeholder_align == "center":
            hx = rect.x + (rect.w - hint_surf.get_width()) // 2
            hy = rect.y + (rect.h - hint_surf.get_height()) // 2
        else:
            # left/right도 선택 가능
            hx = _aligned_x(hint_surf.get_width(), placeholder_align)
            hy = rect.y + (rect.h - hint_surf.get_height()) // 2

        surf.blit(hint_surf, (hx, hy))
