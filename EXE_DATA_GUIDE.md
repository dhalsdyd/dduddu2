# 🎮 EXE 파일 데이터 저장 가이드

## 📋 문제 상황

PyInstaller로 만든 EXE 파일은 **임시 폴더**에 압축이 풀려서 실행됩니다.

- JSON 파일을 현재 디렉토리에 저장하면 **임시 폴더**에 저장됨
- EXE 종료 시 임시 폴더가 삭제될 수 있음
- 사용자 데이터가 유실됨 ❌

---

## ✅ 해결 방법: 사용자 디렉토리 사용

### 저장 위치

| OS          | 데이터 저장 위치                            |
| ----------- | ------------------------------------------- |
| **Windows** | `C:\Users\사용자명\AppData\Roaming\dduddu\` |
| **macOS**   | `~/Library/Application Support/dduddu/`     |
| **Linux**   | `~/.config/dduddu/`                         |

### 저장되는 파일

```
dduddu/
├── settings.json       # 카메라/시리얼 설정
├── leaderboard.json    # 리더보드 데이터
└── session.json        # 세션 정보
```

---

## 🔧 구현 내용

### 1. core/settings.py

```python
def get_user_data_dir() -> Path:
    """사용자 데이터 디렉토리 경로 반환"""
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
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir
```

### 2. 모든 JSON 파일이 사용자 디렉토리 사용

- ✅ `settings.json` → 사용자 디렉토리
- ✅ `leaderboard.json` → 사용자 디렉토리
- ✅ `session.json` → 사용자 디렉토리

---

## 💡 장점

### 1. 데이터 영속성 ✅

- EXE 종료 후에도 데이터 유지
- 업데이트 후에도 데이터 보존

### 2. 다중 사용자 지원 ✅

- 각 사용자마다 독립적인 데이터
- 권한 문제 없음

### 3. 표준 규약 준수 ✅

- OS별 표준 위치 사용
- 다른 앱들과 일관성

### 4. 백업 용이 ✅

- 명확한 위치
- 쉬운 백업/복원

---

## 📁 데이터 관리

### Windows에서 데이터 위치 찾기

1. **탐색기 열기**
2. 주소창에 입력: `%APPDATA%\dduddu`
3. Enter

또는 명령 프롬프트:

```cmd
cd %APPDATA%\dduddu
dir
```

### macOS에서 데이터 위치 찾기

터미널에서:

```bash
cd ~/Library/Application\ Support/dduddu
ls -la
```

Finder에서:

1. Finder 열기
2. `Cmd + Shift + G`
3. 입력: `~/Library/Application Support/dduddu`

### Linux에서 데이터 위치 찾기

터미널에서:

```bash
cd ~/.config/dduddu
ls -la
```

---

## 🔄 데이터 백업/복원

### 백업

**Windows**:

```cmd
xcopy %APPDATA%\dduddu D:\backup\dduddu /E /I
```

**macOS/Linux**:

```bash
cp -r ~/Library/Application\ Support/dduddu ~/backup/dduddu
# 또는 Linux
cp -r ~/.config/dduddu ~/backup/dduddu
```

### 복원

**Windows**:

```cmd
xcopy D:\backup\dduddu %APPDATA%\dduddu /E /I
```

**macOS/Linux**:

```bash
cp -r ~/backup/dduddu ~/Library/Application\ Support/dduddu
# 또는 Linux
cp -r ~/backup/dduddu ~/.config/dduddu
```

---

## 🧪 테스트 방법

### 1. 일반 실행으로 테스트

```bash
python main.py
```

- 데이터가 사용자 디렉토리에 저장되는지 확인
- 파일 위치 로그 확인: `[SETTINGS] 설정 저장 완료: /path/to/...`

### 2. EXE로 빌드하여 테스트

```bash
python build_exe.py
```

1. 생성된 EXE 실행
2. 관리자 페이지에서 설정 변경
3. EXE 종료
4. 데이터 디렉토리 확인
5. EXE 재실행하여 설정 유지 확인

### 3. 다른 위치에서 실행 테스트

1. EXE를 다른 폴더로 복사
2. 해당 위치에서 실행
3. 동일한 데이터 사용하는지 확인

---

## 🚨 문제 해결

### 데이터가 저장 안 돼요

**원인**: 권한 문제

**해결**:

```bash
# Windows (관리자 권한으로 cmd 실행)
icacls "%APPDATA%\dduddu" /grant %USERNAME%:F /T

