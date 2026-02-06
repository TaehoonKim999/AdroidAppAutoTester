# Android App Auto Tester

> 안드로이드 폰에 설치된 여러 네이티브 앱을 자동으로 테스트하는 시스템

## 📋 개요

**Android App Auto Tester**는 Google Play 비공개 테스트 기간 동안 자동으로 앱을 테스트하고 에러, 크래시, ANR 등을 감지하는 시스템입니다.

### 주요 기능

- ✅ 여러 앱을 자동으로 테스트
- ✅ UI 자동 탐색 및 다양한 동작 수행 (클릭, 스크롤, 텍스트 입력 등)
- ✅ 에러, 크래시, ANR 감지 및 리포트 생성
- ✅ 실시간 스크린샷 촬영
- ✅ logcat 로그 수집 및 분석
- ✅ 다양한 포맷의 리포트 생성 (Text, HTML, JSON)
- ✅ GUI를 통한 쉬운 앱 선택 및 테스트 관리
- ✅ CLI를 통한 스크립트 자동화 지원
- ✅ 디바이스 및 설정 관리 기능

### 지원 환경

| 플랫폼 | 지원 버전 |
|--------|----------|
| Windows | 10/11 |
| Ubuntu  | 20.04/22.04 |

### 시스템 요구사항

- Python 3.8 이상
- USB 연결된 안드로이드 폰 (Android 5.0+)
- USB 디버깅이 활성화된 디바이스

---

## 🚀 빠른 시작

### Windows

1. **레포지토리 클론**
   ```bash
   git clone <repository-url>
   cd 05_AndroidAppAutoTester
   ```

2. **설치 스크립트 실행**
   ```cmd
   setup_windows.bat
   ```

3. **앱 실행**
   ```cmd
   # GUI 버전 (권장)
   python -m src.main --gui

   # CLI 버전
   python -m src.main
   ```

### Ubuntu

1. **레포지토리 클론**
   ```bash
   git clone <repository-url>
   cd 05_AndroidAppAutoTester
   ```

2. **설치 스크립트 실행**
   ```bash
   chmod +x setup_ubuntu.sh
   ./setup_ubuntu.sh
   ```

3. **앱 실행**
   ```bash
   # GUI 버전 (권장)
   python3 -m src.main --gui

   # CLI 버전
   python3 -m src.main
   ```

---

## 📖 사용 방법

### GUI 버전 (권장)

#### 1. 앱 실행
```bash
# Windows
python -m src.main --gui

# Ubuntu
python3 -m src.main --gui

# 또는 간단하게
python -m src.main -g
```

#### 2. 디바이스 선택
- "Devices" 탭 클릭
- "Refresh" 버튼으로 연결된 디바이스 목록 로드
- 사용할 디바이스 "Select" 버튼 클릭

#### 3. 앱 설정
- "Apps" 탭 클릭
- "Add App"으로 새 앱 추가
- 또는 기존 앱 "Edit/Delete"
- 필요한 필드: Name, Package, Activity, Duration

#### 4. 설정 관리
- "Config" 탭 클릭
- 전역 설정 편집 (스크린샷, logcat, 재시도 등)
- "Save"로 설정 저장
- "Reset"으로 기본값 복원

#### 5. 테스트 실행
- "Test" 탭 클릭
- 테스트할 앱 체크박스 선택
- "Select All"로 모든 앱 선택
- "Run Tests" 버튼 클릭
- 실시간 로그 및 진행률 모니터링

#### 6. 결과 확인
- "Report" 탭 클릭
- 생성된 리포트 목록 확인
- HTML 리포트는 "Preview"로 미리보기
- "Open"으로 브라우저에서 열기

### CLI 버전

#### 기본 사용법

```bash
# 연결된 디바이스 목록
python -m src.main list

# 모든 앱 목록
python -m src.main list --apps

# 모든 테스트 실행
python -m src.main run

# 특정 앱 테스트
python -m src.main run --app com.example.app

# 상세 옵션
python -m src.main --help
```

#### 고급 옵션

```bash
# 테스트 시간 조정 (초)
python -m src.main run --duration 60

# 특정 동작만 실행
python -m src.main run --actions scroll click_buttons

# 다중 리포트 포맷
python -m src.main run --report html json

# logcat 비활성화
python -m src.main run --no-logcat

# 스크린샷 비활성화
python -m src.main run --no-screenshot

# 출력 디렉토리 지정
python -m src.main run --output-dir /path/to/output
```

