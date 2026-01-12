# core/fonts.py
import pygame, os, math
from .path_utils import get_asset_path, safe_font_load

class FontPack:
    def __init__(self, regular, medium, semibold, bold):
        self.regular = regular
        self.medium = medium
        self.semibold = semibold
        self.bold = bold
        # 용도별 프리셋(필요분)
        self.h1 = bold; self.h2 = semibold; self.h3 = medium; self.txt = regular

def _load(path, size): 
    return safe_font_load(path, max(10, int(round(size))))

def make_fonts(scale: float, cfg):
    # Windows와 macOS/Linux 모두에서 작동하는 경로 사용
    base = get_asset_path("fonts")
    # 새로운 폰트로 변경
    yoon_font = os.path.join(base, "YoonChildfundkoreaManSeh.ttf")
    
    # 스케일 적용 (상/하한 클램프)
    clamp = lambda s: max(12, min(120, s*scale))
    
    return FontPack(
        _load(yoon_font, clamp(cfg.TXT)),
        _load(yoon_font, clamp(cfg.H3)),
        _load(yoon_font, clamp(cfg.H2)),
        _load(yoon_font, clamp(cfg.H1)),
    )