# macOS/Linux
chmod -R 755 ~/Library/Application\ Support/dduddu
# 또는
chmod -R 755 ~/.config/dduddu
```

### 데이터가 두 곳에 저장돼요

**원인**: 이전 버전 사용 시 현재 디렉토리에 저장된 파일

**해결**:

1. 프로젝트 폴더의 JSON 파일 삭제:

```bash
rm settings.json leaderboard.json session.json
```

2. 사용자 디렉토리만 사용

### 데이터 위치를 확인하고 싶어요

관리자 페이지에서 설정 저장 시 로그 확인:

```
[SETTINGS] 설정 저장 완료: C:\Users\사용자명\AppData\Roaming\dduddu\settings.json
```

또는 Python으로 확인:

```python
from core.settings import get_user_data_dir
print(get_user_data_dir())
```

---

## 📊 파일 구조

### 개발 환경 (Python 실행)

```
프로젝트/
├── main.py
├── config.py
└── (JSON 파일 없음 - 사용자 디렉토리 사용)

사용자 디렉토리/
└── dduddu/
    ├── settings.json
    ├── leaderboard.json
    └── session.json
```

### 배포 환경 (EXE 실행)

```
배포용/
└── 뚜뚜의어드벤처.exe

사용자 디렉토리/
└── dduddu/
    ├── settings.json
    ├── leaderboard.json
    └── session.json
```

---

## 🎯 최종 확인 사항

### EXE 빌드 전

- [ ] `core/settings.py`에서 `get_user_data_dir()` 함수 확인
- [ ] `config.py`에서 DATA_FILE, SESSION_FILE이 사용자 디렉토리 사용
- [ ] Python 실행으로 데이터 저장 테스트

### EXE 빌드 후

- [ ] EXE 실행
- [ ] 관리자 페이지에서 설정 변경
- [ ] 사용자 디렉토리에 파일 생성 확인
- [ ] EXE 종료 후 재실행하여 데이터 유지 확인

### 배포 전

- [ ] 다른 컴퓨터에서 테스트
- [ ] 여러 위치에서 EXE 실행 테스트
- [ ] 데이터 백업/복원 테스트

---

## 💻 코드 예시

### 데이터 위치 확인 코드

```python
# test_data_location.py
from core.settings import get_user_data_dir

print("="*50)
print("데이터 저장 위치")
print("="*50)
print(f"디렉토리: {get_user_data_dir()}")
print()
print("파일 목록:")
data_dir = get_user_data_dir()
if data_dir.exists():
    for file in data_dir.iterdir():
        size = file.stat().st_size if file.is_file() else "-"
        print(f"  - {file.name} ({size} bytes)")
else:
    print("  (디렉토리가 아직 생성되지 않았습니다)")
```

실행:

```bash
python test_data_location.py
```

---

## 🌟 추가 팁

### 포터블 모드 (선택사항)

만약 USB 메모리에서 실행하고 데이터도 같이 저장하고 싶다면:

```python
# core/settings.py에서 수정
def get_user_data_dir() -> Path:
    # portable.txt 파일이 있으면 현재 디렉토리 사용
    portable_marker = Path("portable.txt")
    if portable_marker.exists():
        return Path(".")

    # 기존 코드...
```

사용법:

1. EXE와 같은 폴더에 `portable.txt` 빈 파일 생성
2. 데이터가 EXE와 같은 폴더에 저장됨

---

**이제 EXE 파일로 배포해도 사용자 데이터가 안전하게 저장됩니다! 🎉**