#### 설정 관리

```bash
# 설정 조회
python -m src.main config --get test_duration

# 설정 변경
python -m src.main config --set test_duration 60

# 설정 초기화
python -m src.main config --reset
```

---

## ⚙️ 설정 파일

### config/apps.json

테스트할 앱 목록을 설정합니다.

```json
[
  {
    "name": "앱 이름",
    "package": "com.example.app",
    "activity": ".MainActivity",
    "test_duration": 120
  }
]
```

| 필드 | 설명 |
|------|------|
| name | 앱 표시 이름 |
| package | 패키지명 (ADB로 확인 가능) |
| activity | 시작 액티비티 |
| test_duration | 테스트 시간 (초) |

### config/settings.json

전역 설정을 관리합니다.

```json
{
  "screenshot_on_error": true,
  "screenshot_interval": 0,
  "collect_logcat": true,
  "logcat_filter": ["E", "W", "F"],
  "max_test_retries": 3,
  "delay_between_apps": 5
}
```

| 필드 | 설명 |
|------|------|
| screenshot_on_error | 에러 시 스크린샷 저장 여부 |
| screenshot_interval | 정기 스크린샷 간격 (초, 0=비활성화) |
| collect_logcat | logcat 수집 여부 |
| logcat_filter | 수집할 로그 레벨 (E=Error, W=Warning, F=Fatal) |
| max_test_retries | 테스트 실패 시 최대 재시도 횟수 |
| delay_between_apps | 앱 간 대기 시간 (초) |

---

## 📂 디렉토리 구조

```
05_AndroidAppAutoTester/
├── docs/                    # 문서
│   ├── SOFTWARE_DESIGN.md
│   └── TODO.md
├── config/                  # 설정 파일
│   ├── apps.json.sample
│   └── settings.json.sample
├── src/                     # 소스 코드
│   ├── __init__.py
│   ├── platform_utils.py   # OS별 유틸리티
│   ├── config_manager.py   # 설정 관리
│   ├── device_manager.py   # 디바이스 연결 관리
│   ├── ui_explorer.py      # UI 자동 탐색
│   ├── log_collector.py    # 로그 수집
│   ├── test_engine.py     # 테스트 실행 엔진
│   ├── report_generator.py # 리포트 생성
│   ├── main.py          # CLI 메인
│   └── gui/            # GUI 모듈
│       ├── __init__.py
│       ├── main_window.py      # 메인 윈도우
│       ├── devices_view.py     # 디바이스 뷰
│       ├── apps_view.py        # 앱 뷰
│       ├── config_view.py      # 설정 뷰
│       ├── test_view.py        # 테스트 뷰
│       └── report_view.py     # 리포트 뷰
├── tests/                   # 단위 테스트
│   ├── test_phase1.py   # 테스트 Phase 1
│   ├── test_phase2.py   # 테스트 Phase 2
│   ├── test_phase3.py   # 테스트 Phase 3
│   ├── test_phase4.py   # 테스트 Phase 4
│   ├── test_phase5.py   # 테스트 Phase 5
│   ├── test_phase6.py   # 테스트 Phase 6
│   └── test_phase7.py   # 테스트 Phase 7
├── templates/               # 리포트 템플릿
│   ├── report_template.html
│   └── report_template.md
├── reports/                 # 생성된 리포트
├── screenshots/             # 스크린샷
├── logs/                    # 로그 파일
├── requirements.txt         # Python 의존성
├── setup_windows.bat        # Windows 설치 스크립트
├── setup_ubuntu.sh         # Ubuntu 설치 스크립트
├── .gitignore
└── README.md               # 프로젝트 설명 (본 파일)
```

---

## 🔧 Android 디바이스 설정

### 1. 개발자 옵션 활성화

1. **설정** > **휴대전화 정보** 이동
2. **빌드 번호**를 7번 탭하여 개발자 옵션 활성화

### 2. USB 디버깅 활성화

1. **설정** > **개발자 옵션** 이동
2. **USB 디버깅** 활성화

### 3. USB 연결 확인

```bash
# 연결된 디바이스 확인
adb devices

# 정상 연결 시 다음과 같이 표시:
# List of devices attached
# XXXXXXXXXXXX    device
```

### 4. Ubuntu에서 USB 권한 설정 (필요한 경우)

