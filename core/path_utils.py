# core/path_utils.py
import os
import sys

def get_asset_path(*path_parts):
    """
    assets 폴더의 경로를 안전하게 생성합니다.
    Windows와 macOS/Linux 모두에서 작동합니다.
    """
    # 현재 스크립트의 디렉토리를 기준으로 assets 폴더 경로 생성
    if getattr(sys, 'frozen', False):
        # PyInstaller로 패키징된 경우
        base_path = sys._MEIPASS
    else:
        # 일반 Python 스크립트로 실행된 경우
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # assets 폴더 경로 생성
    assets_path = os.path.join(base_path, "assets")
    
    # 요청된 하위 경로들을 추가
    full_path = os.path.join(assets_path, *path_parts)
    
    # 경로 정규화 (Windows에서 \ -> / 변환 등)
    normalized_path = os.path.normpath(full_path)
    
    # Windows에서 경로가 존재하지 않을 경우 대안 경로 시도
    if not os.path.exists(normalized_path) and sys.platform.startswith('win'):
        # 현재 작업 디렉토리 기준으로 시도
        alt_path = os.path.join(os.getcwd(), "assets", *path_parts)
        alt_path = os.path.normpath(alt_path)
        if os.path.exists(alt_path):
            return alt_path
        
        # 상대 경로로 시도
        rel_path = os.path.join("assets", *path_parts)
        rel_path = os.path.normpath(rel_path)
        if os.path.exists(rel_path):
            return rel_path
    
    return normalized_path

def safe_image_load(image_path):
    """
    이미지 파일을 안전하게 로드합니다.
    파일이 없으면 None을 반환하고 에러를 출력합니다.
    """
    try:
        import pygame
        if os.path.exists(image_path):
            return pygame.image.load(image_path)
        else:
            print(f"이미지 파일을 찾을 수 없습니다: {image_path}")
            return None
    except Exception as e:
        print(f"이미지 로딩 실패: {image_path} - {e}")
        return None

def safe_font_load(font_path, size):
    """
    폰트 파일을 안전하게 로드합니다.
    파일이 없으면 기본 폰트를 반환합니다.
    """
    try:
        import pygame
        if os.path.exists(font_path):
            return pygame.font.Font(font_path, size)
        else:
            print(f"폰트 파일을 찾을 수 없습니다: {font_path}")
            # 기본 폰트 반환
            return pygame.font.Font(None, size)
    except Exception as e:
        print(f"폰트 로딩 실패: {font_path} - {e}")
        # 기본 폰트 반환
        return pygame.font.Font(None, size)

def debug_paths():
    """
    디버깅을 위해 현재 경로 정보를 출력합니다.
    """
    print("=== 경로 디버깅 정보 ===")
    print(f"현재 작업 디렉토리: {os.getcwd()}")
    print(f"스크립트 위치: {os.path.abspath(__file__)}")
    print(f"Python 실행 파일: {sys.executable}")
    print(f"Python 경로: {sys.path}")
    
    # assets 폴더 경로들 시도
    test_paths = [
        get_asset_path(),
        os.path.join(os.getcwd(), "assets"),
        os.path.join("assets"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
    ]
    
    print("\n=== Assets 폴더 경로 테스트 ===")
    for i, path in enumerate(test_paths):
        exists = os.path.exists(path)
        print(f"경로 {i+1}: {path} - {'존재함' if exists else '존재하지 않음'}")
        if exists:
            try:
                contents = os.listdir(path)
                print(f"  내용: {contents[:5]}...")  # 처음 5개만 표시
            except Exception as e:
                print(f"  읽기 오류: {e}")
    
    print("=== 경로 디버깅 완료 ===\n")
