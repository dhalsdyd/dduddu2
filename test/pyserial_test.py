import serial
import time
import json

class UltrasonicSerialTest:
    def __init__(self, port='/dev/tty.usbmodem*', baudrate=9600):
        """
        초음파 센서 시리얼 테스트 클래스
        
        Args:
            port (str): 시리얼 포트 (기본값: '/dev/tty.usbmodem*')
            baudrate (int): 통신 속도 (기본값: 9600)
        """
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        
    def connect(self):
        """시리얼 연결"""
        try:
            # macOS에서 자동으로 포트 찾기
            import glob
            ports = glob.glob(self.port)
            
            if not ports:
                print("사용 가능한 USB 시리얼 포트를 찾을 수 없습니다.")
                print("사용 가능한 포트 목록:")
                self.list_ports()
                return False
                
            # 첫 번째 사용 가능한 포트 사용
            actual_port = ports[0]
            print(f"연결 시도: {actual_port}")
            
            self.serial_conn = serial.Serial(
                port=actual_port,
                baudrate=self.baudrate,
                timeout=1
            )
            
            # 연결 대기
            time.sleep(2)
            print(f"성공적으로 연결됨: {actual_port}")
            return True
            
        except serial.SerialException as e:
            print(f"시리얼 연결 오류: {e}")
            return False
    
    def list_ports(self):
        """사용 가능한 시리얼 포트 목록 출력"""
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        
        if not ports:
            print("사용 가능한 시리얼 포트가 없습니다.")
        else:
            for port in ports:
                print(f"  {port.device}: {port.description}")
    
    def disconnect(self):
        """시리얼 연결 해제"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print("시리얼 연결이 해제되었습니다.")
    
    def read_distance(self):
        """초음파 센서 거리 데이터 읽기"""
        if not self.serial_conn or not self.serial_conn.is_open:
            print("시리얼 연결이 없습니다.")
            return None
            
        try:
            # 데이터 읽기
            if self.serial_conn.in_waiting > 0:
                try:
                    line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                    
                    # JSON 형식 파싱 시도
                    try:
                        data = json.loads(line)
                        return data
                    except json.JSONDecodeError:
                        # 일반 텍스트 형식 처리
                        return {"raw": line, "distance": None}
                except UnicodeDecodeError as ude:
                    print(f"UTF-8 디코딩 오류: {ude}")
                    # 버퍼 클리어
                    self.serial_conn.reset_input_buffer()
                    return None
                except Exception as decode_error:
                    print(f"디코딩 오류: {decode_error}")
                    # 버퍼 클리어
                    self.serial_conn.reset_input_buffer()
                    return None
            
            return None
            
        except serial.SerialException as e:
            print(f"데이터 읽기 오류: {e}")
            return None
    
    def run_test(self, duration=30):
        """테스트 실행"""
        print("초음파 센서 시리얼 테스트 시작...")
        print(f"테스트 시간: {duration}초")
        print("-" * 50)
        
        if not self.connect():
            return
        
        start_time = time.time()
        data_count = 0
        
        try:
            while time.time() - start_time < duration:
                data = self.read_distance()
                
                if data:
                    data_count += 1
                    print(f"[{data_count:03d}] {time.strftime('%H:%M:%S')} - {data}")
                
                time.sleep(0.1)  # 100ms 대기
                
        except KeyboardInterrupt:
            print("\n테스트가 중단되었습니다.")
        
        finally:
            self.disconnect()
            print(f"\n테스트 완료: {data_count}개의 데이터를 수신했습니다.")

def main():
    """메인 함수"""
    print("초음파 센서 시리얼 테스트 프로그램")
    print("=" * 50)
    
    # 테스트 객체 생성
    test = UltrasonicSerialTest()
    
    # 사용 가능한 포트 목록 출력
    print("사용 가능한 시리얼 포트:")
    test.list_ports()
    print()
    
    # 테스트 실행
    test.run_test(duration=60)

if __name__ == "__main__":
    main()
