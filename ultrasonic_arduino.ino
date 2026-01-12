/*
 * 초음파 센서 시리얼 테스트 코드 (게임 프로젝트 호환)
 * HC-SR04 초음파 센서를 사용하여 거리를 측정하고 시리얼로 전송
 * 기존 게임 프로젝트와 호환되는 데이터 형식 지원
 */

// 핀 정의
const int TRIG_PIN = 9;    // 트리거 핀
const int ECHO_PIN = 10;   // 에코 핀

// 설정
const int MEASURE_INTERVAL = 100;  // 측정 간격 (ms)
const int MAX_DISTANCE = 400;      // 최대 측정 거리 (cm)
const int MIN_DISTANCE = 2;        // 최소 측정 거리 (cm)
const int NEAR_THRESHOLD = 28;      // 근접 감지 임계값 (cm)

// 변수
unsigned long lastMeasureTime = 0;
int distance = 0;
bool isConnected = false;
bool nearDetected = false;

// 데이터 형식 설정
const bool USE_GAME_FORMAT = true;  // 게임 프로젝트 형식 사용
const bool USE_JSON_FORMAT = true;  // JSON 형식 사용

void setup() {
  // 시리얼 통신 초기화
  Serial.begin(9600);
  
  // 핀 모드 설정
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  // 버퍼 클리어
  Serial.flush();
  delay(100);
  
  // 초기화 완료 신호
  if (USE_JSON_FORMAT) {
    Serial.println("{\"status\": \"ready\", \"message\": \"Ultrasonic sensor initialized for game\"}");
  } else {
    Serial.println("Ultrasonic sensor initialized for game");
  }
  Serial.flush();
  
  // 연결 상태 확인
  isConnected = true;
}

void loop() {
  unsigned long currentTime = millis();
  
  // 정해진 간격으로 측정
  if (currentTime - lastMeasureTime >= MEASURE_INTERVAL) {
    distance = measureDistance();
    
    if (distance > 0) {
      sendData(distance);
      
      // 근접 감지
      if (distance <= NEAR_THRESHOLD && !nearDetected) {
        nearDetected = true;
        sendNearSignal();
      } else if (distance > NEAR_THRESHOLD && nearDetected) {
        nearDetected = false;
      }
    }
    
    lastMeasureTime = currentTime;
  }
  
  // 시리얼 명령 처리
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    handleCommand(command);
  }
}

int measureDistance() {
  // 트리거 핀 초기화
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  
  // 트리거 신호 발생 (10μs)
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  // 에코 신호 대기 및 측정
  long duration = pulseIn(ECHO_PIN, HIGH, 30000); // 30ms 타임아웃
  
  // 거리 계산 (cm)
  int distance = duration * 0.034 / 2;
  
  // 유효 범위 체크
  if (distance < MIN_DISTANCE || distance > MAX_DISTANCE) {
    distance = -1; // 측정 실패
  }
  
  return distance;
}

void sendData(int distance) {
  if (USE_GAME_FORMAT) {
    // 게임 프로젝트 호환 형식
    if (USE_JSON_FORMAT) {
      // JSON 형식: {"cm": 25} (기존 게임 형식)
      String jsonData = "{\"cm\": " + String(distance) + "}";
      Serial.println(jsonData);
      Serial.flush(); // 버퍼 즉시 전송
    } else {
      // 간단한 형식: cm=25
      Serial.println("cm=" + String(distance));
      Serial.flush(); // 버퍼 즉시 전송
    }
  } else {
    // 테스트용 상세 형식
    if (USE_JSON_FORMAT) {
      String jsonData = "{\"distance\": " + String(distance) + 
                       ", \"timestamp\": " + String(millis()) + 
                       ", \"unit\": \"cm\"}";
      Serial.println(jsonData);
      Serial.flush(); // 버퍼 즉시 전송
    } else {
      Serial.println("Distance: " + String(distance) + " cm");
      Serial.flush(); // 버퍼 즉시 전송
    }
  }
}

