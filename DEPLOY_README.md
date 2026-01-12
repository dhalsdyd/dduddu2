# 🚀 배포 가이드

## 📦 두 가지 배포 방법

### 1. EXE 파일로 배포 (Windows 실행 파일)

Python이 없는 컴퓨터에서도 실행할 수 있는 독립 실행 파일을 만듭니다.

#### 장점

- ✅ Python 설치 불필요
- ✅ 웹캠과 센서 완전 지원
- ✅ 실제 게임 플레이 가능
- ✅ 파일 하나로 배포 가능

#### 단점

- ❌ Windows에서만 실행 가능
- ❌ 파일 크기가 큼 (100-200MB)
- ❌ 빌드 시간 소요

#### 실행 방법

```bash
python build_exe.py
```

#### 빌드 후 생성되는 파일

```
배포용/
├── 뚜뚜의어드벤처.exe    # 실행 파일 (더블클릭으로 실행)
└── README.txt             # 사용 설명서
```

#### 배포 방법

1. `배포용/` 폴더를 압축 (zip)
2. 사용자에게 전달
3. 압축 해제 후 `.exe` 파일 실행

#### 주의사항

- Windows Defender가 차단할 수 있음 → "추가 정보" > "실행" 클릭
- 처음 실행 시 시간이 걸릴 수 있음
- 센서와 웹캠은 선택사항 (없어도 실행 가능)

---

### 2. 웹사이트로 배포

게임 소개 페이지를 웹에 배포합니다.

#### 장점

- ✅ 모든 기기에서 접속 가능
- ✅ 설치 불필요
- ✅ 즉시 확인 가능
- ✅ 무료 호스팅 가능

#### 단점

- ❌ 실제 게임 플레이 불가능 (소개 페이지만)
- ❌ 웹캠/센서 기능 없음

#### 실행 방법

```bash
python build_web.py
```

#### 빌드 후 생성되는 파일

```
web_deploy/
├── index.html           # 메인 페이지
├── style.css            # 스타일시트
├── script.js            # JavaScript
├── assets/              # 이미지 및 폰트
├── README.md            # 설명서
├── DEPLOY_GUIDE.md      # 배포 가이드
├── test_local.py        # 로컬 테스트 스크립트
├── netlify.toml         # Netlify 설정
└── vercel.json          # Vercel 설정
```

#### 로컬 테스트

```bash
cd web_deploy
python3 test_local.py
```

브라우저에서 `http://localhost:8000`이 자동으로 열립니다.

#### 온라인 배포 방법

##### 1️⃣ GitHub Pages (추천)

```bash
cd web_deploy
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/사용자이름/저장소.git
git push -u origin main
```

그 다음:

1. GitHub 저장소 → Settings
2. Pages → Source: main branch 선택
3. Save 클릭
4. 몇 분 후 URL 생성

##### 2️⃣ Netlify (가장 간단)

1. [netlify.com](https://netlify.com) 접속 및 가입
2. "새 사이트" 클릭
3. `web_deploy/` 폴더를 드래그 앤 드롭
4. 몇 초 후 배포 완료!

##### 3️⃣ Vercel

1. [vercel.com](https://vercel.com) 접속 및 가입
2. "새 프로젝트" 클릭
3. `web_deploy/` 폴더 업로드
4. 자동 배포 완료

---

## 🎯 추천 배포 방법

### 실제 게임을 배포하고 싶다면

→ **EXE 배포** 사용

- 게임 전체 기능 사용 가능
- 센서와 웹캠 연동 가능

### 게임을 소개하고 싶다면

→ **웹사이트 배포** 사용

- 누구나 쉽게 접근 가능
- 멋진 소개 페이지

### 둘 다 하고 싶다면

→ **웹사이트 + EXE 다운로드 링크**

- 웹사이트에서 게임 소개
- EXE 파일 다운로드 링크 제공

---

## 📝 배포 체크리스트

### EXE 배포 전

- [ ] 게임이 정상 작동하는지 테스트
- [ ] assets 폴더가 모두 포함되었는지 확인
- [ ] README.txt 작성
- [ ] 압축 파일 생성

### 웹 배포 전

- [ ] 로컬에서 테스트 (`test_local.py`)
- [ ] 이미지 경로가 올바른지 확인
- [ ] 한글이 제대로 표시되는지 확인
- [ ] 모바일에서도 확인

---

## 🛠️ 문제 해결

### EXE 빌드 실패

**PyInstaller 설치 오류**

```bash
pip install --upgrade pip
pip install pyinstaller
```

**빌드 오류**

```bash
# 캐시 삭제 후 재시도
rm -rf build dist
python build_exe.py
```

### 웹 배포 문제

**이미지가 안 보임**

- `assets/` 폴더가 올바르게 복사되었는지 확인
- 경로가 `../assets/`로 시작하는지 확인

**한글 깨짐**

- 파일이 UTF-8로 저장되었는지 확인
- HTML에 `<meta charset="UTF-8">` 확인

---

## 💡 팁

### EXE 파일 크기 줄이기

```python
# build_exe.py에서 수정
pyinstaller_args = [
    "--onefile",
    "--windowed",
    "--exclude-module", "tkinter",  # 미사용 모듈 제외
    "--exclude-module", "matplotlib",
    # ... 기타 설정
]
```

### 웹사이트 최적화

1. **이미지 압축**

   - [TinyPNG](https://tinypng.com/) 사용
   - 파일 크기 50-70% 감소

2. **코드 압축**

   - CSS: [CSSMinifier](https://cssminifier.com/)
   - JS: [JSCompress](https://jscompress.com/)

3. **캐싱 활용**
   - 정적 파일은 브라우저 캐시 사용

---

## 📞 지원

문제가 발생하면:

1. 오류 메시지 전체를 복사
2. 실행 환경 정보 수집 (OS, Python 버전)
3. 재현 가능한 단계 정리

---

**즐거운 배포 되세요! 🎮✨**
