# 뚜뚜의 어드벤처 - 설치 및 사용 메뉴얼

## 📖 프로젝트 소개

"뚜뚜의 어드벤처"는 초음파 센서를 이용한 인터랙티브 게임입니다. 플레이어가 센서 앞에서 손을 움직이면 게임이 반응하여 점수를 얻을 수 있습니다.

### 🎮 게임 특징

- **초음파 센서 연동**: 실제 물리적 움직임으로 게임 조작
- **실시간 반응**: 센서가 감지하는 거리에 따라 게임 진행
- **점수 시스템**: 빠른 반응과 정확한 거리 측정으로 점수 획득
- **리더보드**: 최고 기록 저장 및 확인

---

## 🛠️ 설치 가이드 (Windows)

### 1단계: Python 설치

1. **Python 다운로드**

   - [Python 공식 웹사이트](https://www.python.org/downloads/) 접속
   - "Download Python" 버튼 클릭 (최신 버전 권장)
   - 다운로드된 설치 파일 실행

2. **설치 과정**

   - ✅ "Add Python to PATH" 체크박스 반드시 선택
   - "Install Now" 클릭
   - 설치 완료 후 "Close" 클릭

3. **설치 확인**
   - 명령 프롬프트(cmd) 열기
   - 다음 명령어 입력:
   ```cmd
   python --version
   ```
   - Python 버전이 표시되면 설치 성공

### 2단계: 필요한 라이브러리 설치

1. **명령 프롬프트에서 프로젝트 폴더로 이동**

   ```cmd
   cd C:\Users\[사용자이름]\Downloads\dduddu
   ```

2. **필요한 라이브러리 설치**
   ```cmd
   pip install pygame==2.5.2 opencv-python pyserial
   ```

### 3단계: Arduino IDE 설치

1. **Arduino IDE 다운로드**

   - [Arduino 공식 웹사이트](https://www.arduino.cc/en/software) 접속
   - "Arduino IDE" 다운로드
   - 설치 파일 실행

2. **설치 과정**
   - 기본 설정으로 "Next" 클릭
   - 설치 완료 후 "Close" 클릭

### 4단계: 하드웨어 준비

#### 필요한 부품

- Arduino Uno (또는 호환 보드)
- HC-SR04 초음파 센서
- 점퍼 와이어 4개

#### 연결 방법

```
HC-SR04 센서    →    Arduino
VCC (전원)      →    5V
GND (접지)      →    GND
TRIG (트리거)   →    Pin 9
ECHO (에코)     →    Pin 10
```

### 5단계: Arduino 코드 업로드

1. **Arduino IDE 실행**

2. **코드 파일 열기**

   - `test/ultrasonic_arduino.ino` 파일을 Arduino IDE에서 열기

3. **보드 설정**

   - Tools → Board → Arduino Uno 선택
   - Tools → Port → Arduino가 연결된 COM 포트 선택

4. **코드 업로드**
   - 상단의 화살표 버튼(→) 클릭
   - "Upload completed" 메시지 확인

---

## 🎮 게임 실행 방법

### 1. 기본 실행 (센서 없이)

```cmd
python main.py
```

### 2. 센서 연결 후 실행

1. Arduino를 USB로 컴퓨터에 연결
2. 센서가 올바르게 연결되었는지 확인
3. 게임 실행:
   ```cmd
   python main.py
   ```

---

## 🎯 게임 플레이 방법

### 게임 화면 구성

1. **타이틀 화면**: 게임 시작 및 설정
2. **게임 화면**: 실제 플레이 영역
3. **결과 화면**: 점수 확인 및 리더보드

### 조작 방법

- **마우스**: 메뉴 선택, 버튼 클릭
- **키보드**:
  - `F11`: 전체화면 전환
  - `ESC`: 게임 종료
- **초음파 센서**: 손을 센서 앞에서 움직여 게임 조작

### 게임 규칙

1. 센서 앞에 손을 가져가면 게임 시작
2. 화면의 지시에 따라 손을 움직임
3. 빠르고 정확한 반응으로 높은 점수 획득
4. 최고 기록은 자동으로 저장됨

---

## 🔧 문제 해결

### Python 관련 문제

**Q: "python은 내부 또는 외부 명령이 아닙니다" 오류**

- Python이 PATH에 추가되지 않았습니다
- Python을 재설치하고 "Add Python to PATH" 옵션을 선택하세요

**Q: "pip는 내부 또는 외부 명령이 아닙니다" 오류**

- Python 설치 후 명령 프롬프트를 재시작하세요
- 또는 다음 명령어로 pip 설치:
  ```cmd
  python -m ensurepip --upgrade
  ```

### 라이브러리 설치 문제

**Q: "Microsoft Visual C++ 14.0 is required" 오류**

- [Microsoft Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) 다운로드 및 설치

**Q: 특정 라이브러리 설치 실패**

- 관리자 권한으로 명령 프롬프트 실행 후 재시도
- 또는 가상환경 사용:
  ```cmd
  python -m venv venv
  venv\Scripts\activate
  pip install pygame==2.5.2 opencv-python pyserial
  ```

### Arduino 관련 문제

**Q: Arduino가 인식되지 않음**

- USB 케이블 교체
- 다른 USB 포트 시도
- Arduino 드라이버 재설치

**Q: 코드 업로드 실패**

- 올바른 보드와 포트 선택 확인
- Arduino 재부팅
- 다른 USB 케이블 사용

### 센서 관련 문제

**Q: 센서가 거리를 측정하지 않음**

- 연결 상태 확인
- 센서 표면에 장애물이 없는지 확인
- 측정 범위 내에 물체가 있는지 확인 (2cm~400cm)

**Q: 측정값이 부정확함**

- 센서 표면을 깨끗이 닦기
- 주변 환경의 간섭 확인
- 센서 위치 조정

---

## 📁 프로젝트 구조

```
dduddu/
├── main.py              # 메인 게임 실행 파일
├── config.py            # 게임 설정 파일
├── assets/              # 게임 리소스 (이미지, 폰트)
├── core/                # 핵심 기능 모듈
├── ui/                  # 사용자 인터페이스
├── test/                # Arduino 테스트 코드
└── README.md           # 이 메뉴얼
```

---

## 🆘 추가 도움말

### 기술 지원

- 문제가 발생하면 오류 메시지를 정확히 기록
- 하드웨어 연결 상태 사진 첨부
- 사용 중인 운영체제와 Python 버전 명시

### 개발자 정보

- 이 프로젝트는 Python과 Arduino를 활용한 인터랙티브 게임입니다
- 초음파 센서를 통한 물리적 인터랙션을 구현했습니다

---

## 📝 라이센스

이 프로젝트는 교육 목적으로 제작되었습니다.

---

**즐거운 게임 되세요! 🎮**