void sendNearSignal() {
  if (USE_GAME_FORMAT) {
    // 게임 프로젝트 호환 형식
    if (USE_JSON_FORMAT) {
      // JSON 형식: {"near": true, "cm": 4}
      String jsonData = "{\"near\": true, \"cm\": " + String(distance) + "}";
      Serial.println(jsonData);
      Serial.flush(); // 버퍼 즉시 전송
    } else {
      // 간단한 형식: near=true
      Serial.println("near=true");
      Serial.flush(); // 버퍼 즉시 전송
    }
  } else {
    // 테스트용 형식
    if (USE_JSON_FORMAT) {
      String jsonData = "{\"near\": true, \"distance\": " + String(distance) + "}";
      Serial.println(jsonData);
      Serial.flush(); // 버퍼 즉시 전송
    } else {
      Serial.println("NEAR DETECTED: " + String(distance) + " cm");
      Serial.flush(); // 버퍼 즉시 전송
    }
  }
}

void handleCommand(String command) {
  if (command == "ping") {
    if (USE_JSON_FORMAT) {
      Serial.println("{\"status\": \"pong\", \"message\": \"Arduino is alive\"}");
    } else {
      Serial.println("pong");
    }
  }
  else if (command == "status") {
    if (USE_JSON_FORMAT) {
      Serial.println("{\"status\": \"running\", \"sensor\": \"HC-SR04\", \"interval\": " + String(MEASURE_INTERVAL) + ", \"format\": \"game\"}");
    } else {
      Serial.println("status: running, interval: " + String(MEASURE_INTERVAL) + "ms");
    }
  }
  else if (command == "measure") {
    int dist = measureDistance();
    sendData(dist);
  }
  else if (command == "near") {
    sendNearSignal();
  }
  else if (command.startsWith("interval:")) {
    int newInterval = command.substring(9).toInt();
    if (newInterval >= 50 && newInterval <= 5000) {
      
      if (USE_JSON_FORMAT) {
        Serial.println("{\"status\": \"updated\", \"interval\": " + String(MEASURE_INTERVAL) + "}");
      } else {
        Serial.println("interval updated: " + String(MEASURE_INTERVAL) + "ms");
      }
    } else {
      if (USE_JSON_FORMAT) {
        Serial.println("{\"status\": \"error\", \"message\": \"Invalid interval (50-5000ms)\"}");
      } else {
        Serial.println("error: invalid interval");
      }
    }
  }
  else if (command == "format:game") {
    
    if (USE_JSON_FORMAT) {
      Serial.println("{\"status\": \"updated\", \"format\": \"game\"}");
    } else {
      Serial.println("format: game");
    }
  }
  else if (command == "format:test") {
    
    if (USE_JSON_FORMAT) {
      Serial.println("{\"status\": \"updated\", \"format\": \"test\"}");
    } else {
      Serial.println("format: test");
    }
  }
  else {
    if (USE_JSON_FORMAT) {
      Serial.println("{\"status\": \"error\", \"message\": \"Unknown command: " + command + "\"}");
    } else {
      Serial.println("error: unknown command");
    }
  }
}

// 추가 유틸리티 함수들
void sendRawData(int distance) {
  // 간단한 텍스트 형식으로 데이터 전송
  Serial.println("Distance: " + String(distance) + " cm");
}

void sendDetailedData(int distance) {
  // 상세한 정보와 함께 데이터 전송
  String detailedData = "{\"distance\": " + String(distance) + 
                       ", \"timestamp\": " + String(millis()) + 
                       ", \"unit\": \"cm\"" +
                       ", \"voltage\": " + String(analogRead(A0) * 5.0 / 1024.0) + 
                       ", \"free_memory\": " + String(freeMemory()) + "}";
  Serial.println(detailedData);
}

// 메모리 사용량 확인 함수
int freeMemory() {
  extern int __heap_start, *__brkval;
  int v;
  return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval);
}
