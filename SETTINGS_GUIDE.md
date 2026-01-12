# 🎮 게임 설정 자동 저장

## 📋 개요

관리자 페이지에서 설정한 카메라 인덱스와 시리얼 포트가 자동으로 저장되어, 다음 게임 실행 시 동일한 설정이 적용됩니다.

---

## ✨ 자동 저장되는 설정

### 1. 카메라 인덱스

- **저장 시점**: 관리자 페이지 > 카메라 탭에서 연결 성공 시
- **사용 시점**: 게임 시작 시 자동으로 저장된 인덱스 사용
- **기본값**: 0

### 2. 시리얼 포트

- **저장 시점**: 관리자 페이지 > 시리얼 탭에서 연결 성공 시
- **사용 시점**: 게임 시작 시 자동으로 저장된 포트 사용
- **기본값**: None (자동 탐지)

---

## 🔧 사용 방법

### 최초 설정 (한 번만)

1. **관리자 페이지 진입**

   - 타이틀 화면에서 `Ctrl+Shift+A` (macOS: `Cmd+Shift+A`)

2. **카메라 설정**

   - `2` 키로 카메라 탭 이동
   - `0-9` 키로 작동하는 카메라 인덱스 찾기
   - 연결 성공 시 자동으로 저장됨 ✅

3. **센서 설정** (선택사항)

   - `1` 키로 시리얼 탭 이동
   - `C` 키로 연결 시도
   - 연결 성공 시 자동으로 저장됨 ✅

4. **게임 시작**
   - `ESC`로 타이틀로 돌아가기
   - 저장된 설정으로 게임 자동 시작!

### 이후 실행

- 저장된 설정이 자동으로 적용됨
- 설정 변경이 필요할 때만 관리자 페이지 진입

---

## 📁 설정 파일

### settings.json

모든 설정이 이 파일에 저장됩니다.

**위치**: 프로젝트 루트 디렉토리

**내용 예시**:

```json
{
  "camera_index": 1,
  "serial_port": "/dev/tty.usbmodem1101"
}
```

### 파일 관리

#### 설정 확인

```bash
cat settings.json
```

#### 설정 초기화

```bash
rm settings.json
```

다음 실행 시 기본값으로 시작됩니다.

#### 수동 편집

```json
{
  "camera_index": 2,
  "serial_port": "COM3"
}
```

---

## 💡 작동 원리

### 설정 저장 흐름

```
관리자 페이지
  └─> 카메라 연결 성공
       └─> settings.json에 인덱스 저장
            └─> 게임 시작 시 자동 로드
```

### 코드 구조

1. **core/settings.py**

   - 설정 저장/로드 함수 제공
   - `get_camera_index()`: 저장된 인덱스 가져오기
   - `set_camera_index(index)`: 인덱스 저장하기

2. **ui/admin_state.py**

   - 카메라 연결 성공 시 `set_camera_index()` 호출
   - 시리얼 연결 성공 시 `set_serial_port()` 호출

3. **ui/game_state.py**
   - 초기화 시 `get_camera_index()` 호출
   - 저장된 값이 없으면 기본값(0) 사용

---

## 🎯 사용 예시

### 시나리오 1: 외장 웹캠 사용

**문제**: 외장 웹캠이 인덱스 1에 있음

**해결**:

```
1. Ctrl+Shift+A로 관리자 페이지
2. '2'로 카메라 탭
3. '1' 키 눌러 인덱스 1 선택
4. 연결 확인 → 자동 저장! ✅
5. 이후 게임 실행 시 항상 인덱스 1 사용
```

### 시나리오 2: 컴퓨터마다 다른 설정

**컴퓨터 A**: 내장 웹캠 (인덱스 0)
**컴퓨터 B**: 외장 웹캠 (인덱스 2)

**해결**:

- 각 컴퓨터에서 한 번씩만 관리자 페이지에서 설정
- 이후 자동으로 해당 컴퓨터의 설정 사용
- `settings.json` 파일만 복사하면 설정도 복사됨

### 시나리오 3: 게임 데모/전시

**준비**:

```bash
# 설정 파일 백업
cp settings.json settings.backup.json
```

**전시 중**:

- 자동으로 저장된 설정 사용
- 관리자 페이지로 현장에서 즉시 조정 가능

**정리**:

```bash
# 설정 복원
cp settings.backup.json settings.json
```

---

## ⚙️ 고급 설정

### 기본 카메라 인덱스 변경

**config.py**에서 전역 기본값 설정 가능 (하지만 settings.json이 우선):

```python
# config.py
DEFAULT_CAMERA_INDEX = 1  # 외장 웹캠
```

### 프로그래밍 방식으로 설정

```python
from core.settings import set_camera_index, set_serial_port

# 카메라 인덱스 설정
set_camera_index(2)

# 시리얼 포트 설정
set_serial_port("/dev/tty.usbmodem1101")
```

---

## 🔍 문제 해결

### 설정이 저장 안 돼요

**원인**: 파일 쓰기 권한 문제

**해결**:

```bash
# 권한 확인
ls -l settings.json

# 권한 부여 (macOS/Linux)
chmod 644 settings.json
```

### 잘못된 설정이 저장됐어요

**해결**:

```bash
# 1. 설정 파일 삭제
rm settings.json

# 2. 게임 재시작
python main.py

# 3. 관리자 페이지에서 다시 설정
```

### 여러 컴퓨터에서 다른 설정 필요해요

**해결**: 각 컴퓨터마다 별도의 `settings.json` 유지

```bash
# 컴퓨터 A
cp settings.json settings_computerA.json

# 컴퓨터 B
cp settings.json settings_computerB.json

# 필요시 복사해서 사용
cp settings_computerA.json settings.json
```

---

## 📊 설정 파일 구조

### 완전한 예시

```json
{
  "camera_index": 1,
  "serial_port": "/dev/tty.usbmodem1101",
  "last_updated": "2026-01-11T10:30:00"
}
```

### 최소 구성

```json
{
  "camera_index": 0
}
```

### Windows 예시

```json
{
  "camera_index": 0,
  "serial_port": "COM3"
}
```

### macOS 예시

```json
{
  "camera_index": 1,
  "serial_port": "/dev/tty.usbmodem1101"
}
```

---

## ✅ 체크리스트

### 최초 설정 시

- [ ] 관리자 페이지 진입 (`Ctrl+Shift+A`)
- [ ] 카메라 탭에서 작동하는 인덱스 찾기
- [ ] 연결 성공 확인 (초록색 "연결됨" 표시)
- [ ] 시리얼 탭에서 센서 연결 (선택사항)
- [ ] 타이틀로 돌아가기 (`ESC`)
- [ ] 게임 실행하여 설정 적용 확인

### 설정 변경 시

- [ ] 관리자 페이지 진입
- [ ] 새 설정 적용
- [ ] 연결 확인
- [ ] 게임에서 테스트

---

**설정이 자동으로 저장되어 매번 설정할 필요가 없습니다! 🎉**
