# core/settings.py
# 게임 설정 저장 및 로드
import json
import os
import sys
from pathlib import Path

def get_user_data_dir() -> Path:
    """
    사용자 데이터 디렉토리 경로 반환
    EXE 실행 시에도 사용자 홈 디렉토리에 저장
    """
    if sys.platform == "win32":
        # Windows: %APPDATA%/dduddu
        base_dir = Path(os.getenv("APPDATA", os.path.expanduser("~")))
    elif sys.platform == "darwin":
        # macOS: ~/Library/Application Support/dduddu
        base_dir = Path.home() / "Library" / "Application Support"
    else:
        # Linux: ~/.config/dduddu
        base_dir = Path.home() / ".config"
    
    data_dir = base_dir / "dduddu"
    
    # 디렉토리 생성
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[SETTINGS] 데이터 디렉토리 생성 실패: {e}")
        # 폴백: 현재 디렉토리 사용
        data_dir = Path(".")
    
    return data_dir

SETTINGS_FILE = get_user_data_dir() / "settings.json"

def load_settings() -> dict:
    """설정 파일 로드"""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[SETTINGS] 설정 로드 실패: {e}")
            return {}
    return {}

def save_settings(settings: dict):
    """설정 파일 저장"""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        print(f"[SETTINGS] 설정 저장 완료: {SETTINGS_FILE}")
    except Exception as e:
        print(f"[SETTINGS] 설정 저장 실패: {e}")

def get_camera_index() -> int:
    """저장된 카메라 인덱스 가져오기"""
    settings = load_settings()
    return settings.get("camera_index", 0)

def set_camera_index(index: int):
    """카메라 인덱스 저장"""
    settings = load_settings()
    settings["camera_index"] = index
    save_settings(settings)
    print(f"[SETTINGS] 카메라 인덱스 저장: {index}")

def get_serial_port() -> str:
    """저장된 시리얼 포트 가져오기"""
    settings = load_settings()
    return settings.get("serial_port", None)

def set_serial_port(port: str):
    """시리얼 포트 저장"""
    settings = load_settings()
    settings["serial_port"] = port
    save_settings(settings)
    print(f"[SETTINGS] 시리얼 포트 저장: {port}")
