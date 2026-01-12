#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹 배포를 위한 파일들을 준비합니다.
"""

import os
import shutil
import json

def build_web():
    """웹 배포를 위한 파일들을 준비합니다."""
    
    print("="*60)
    print("🌐 뚜뚜의 어드벤처 - 웹 배포 준비")
    print("="*60)
    
    # 1. 웹 배포 폴더 생성
    deploy_folder = "web_deploy"
    if os.path.exists(deploy_folder):
        print(f"⚠️  기존 {deploy_folder} 폴더를 삭제합니다...")
        shutil.rmtree(deploy_folder)
    
    os.makedirs(deploy_folder)
    print(f"✅ {deploy_folder} 폴더 생성")
    
    # 2. web 폴더 복사
    print("\n📁 웹 파일 복사 중...")
    web_files = ["index.html", "style.css", "script.js"]
    for file in web_files:
        src = os.path.join("web", file)
        if os.path.exists(src):
            shutil.copy(src, deploy_folder)
            print(f"  ✅ {file}")
        else:
            print(f"  ⚠️  {file} 파일을 찾을 수 없습니다.")
    
    # 3. assets 폴더 복사
    print("\n📁 assets 폴더 복사 중...")
    assets_src = "assets"
    assets_dst = os.path.join(deploy_folder, "assets")
    if os.path.exists(assets_src):
        shutil.copytree(assets_src, assets_dst)
        print(f"  ✅ assets 폴더 복사 완료")
    else:
        print(f"  ⚠️  assets 폴더를 찾을 수 없습니다.")
    
    # 4. README 파일 생성
    print("\n📝 README 파일 생성 중...")
    readme_path = os.path.join(deploy_folder, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("# 뚜뚜의 어드벤처 - 웹 버전\n\n")
        f.write("## 🚀 배포 방법\n\n")
        f.write("### 1. GitHub Pages로 배포\n\n")
        f.write("```bash\n")
        f.write("# 이 폴더를 GitHub 저장소로 업로드\n")
        f.write("git init\n")
        f.write("git add .\n")
        f.write("git commit -m \"Initial commit\"\n")
        f.write("git branch -M main\n")
        f.write("git remote add origin https://github.com/username/repo.git\n")
        f.write("git push -u origin main\n\n")
        f.write("# GitHub 저장소 Settings > Pages에서 배포\n")
        f.write("```\n\n")
        f.write("### 2. Netlify로 배포\n\n")
        f.write("1. [Netlify](https://www.netlify.com/)에 가입\n")
        f.write("2. '새 사이트' > '폴더 업로드'\n")
        f.write("3. 이 폴더를 드래그 앤 드롭\n\n")
        f.write("### 3. Vercel로 배포\n\n")
        f.write("1. [Vercel](https://vercel.com/)에 가입\n")
        f.write("2. '새 프로젝트' > '폴더 업로드'\n")
        f.write("3. 이 폴더를 업로드\n\n")
        f.write("### 4. 로컬에서 테스트\n\n")
        f.write("```bash\n")
        f.write("# Python 내장 서버 사용\n")
        f.write("python3 -m http.server 8000\n\n")
        f.write("# 브라우저에서 http://localhost:8000 접속\n")
        f.write("```\n\n")
        f.write("## 📝 주의사항\n\n")
        f.write("- 이 웹사이트는 게임의 소개 페이지입니다\n")
        f.write("- 실제 게임 플레이는 Python 프로그램에서만 가능합니다\n")
        f.write("- 웹캠과 센서 기능은 웹 버전에서 지원되지 않습니다\n\n")
        f.write("## 🎨 커스터마이징\n\n")
        f.write("- `index.html`: 내용 수정\n")
        f.write("- `style.css`: 디자인 수정\n")
        f.write("- `script.js`: 기능 추가\n")
        f.write("- `assets/`: 이미지 교체\n")
    
    print(f"  ✅ README.md 생성")
    
    # 5. netlify.toml 생성 (Netlify 배포용)
    print("\n📝 Netlify 설정 파일 생성 중...")
    netlify_config = os.path.join(deploy_folder, "netlify.toml")
    with open(netlify_config, "w", encoding="utf-8") as f:
        f.write("[build]\n")
        f.write('  publish = "."\n\n')
        f.write("[[redirects]]\n")
        f.write('  from = "/*"\n')
        f.write('  to = "/index.html"\n')
        f.write('  status = 200\n')
    print(f"  ✅ netlify.toml 생성")
    
    # 6. vercel.json 생성 (Vercel 배포용)
    print("\n📝 Vercel 설정 파일 생성 중...")
    vercel_config = os.path.join(deploy_folder, "vercel.json")
    vercel_data = {
        "version": 2,
        "routes": [
            {
                "src": "/(.*)",
                "dest": "/$1"
            }
        ]
    }
    with open(vercel_config, "w", encoding="utf-8") as f:
        json.dump(vercel_data, f, indent=2, ensure_ascii=False)
    print(f"  ✅ vercel.json 생성")
    
    # 7. .gitignore 생성
    print("\n📝 .gitignore 파일 생성 중...")
    gitignore_path = os.path.join(deploy_folder, ".gitignore")
    with open(gitignore_path, "w", encoding="utf-8") as f:
        f.write("# macOS\n")
        f.write(".DS_Store\n\n")
        f.write("# Windows\n")
        f.write("Thumbs.db\n\n")
        f.write("# Editor\n")
        f.write(".vscode/\n")
        f.write(".idea/\n")
    print(f"  ✅ .gitignore 생성")
    
    # 8. 로컬 테스트 스크립트 생성
    print("\n📝 로컬 테스트 스크립트 생성 중...")
    test_script = os.path.join(deploy_folder, "test_local.py")
    with open(test_script, "w", encoding="utf-8") as f:
        f.write("#!/usr/bin/env python3\n")
        f.write('"""로컬에서 웹사이트를 테스트합니다."""\n\n')
        f.write("import http.server\n")
        f.write("import socketserver\n")
        f.write("import webbrowser\n")
        f.write("import os\n\n")
        f.write("PORT = 8000\n\n")
        f.write('print("="*60)\n')
        f.write('print("🌐 뚜뚜의 어드벤처 - 로컬 웹 서버")\n')
        f.write('print("="*60)\n')
        f.write('print(f"서버 시작: http://localhost:{PORT}")\n')
        f.write('print("종료하려면 Ctrl+C를 누르세요")\n')
        f.write('print("="*60)\n\n')
        f.write("# 브라우저 자동 열기\n")
        f.write("webbrowser.open(f'http://localhost:{PORT}')\n\n")
        f.write("# 서버 시작\n")
        f.write("Handler = http.server.SimpleHTTPRequestHandler\n")
        f.write("with socketserver.TCPServer(('', PORT), Handler) as httpd:\n")
        f.write("    try:\n")
        f.write("        httpd.serve_forever()\n")
        f.write("    except KeyboardInterrupt:\n")
        f.write('        print("\\n서버를 종료합니다...")\n')
    
    # 실행 권한 추가 (Unix 계열)
    if os.name != 'nt':
        os.chmod(test_script, 0o755)
    print(f"  ✅ test_local.py 생성")
    
    # 9. 배포 가이드 생성
    print("\n📝 배포 가이드 생성 중...")
    guide_path = os.path.join(deploy_folder, "DEPLOY_GUIDE.md")
    with open(guide_path, "w", encoding="utf-8") as f:
        f.write("# 🚀 웹 배포 가이드\n\n")
        f.write("## 준비된 파일들\n\n")
        f.write("- `index.html`: 메인 HTML 파일\n")
        f.write("- `style.css`: 스타일시트\n")
        f.write("- `script.js`: JavaScript 파일\n")
        f.write("- `assets/`: 이미지 및 폰트\n")
        f.write("- `netlify.toml`: Netlify 설정\n")
        f.write("- `vercel.json`: Vercel 설정\n\n")
        f.write("## 🌐 무료 호스팅 서비스\n\n")
        f.write("### 1️⃣ GitHub Pages (추천)\n\n")
        f.write("**장점**: 무료, 간단, GitHub 통합\n\n")
        f.write("**단계**:\n")
        f.write("1. GitHub에 새 저장소 생성\n")
        f.write("2. 이 폴더를 저장소로 업로드\n")
        f.write("3. Settings > Pages > Source: main branch 선택\n")
        f.write("4. 몇 분 후 URL 생성 완료\n\n")
        f.write("### 2️⃣ Netlify\n\n")
        f.write("**장점**: 드래그 앤 드롭으로 즉시 배포\n\n")
        f.write("**단계**:\n")
        f.write("1. [netlify.com](https://netlify.com) 가입\n")
        f.write("2. '새 사이트' 클릭\n")
        f.write("3. 이 폴더를 드래그 앤 드롭\n")
        f.write("4. 즉시 배포 완료!\n\n")
        f.write("### 3️⃣ Vercel\n\n")
        f.write("**장점**: 빠른 CDN, 자동 HTTPS\n\n")
        f.write("**단계**:\n")
        f.write("1. [vercel.com](https://vercel.com) 가입\n")
        f.write("2. '새 프로젝트' 클릭\n")
        f.write("3. 이 폴더 업로드\n")
        f.write("4. 자동 배포 완료\n\n")
        f.write("## 🖥️ 로컬 테스트\n\n")
        f.write("배포 전에 로컬에서 테스트하세요:\n\n")
        f.write("```bash\n")
        f.write("python3 test_local.py\n")
        f.write("```\n\n")
        f.write("브라우저가 자동으로 열립니다.\n\n")
        f.write("## ✏️ 내용 수정\n\n")
        f.write("- **텍스트 수정**: `index.html` 파일 편집\n")
        f.write("- **디자인 변경**: `style.css` 파일 편집\n")
        f.write("- **기능 추가**: `script.js` 파일 편집\n")
        f.write("- **이미지 교체**: `assets/` 폴더의 파일 교체\n\n")
        f.write("## 📞 문제 해결\n\n")
        f.write("**Q: 이미지가 안 보여요**\n")
        f.write("- `assets/` 폴더가 올바르게 업로드되었는지 확인\n")
        f.write("- 파일 경로가 `../assets/`로 시작하는지 확인\n\n")
        f.write("**Q: 한글이 깨져요**\n")
        f.write("- 파일이 UTF-8로 저장되었는지 확인\n")
        f.write("- HTML에 `<meta charset=\"UTF-8\">` 있는지 확인\n\n")
        f.write("**Q: CSS가 적용 안 돼요**\n")
        f.write("- `style.css` 파일이 같은 폴더에 있는지 확인\n")
        f.write("- 브라우저 캐시 삭제 (Ctrl+Shift+R)\n")
    
    print(f"  ✅ DEPLOY_GUIDE.md 생성")
    
    # 10. 완료 메시지
    print("\n"+"="*60)
    print("🎉 웹 배포 준비 완료!")
    print("="*60)
    print(f"\n📁 배포 폴더: {os.path.abspath(deploy_folder)}/")
    print("\n다음 단계:")
    print("1. 로컬 테스트:")
    print(f"   cd {deploy_folder}")
    print("   python3 test_local.py")
    print("\n2. 온라인 배포:")
    print("   - DEPLOY_GUIDE.md 파일을 참고하세요")
    print("   - GitHub Pages, Netlify, Vercel 중 선택\n")

if __name__ == "__main__":
    build_web()
