# 초음파 센서 시리얼 테스트

HC-SR04 초음파 센서를 사용하여 거리를 측정하고 시리얼 통신으로 데이터를 전송하는 테스트 코드입니다.

## 하드웨어 구성

### 필요한 부품

- Arduino Uno (또는 호환 보드)
- HC-SR04 초음파 센서
- 점퍼 와이어

### 연결 방법

```
HC-SR04    Arduino
VCC    →   5V
GND    →   GND
TRIG   →   Pin 9
ECHO   →   Pin 10
```

## 파일 설명

### 1. `ultrasonic_arduino.ino`

Arduino 스케치 파일입니다.

**주요 기능:**

- 100ms 간격으로 초음파 센서 측정
- 게임 프로젝트 호환 데이터 형식 지원
- JSON 형식으로 데이터 전송
- 근접 감지 기능 (5cm 이하)
- 시리얼 명령 처리 (ping, status, measure, near, interval 변경, format 변경)

**설정 가능한 매개변수:**

- `MEASURE_INTERVAL`: 측정 간격 (기본값: 100ms)
- `MAX_DISTANCE`: 최대 측정 거리 (기본값: 400cm)
- `MIN_DISTANCE`: 최소 측정 거리 (기본값: 2cm)
- `NEAR_THRESHOLD`: 근접 감지 임계값 (기본값: 5cm)
- `USE_GAME_FORMAT`: 게임 프로젝트 형식 사용 (기본값: true)
- `USE_JSON_FORMAT`: JSON 형식 사용 (기본값: true)

### 2. `pyserial_test.py`

Python 테스트 프로그램입니다.

**주요 기능:**

- 자동 포트 감지 및 연결
- JSON 데이터 파싱
- 실시간 데이터 모니터링
- 연결 상태 확인

## 사용 방법

### 1. Arduino 코드 업로드

1. Arduino IDE에서 `ultrasonic_arduino.ino` 파일을 엽니다.
2. Arduino 보드에 업로드합니다.
3. 시리얼 모니터에서 초기화 메시지를 확인합니다.

### 2. Python 테스트 실행

```bash
# 필요한 라이브러리 설치
pip install pyserial

# 테스트 실행
python pyserial_test.py
```

### 3. 시리얼 명령어

Arduino에 다음 명령어를 시리얼로 전송할 수 있습니다:

- `ping`: 연결 상태 확인
- `status`: 현재 상태 정보
- `measure`: 즉시 측정 실행
- `near`: 근접 신호 강제 전송
- `interval:500`: 측정 간격을 500ms로 변경
- `format:game`: 게임 프로젝트 형식으로 변경
- `format:test`: 테스트 형식으로 변경

## 데이터 형식

### JSON 형식 (게임 프로젝트 호환)

```json
{
  "cm": 25
}
```

### 근접 감지 형식

```json
{
  "near": true,
  "cm": 4
}
```

### 테스트 형식

```json
{
  "distance": 25,
  "timestamp": 12345,
  "unit": "cm"
}
```

### 상태 메시지

```json
{
  "status": "ready",
  "message": "Ultrasonic sensor initialized"
}
```

## 문제 해결

### 1. 포트 연결 실패

- Arduino가 올바르게 연결되었는지 확인
- USB 케이블 상태 확인
- 다른 프로그램에서 포트를 사용 중인지 확인

### 2. 측정값이 -1로 나오는 경우

- 센서 연결 상태 확인
- 측정 범위 내에 물체가 있는지 확인
- 센서 표면에 장애물이 없는지 확인

### 3. 데이터가 수신되지 않는 경우

- 통신 속도(baudrate) 확인 (기본값: 9600)
- 시리얼 케이블 상태 확인
- Arduino 재부팅

## 추가 기능

### 게임 프로젝트 호환성

이 Arduino 코드는 기존 게임 프로젝트와 완전히 호환됩니다:

- **데이터 형식**: `{"cm": 25}` 형식으로 거리 전송
- **근접 감지**: `{"near": true, "cm": 4}` 형식으로 근접 신호 전송
- **통신 속도**: 9600 baud (게임 프로젝트와 동일)
- **자동 포트 감지**: macOS에서 USB 시리얼 포트 자동 찾기

### 상세 데이터 전송

Arduino 코드에서 `sendDetailedData()` 함수를 사용하면 추가 정보를 포함한 데이터를 전송할 수 있습니다:

```json
{
  "distance": 25,
  "timestamp": 12345,
  "unit": "cm",
  "voltage": 4.8,
  "free_memory": 1024
}
```

### 측정 간격 조정

Python에서 측정 간격을 동적으로 조정할 수 있습니다:

```python
# 시리얼로 명령 전송
serial_conn.write("interval:200\n".encode())  # 200ms로 변경
```

## 라이센스

이 코드는 MIT 라이센스 하에 배포됩니다.