```bash
# udev 규칙 파일 생성
sudo nano /etc/udev/rules.d/51-android.rules

# 다음 내용 추가 (DEVICE_ID는 adb devices로 확인)
SUBSYSTEM=="usb", ATTR{idVendor}=="DEVICE_ID", MODE="0666"

# udev 규칙 재로드
sudo udevadm control --reload-rules
sudo udevadm trigger
```

---

## 📊 테스트 리포트 예시

테스트 완료 후 `reports/` 디렉토리에 리포트가 생성됩니다.

### Text 리포트

```
================================================================================
  Test Report
================================================================================

Date: 2025-02-04 14:30:00
Device: Samsung Galaxy S23 (Android 14)

--------------------------------------------------------------------------------
Summary
--------------------------------------------------------------------------------

Total Apps: 10
Success: 8
Errors: 2
Crashes: 1
ANRs: 0

--------------------------------------------------------------------------------
App Results
--------------------------------------------------------------------------------

✅ App 1 (com.example.app1)
  Status: Success
  Duration: 2:05
  Screenshots: 15
  Actions: 42
  Errors: 0

❌ App 2 (com.example.app2)
  Status: Error
  Duration: 1:30
  Screenshots: 8
  Actions: 21
  Errors: 2
    - NullPointerException at MainActivity.java:45
    - Network timeout (30s)
```

### HTML 리포트

HTML 리포트는 브라우저에서 시각적으로 확인할 수 있으며, 스크린샷이 포함됩니다.

### JSON 리포트

JSON 리포트는 프로그래밍 방식으로 분석하기 좋습니다.

```json
{
  "date": "2025-02-04T14:30:00",
  "device": {
    "serial": "XXXXXXXXXXXX",
    "model": "Samsung Galaxy S23",
    "android_version": "14"
  },
  "summary": {
    "total_apps": 10,
    "success": 8,
    "errors": 2,
    "crashes": 1,
    "anrs": 0
  },
  "app_results": [...]
}
```

---

## 🧪 단위 테스트

```bash
# 모든 테스트 실행
pytest tests/

# 특정 Phase 테스트
python tests/test_phase1.py
python tests/test_phase2.py
...

# 테스트 커버리지 확인
pytest --cov=src tests/
```

---

## 🤝 기여

이 프로젝트는 현재 개발 중입니다. 버그 리포트나 기능 요청은 이슈 tracker에 등록해주세요.

---

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

## 🔗 관련 링크

- [uiautomator2 문서](https://github.com/openatx/uiautomator2)
- [Android ADB 문서](https://developer.android.com/studio/command-line/adb)
- [customtkinter 문서](https://customtkinter.tomschimansky.com/)

---

## 💬 자주 묻는 질문 (FAQ)

### Q: 안드로이드 폰이 연결되지 않습니다.
**A**: 다음을 확인하세요:
- USB 케이블이 데이터 전송용인지 확인 (충전용 케이블은 작동하지 않음)
- USB 디버깅이 활성화되어 있는지 확인
- `adb devices` 명령어로 연결 상태 확인
- USB 포트를 변경하거나 컴퓨터 재시작 시도

### Q: 테스트 중 앱이 멈춥니다.
**A**: 자동으로 감지되고 다음 앱으로 진행합니다. 로그와 스크린샷이 저장되므로 리포트를 확인해주세요.

### Q: 어떤 앱을 테스트해야 하나요?
**A**: GUI에서 "Apps" 탭으로 이동하여 "Add App"으로 앱을 추가하세요. CLI에서는 `config/apps.json`을 직접 편집할 수 있습니다.

### Q: 테스트 시간은 어떻게 설정하나요?
**A**: 
- GUI: Apps 탭에서 각 앱의 Duration 설정
- CLI: `config/apps.json`에서 `test_duration` 필드 설정

### Q: GUI 대신 CLI를 사용하고 싶습니다.
**A**: `python -m src.main`으로 CLI를 실행하세요. CLI는 스크립트 자동화에 적합합니다.

### Q: GUI 실행 명령어가 작동하지 않습니다.
**A**: 올바른 명령어는 `python -m src.main --gui` 또는 `python -m src.main -g`입니다.

### Q: HTML 리포트에서 스크린샷이 보이지 않습니다.
**A**: `config/settings.json`에서 `screenshot_on_error: true`로 설정하세요. 정기 스크린샷은 `screenshot_interval` 설정으로 활성화할 수 있습니다.

---

**문의사항이 있으시면 이슈 tracker에 등록해주세요!**