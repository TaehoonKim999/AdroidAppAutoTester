# 안드로이드 앱 자동 테스트 시스템 - 소프트웨어 설계서

## 문서 정보
- **프로젝트명**: Android App Auto Tester
- **버전**: 1.0.0
- **작성일**: 2025-02-04
- **목적**: Google Play 비공개 테스트를 위한 앱 자동 테스트 시스템

---

## 1. 개요

### 1.1 프로젝트 목표
- 실제 안드로이드 폰에 설치된 복수의 네이티브 앱(10개 이상)을 자동으로 테스트
- 각 앱의 UI를 자동 탐색하며 에러, 크래시, ANR 등을 감지
- 테스트 결과를 Markdown 리포트로 생성
- 14일간의 비공개 테스트 기간 동안 매일 자동 실행 가능
- **GUI를 통해 설치된 앱 목록에서 테스트할 앱을 쉽게 선택**

### 1.2 개발 환경
| 항목 | 내용 |
|------|------|
| 운영체제 | Windows 10/11, Ubuntu 20.04/22.04 |
| IDE | Visual Studio Code |
| 프로그래밍 언어 | Python 3.8+ |
| 테스트 기기 | 실제 안드로이드 폰 (USB 연결) |
| 예산 | 무료 도구만 사용 |

### 1.3 사용 기술 스택
| 기술 | 용도 | 버전 |
|------|------|------|
| Python | 메인 프로그래밍 언어 | 3.8+ |
| uiautomator2 | Android UI 자동화 | 최신 |
| ADB | Android Debug Bridge | Platform Tools |
| Pillow | 이미지 처리 (스크린샷) | 최신 |
| Jinja2 | 리포트 템플릿 | 최신 |
| **customtkinter** | **모던 GUI 프레임워크** | **최신** |

---

## 2. 시스템 아키텍처

### 2.1 전체 구조도
```
┌─────────────────────────────────────────────────────────────────┐
│                         테스트 컨트롤 PC                          │
│                    (Windows / Ubuntu)                           │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │   Config     │    │    Core      │    │     Output       │  │
│  │   Module     │───▶│   Engine     │───▶│    Module        │  │
│  │              │    │              │    │                  │  │
│  │ - apps.json  │    │ - 테스트 실행 │    │ - 리포트 생성    │  │
│  │ - settings   │    │ - UI 탐색    │    │ - 스크린샷 저장  │  │
│  └──────────────┘    │ - 로그 수집  │    └──────────────────┘  │
│                      └──────┬───────┘                          │
│                             │                                  │
└─────────────────────────────┼──────────────────────────────────┘
                              │ ADB (USB)
                              ▼
                       ┌─────────────┐
                       │  Android    │
                       │   Phone     │
                       │ (10개+ 앱)  │
                       └─────────────┘
```

### 2.2 모듈 구성도
```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                              │
│                    (프로그램 진입점)                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌─────────────────┐ ┌───────────┐ ┌─────────────────┐
│ ConfigManager   │ │TestRunner │ │ ReportGenerator │
│ (설정 관리)      │ │(테스트 실행)│ │   (리포트 생성)  │
└────────┬────────┘ └─────┬─────┘ └────────┬────────┘
         │                │                │
         ▼                ▼                ▼
┌─────────────────┐ ┌───────────┐ ┌─────────────────┐
│ PlatformUtils   │ │DeviceManager│ │  LogCollector  │
│ (OS별 처리)      │ │(디바이스 관리)│ │   (로그 수집)   │
└─────────────────┘ └─────┬─────┘ └─────────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │ UIExplorer  │
                   │ (UI 자동탐색) │
                   └─────────────┘
```

---

## 3. 디렉토리 구조

```
android-app-tester/
│
├── docs/                          # 문서
│   ├── SOFTWARE_DESIGN.md         # 소프트웨어 설계서 (본 문서)
│   └── TODO.md                    # TODO 리스트
│
├── config/                        # 설정 파일
│   ├── apps.json                  # 테스트할 앱 목록
│   └── settings.json              # 전역 설정
│
├── src/                           # 소스 코드
│   ├── __init__.py
│   ├── platform_utils.py          # OS별 유틸리티
│   ├── config_manager.py          # 설정 관리
│   ├── device_manager.py          # 디바이스 연결 관리
│   ├── ui_explorer.py             # UI 자동 탐색
│   ├── log_collector.py           # 로그 수집
│   ├── test_runner.py             # 테스트 실행 엔진
│   └── report_generator.py        # 리포트 생성
│
├── gui/                           # GUI 모듈
│   ├── __init__.py
│   ├── main_window.py             # 메인 윈도우
│   ├── app_selector.py            # 앱 선택 화면
│   ├── test_progress.py           # 테스트 진행 화면
│   ├── settings_panel.py          # 설정 패널
│   └── widgets.py                 # 커스텀 위젯
│
├── templates/                     # 리포트 템플릿
│   └── report_template.md         # Markdown 리포트 템플릿
│
├── reports/                       # 생성된 리포트 저장
│   └── .gitkeep
│
├── screenshots/                   # 스크린샷 저장
│   └── .gitkeep
│
├── logs/                          # 로그 파일 저장
│   └── .gitkeep
│
├── main.py                        # CLI 메인 실행 파일
├── main_gui.py                    # GUI 메인 실행 파일
├── requirements.txt               # Python 의존성
├── setup_windows.bat              # Windows 설치 스크립트
├── setup_ubuntu.sh                # Ubuntu 설치 스크립트
├── .gitignore                     # Git 제외 파일
└── README.md                      # 프로젝트 설명
```

---

## 4. 모듈 상세 설계

### 4.1 platform_utils.py - 플랫폼 유틸리티

**목적**: Windows와 Ubuntu 양쪽에서 동작하도록 OS별 차이를 추상화

```python
class PlatformUtils:
    """
    Attributes:
        system: str - 현재 OS 이름 ("Windows" / "Linux")
        is_windows: bool - Windows 여부
        is_linux: bool - Linux 여부
        project_root: Path - 프로젝트 루트 경로
    
    Methods:
        get_adb_command() -> str
            - OS에 맞는 ADB 명령어 반환
            - Windows: "adb.exe", Linux: "adb"
        
        get_path(name: str) -> Path
            - 주요 경로 반환 (screenshots, reports, logs, config)
        
        ensure_directories() -> None
            - 필요한 디렉토리 생성
        
        run_command(cmd: list) -> tuple[int, str, str]
            - 시스템 명령어 실행
            - 반환: (return_code, stdout, stderr)
    """
```

### 4.2 config_manager.py - 설정 관리

**목적**: JSON 설정 파일 로드 및 관리

```python
@dataclass
class AppConfig:
    """개별 앱 설정"""
    name: str                    # 앱 표시 이름
    package: str                 # 패키지명 (com.example.app)
    activity: str                # 시작 액티비티 (.MainActivity)
    test_duration: int           # 테스트 시간 (초)
    test_actions: list[str]      # 수행할 테스트 동작 목록

@dataclass
class GlobalSettings:
    """전역 설정"""
    screenshot_on_error: bool    # 에러 시 스크린샷 저장
    screenshot_interval: int     # 스크린샷 간격 (초)
    collect_logcat: bool         # logcat 수집 여부
    logcat_filter: list[str]     # logcat 필터 태그
    report_format: str           # 리포트 형식 (markdown)

class ConfigManager:
    """
    Methods:
        load_apps() -> list[AppConfig]
            - config/apps.json에서 앱 목록 로드
        
        load_settings() -> GlobalSettings
            - config/settings.json에서 전역 설정 로드
        
        validate() -> bool
            - 설정 파일 유효성 검사
    """
```

**config/apps.json 형식**:
```json
{
  "apps": [
    {
      "name": "앱 이름",
      "package": "com.example.app",
      "activity": ".MainActivity",
      "test_duration": 120,
      "test_actions": ["scroll", "click_buttons", "input_text", "back_navigation"]
    }
  ]
}
```

**config/settings.json 형식**:
```json
{
  "screenshot_on_error": true,
  "screenshot_interval": 30,
  "collect_logcat": true,
  "logcat_filter": ["E", "W", "F"],
  "report_format": "markdown",
  "max_test_retries": 3,
  "delay_between_apps": 5
}
```

### 4.3 device_manager.py - 디바이스 관리

**목적**: ADB를 통한 안드로이드 디바이스 연결 및 제어

```python
@dataclass
class DeviceInfo:
    """디바이스 정보"""
    serial: str                  # 디바이스 시리얼 번호
    model: str                   # 모델명
    android_version: str         # Android 버전
    sdk_version: int             # SDK 버전

class DeviceManager:
    """
    Methods:
        connect() -> bool
            - ADB로 디바이스 연결
            - uiautomator2 초기화
        
        disconnect() -> None
            - 연결 해제
        
        get_device_info() -> DeviceInfo
            - 디바이스 정보 조회
        
        is_connected() -> bool
            - 연결 상태 확인
        
        start_app(package: str, activity: str) -> bool
            - 앱 실행
        
        stop_app(package: str) -> bool
            - 앱 강제 종료
        
        is_app_running(package: str) -> bool
            - 앱 실행 상태 확인
        
        take_screenshot(filename: str) -> Path
            - 스크린샷 촬영 및 저장
        
        get_current_activity() -> str
            - 현재 포그라운드 액티비티 반환
    """
```

### 4.4 ui_explorer.py - UI 자동 탐색

**목적**: 앱의 UI를 자동으로 탐색하며 다양한 동작 수행

```python
@dataclass
class UIElement:
    """UI 요소 정보"""
    resource_id: str
    class_name: str
    text: str
    content_desc: str
    bounds: tuple
    clickable: bool
    scrollable: bool

@dataclass
class ExplorationResult:
    """탐색 결과"""
    screens_visited: int         # 방문한 화면 수
    elements_interacted: int     # 상호작용한 요소 수
    actions_performed: list      # 수행한 동작 목록
    errors_found: list           # 발견된 에러 목록

class UIExplorer:
    """
    Attributes:
        device: uiautomator2.Device
        visited_screens: set       # 방문한 화면 기록 (중복 방지)
    
    Methods:
        explore(duration: int, actions: list[str]) -> ExplorationResult
            - 지정된 시간 동안 UI 탐색 수행
            - actions: ["scroll", "click_buttons", "input_text", "back_navigation"]
        
        get_all_elements() -> list[UIElement]
            - 현재 화면의 모든 UI 요소 반환
        
        get_clickable_elements() -> list[UIElement]
            - 클릭 가능한 요소만 반환
        
        click_element(element: UIElement) -> bool
            - 요소 클릭
        
        scroll_screen(direction: str) -> bool
            - 화면 스크롤 (up/down/left/right)
        
        input_text(element: UIElement, text: str) -> bool
            - 텍스트 입력
        
        press_back() -> bool
            - 뒤로가기 버튼
        
        detect_error_dialog() -> bool
            - 에러 다이얼로그 감지
        
        get_screen_signature() -> str
            - 현재 화면의 고유 서명 (중복 방문 체크용)
    """
```

**탐색 알고리즘**:
```
1. 현재 화면의 모든 클릭 가능한 요소 수집
2. 방문하지 않은 요소 우선 선택
3. 요소 클릭 후 화면 변화 감지
4. 에러 다이얼로그 체크
5. 새로운 화면이면 visited_screens에 추가
6. 막다른 화면이면 뒤로가기
7. 지정된 시간까지 반복
```

### 4.5 log_collector.py - 로그 수집

**목적**: logcat 및 시스템 로그에서 에러 정보 수집

```python
@dataclass
class LogEntry:
    """로그 항목"""
    timestamp: datetime
    level: str                   # E(rror), W(arning), F(atal), I(nfo)
    tag: str
    message: str
    pid: int

@dataclass
class CrashInfo:
    """크래시 정보"""
    exception_type: str
    message: str
    stack_trace: str
    timestamp: datetime

class LogCollector:
    """
    Methods:
        start_collection(package: str) -> None
            - 특정 패키지의 로그 수집 시작
        
        stop_collection() -> list[LogEntry]
            - 로그 수집 중지 및 결과 반환
        
        get_errors() -> list[LogEntry]
            - 에러 레벨 로그만 필터링
        
        get_warnings() -> list[LogEntry]
            - 경고 레벨 로그만 필터링
        
        detect_crash() -> CrashInfo | None
            - FATAL EXCEPTION 감지
        
        detect_anr() -> bool
            - ANR (Application Not Responding) 감지
        
        get_memory_info(package: str) -> dict
            - 앱의 메모리 사용량 조회
        
        clear_logcat() -> None
            - logcat 버퍼 클리어
    """
```

### 4.6 test_runner.py - 테스트 실행 엔진

**목적**: 전체 테스트 프로세스 조율 및 실행

```python
@dataclass
class AppTestResult:
    """개별 앱 테스트 결과"""
    app_config: AppConfig
    status: str                  # "success" / "error" / "crash" / "timeout"
    start_time: datetime
    end_time: datetime
    duration: float
    exploration_result: ExplorationResult
    errors: list[LogEntry]
    crashes: list[CrashInfo]
    screenshots: list[Path]
    memory_peak: int
    suggestions: list[str]       # 개선 제안

@dataclass
class TestSessionResult:
    """전체 테스트 세션 결과"""
    session_id: str
    device_info: DeviceInfo
    start_time: datetime
    end_time: datetime
    app_results: list[AppTestResult]
    total_apps: int
    success_count: int
    error_count: int

class TestRunner:
    """
    Attributes:
        config_manager: ConfigManager
        device_manager: DeviceManager
        ui_explorer: UIExplorer
        log_collector: LogCollector
    
    Methods:
        run_all_tests() -> TestSessionResult
            - 모든 앱 순차적으로 테스트
        
        run_single_app_test(app: AppConfig) -> AppTestResult
            - 단일 앱 테스트
        
        _prepare_test(app: AppConfig) -> bool
            - 테스트 준비 (로그 클리어, 앱 실행)
        
        _execute_test(app: AppConfig) -> ExplorationResult
            - UI 탐색 실행
        
        _collect_results(app: AppConfig) -> AppTestResult
            - 결과 수집 및 정리
        
        _cleanup_test(app: AppConfig) -> None
            - 테스트 후 정리 (앱 종료)
        
        _generate_suggestions(result: AppTestResult) -> list[str]
            - 테스트 결과 기반 개선 제안 생성
    """
```

**테스트 흐름**:
```
run_all_tests()
│
├── 디바이스 연결 확인
├── 설정 로드
│
└── 각 앱에 대해:
    │
    ├── _prepare_test()
    │   ├── logcat 클리어
    │   ├── 앱 실행
    │   └── 실행 대기 (3초)
    │
    ├── _execute_test()
    │   ├── UI 탐색 시작
    │   ├── 주기적 스크린샷
    │   └── 에러 모니터링
    │
    ├── _collect_results()
    │   ├── 로그 수집
    │   ├── 에러/크래시 분석
    │   └── 개선 제안 생성
    │
    └── _cleanup_test()
        ├── 앱 종료
        └── 다음 앱 대기 (5초)
```

### 4.7 report_generator.py - 리포트 생성

**목적**: 테스트 결과를 Markdown 리포트로 생성

```python
class ReportGenerator:
    """
    Attributes:
        template_path: Path        # 템플릿 파일 경로
        output_path: Path          # 출력 디렉토리
    
    Methods:
        generate(session_result: TestSessionResult) -> Path
            - 전체 리포트 생성
            - 반환: 생성된 리포트 파일 경로
        
        _render_summary(result: TestSessionResult) -> str
            - 요약 섹션 렌더링
        
        _render_app_detail(app_result: AppTestResult) -> str
            - 개별 앱 상세 결과 렌더링
        
        _render_error_section(errors: list) -> str
            - 에러 섹션 렌더링
        
        _render_suggestions(suggestions: list) -> str
            - 개선 제안 섹션 렌더링
        
        _copy_screenshots(screenshots: list[Path]) -> list[Path]
            - 스크린샷을 리포트 디렉토리로 복사
    """
```

---

## 5. GUI 설계

### 5.1 GUI 개요

**목적**: 사용자가 쉽게 테스트할 앱을 선택하고 테스트 진행 상황을 모니터링

**프레임워크**: customtkinter (모던한 UI, 크로스 플랫폼)

### 5.2 화면 구성

```
┌─────────────────────────────────────────────────────────────────┐
│  Android App Auto Tester                              [─][□][×] │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌───────────────────────────────────────────┐ │
│  │   메뉴      │  │                                           │ │
│  │             │  │              메인 컨텐츠 영역               │ │
│  │ • 앱 선택   │  │                                           │ │
│  │ • 테스트    │  │   (앱 선택 / 테스트 진행 / 결과 표시)       │ │
│  │ • 결과      │  │                                           │ │
│  │ • 설정      │  │                                           │ │
│  │             │  │                                           │ │
│  └─────────────┘  └───────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  상태바: 디바이스 연결 상태 | 선택된 앱: 5개 | 마지막 테스트: ... │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 GUI 모듈 상세 설계

#### 5.3.1 gui/main_window.py - 메인 윈도우

```python
class MainWindow(ctk.CTk):
    """
    메인 애플리케이션 윈도우
    
    Attributes:
        device_manager: DeviceManager
        config_manager: ConfigManager
        current_frame: ctk.CTkFrame    # 현재 표시 중인 프레임
    
    Methods:
        __init__()
            - 윈도우 초기화
            - 메뉴 생성
            - 상태바 생성
        
        show_app_selector()
            - 앱 선택 화면으로 전환
        
        show_test_progress()
            - 테스트 진행 화면으로 전환
        
        show_results()
            - 결과 화면으로 전환
        
        show_settings()
            - 설정 화면으로 전환
        
        update_status_bar(message: str)
            - 상태바 업데이트
        
        on_device_connected()
            - 디바이스 연결 시 콜백
        
        on_device_disconnected()
            - 디바이스 연결 해제 시 콜백
    """
```

#### 5.3.2 gui/app_selector.py - 앱 선택 화면

```python
@dataclass
class InstalledApp:
    """설치된 앱 정보"""
    package: str                 # 패키지명
    app_name: str               # 앱 이름 (표시용)
    version: str                # 버전
    is_system: bool             # 시스템 앱 여부
    icon: Image | None          # 앱 아이콘 (선택적)

class AppSelectorFrame(ctk.CTkFrame):
    """
    앱 선택 화면
    
    ┌─────────────────────────────────────────────────────────────┐
    │  [🔄 새로고침]  [시스템 앱 표시 ☐]  검색: [___________🔍]  │
    ├─────────────────────────────────────────────────────────────┤
    │  ☐ │ 아이콘 │ 앱 이름          │ 패키지명              │ 버전 │
    ├─────────────────────────────────────────────────────────────┤
    │  ☑ │  📱   │ My App 1         │ com.example.app1      │ 1.0  │
    │  ☑ │  📱   │ My App 2         │ com.example.app2      │ 2.1  │
    │  ☐ │  📱   │ Calculator       │ com.android.calc      │ 1.0  │
    │  ...                                                        │
    ├─────────────────────────────────────────────────────────────┤
    │  선택됨: 2개    [전체 선택] [전체 해제] [선택 항목 저장]     │
    │                                                             │
    │  테스트 시간: [120 ▼] 초/앱    [▶ 테스트 시작]              │
    └─────────────────────────────────────────────────────────────┘
    
    Attributes:
        device_manager: DeviceManager
        installed_apps: list[InstalledApp]
        selected_apps: set[str]         # 선택된 패키지명 집합
        
    Methods:
        refresh_app_list()
            - 디바이스에서 설치된 앱 목록 새로고침
            - 백그라운드 스레드에서 실행
        
        _fetch_installed_apps() -> list[InstalledApp]
            - ADB로 설치된 앱 목록 조회
            - 앱 이름, 버전 정보 함께 가져오기
        
        _fetch_app_icon(package: str) -> Image | None
            - 앱 아이콘 가져오기 (선택적)
        
        filter_apps(search_text: str, show_system: bool)
            - 검색어와 필터로 앱 목록 필터링
        
        select_app(package: str)
            - 앱 선택
        
        deselect_app(package: str)
            - 앱 선택 해제
        
        select_all()
            - 전체 선택
        
        deselect_all()
            - 전체 해제
        
        save_selection()
            - 선택한 앱을 config/apps.json에 저장
        
        load_selection()
            - config/apps.json에서 이전 선택 로드
        
        start_test()
            - 선택된 앱으로 테스트 시작
            - TestProgressFrame으로 전환
    """
```

#### 5.3.3 gui/test_progress.py - 테스트 진행 화면

```python
class TestProgressFrame(ctk.CTkFrame):
    """
    테스트 진행 상황 표시 화면
    
    ┌─────────────────────────────────────────────────────────────┐
    │                    테스트 진행 중                            │
    ├─────────────────────────────────────────────────────────────┤
    │  전체 진행률: ████████████░░░░░░░░ 60% (6/10 앱)            │
    │                                                             │
    │  현재 테스트: My App 3 (com.example.app3)                   │
    │  앱 진행률:   ██████████████░░░░░░ 70% (84/120초)           │
    │                                                             │
    │  ┌─────────────────────────────────────────────────────┐   │
    │  │              실시간 스크린샷 미리보기                 │   │
    │  │                                                     │   │
    │  │                    [ 📱 ]                           │   │
    │  │                                                     │   │
    │  └─────────────────────────────────────────────────────┘   │
    │                                                             │
    │  로그:                                                      │
    │  ┌─────────────────────────────────────────────────────┐   │
    │  │ [14:30:01] 앱 실행 완료                              │   │
    │  │ [14:30:05] 버튼 클릭: btn_login                      │   │
    │  │ [14:30:08] 화면 전환 감지                            │   │
    │  │ [14:30:12] 스크롤 수행                               │   │
    │  └─────────────────────────────────────────────────────┘   │
    │                                                             │
    │  [⏸ 일시정지]  [⏹ 중지]  [📋 로그 복사]                    │
    └─────────────────────────────────────────────────────────────┘
    
    Attributes:
        test_runner: TestRunner
        is_running: bool
        is_paused: bool
        current_app: AppConfig
        
    Methods:
        start_test(apps: list[AppConfig])
            - 테스트 시작 (백그라운드 스레드)
        
        pause_test()
            - 테스트 일시정지
        
        resume_test()
            - 테스트 재개
        
        stop_test()
            - 테스트 중지
        
        update_progress(app_index: int, app_progress: float)
            - 진행률 업데이트
        
        update_screenshot(image: Image)
            - 스크린샷 미리보기 업데이트
        
        append_log(message: str)
            - 로그 메시지 추가
        
        on_test_complete(result: TestSessionResult)
            - 테스트 완료 시 콜백
            - 결과 화면으로 전환
        
        on_app_complete(app_result: AppTestResult)
            - 개별 앱 테스트 완료 시 콜백
        
        on_error(error: Exception)
            - 에러 발생 시 콜백
    """
```

#### 5.3.4 gui/settings_panel.py - 설정 패널

```python
class SettingsFrame(ctk.CTkFrame):
    """
    설정 화면
    
    ┌─────────────────────────────────────────────────────────────┐
    │                        설정                                  │
    ├─────────────────────────────────────────────────────────────┤
    │  테스트 설정                                                 │
    │  ├─ 기본 테스트 시간: [120    ] 초                          │
    │  ├─ 앱 간 대기 시간:  [5      ] 초                          │
    │  ├─ 최대 재시도 횟수: [3      ] 회                          │
    │  └─ 탐색 전략:        [랜덤   ▼]                            │
    │                                                             │
    │  스크린샷 설정                                               │
    │  ├─ 에러 시 스크린샷:    [✓]                                │
    │  ├─ 정기 스크린샷 간격:  [30     ] 초 (0=비활성화)           │
    │  └─ 저장 경로:          [screenshots/        ] [찾아보기]   │
    │                                                             │
    │  로그 설정                                                   │
    │  ├─ Logcat 수집:        [✓]                                │
    │  └─ 로그 레벨:          [✓]E [✓]W [✓]F [ ]I [ ]D           │
    │                                                             │
    │  디바이스                                                    │
    │  ├─ 연결 상태:          🟢 Galaxy S23 (Android 14)          │
    │  └─ [🔄 재연결]  [📋 디바이스 정보]                         │
    │                                                             │
    │                    [기본값 복원]  [저장]                     │
    └─────────────────────────────────────────────────────────────┘
    
    Methods:
        load_settings()
            - settings.json에서 설정 로드
        
        save_settings()
            - settings.json에 설정 저장
        
        reset_to_defaults()
            - 기본값으로 복원
        
        refresh_device_status()
            - 디바이스 연결 상태 새로고침
        
        reconnect_device()
            - 디바이스 재연결 시도
    """
```

#### 5.3.5 gui/results_viewer.py - 결과 뷰어

```python
class ResultsFrame(ctk.CTkFrame):
    """
    테스트 결과 화면
    
    ┌─────────────────────────────────────────────────────────────┐
    │                     테스트 결과                              │
    ├─────────────────────────────────────────────────────────────┤
    │  세션: 2025-02-04 14:30:00                                  │
    │  요약: 총 10개 앱 | ✅ 8개 성공 | ❌ 2개 에러               │
    │                                                             │
    │  ┌───────────────────────────────────────────────────────┐ │
    │  │ 앱 목록                      │ 상세 정보              │ │
    │  │ ┌─────────────────────────┐  │ ┌──────────────────┐  │ │
    │  │ │ ✅ My App 1             │  │ │ My App 1         │  │ │
    │  │ │ ✅ My App 2             │  │ │                  │  │ │
    │  │ │ ❌ My App 3 ◀          │  │ │ 상태: 에러 발견   │  │ │
    │  │ │ ✅ My App 4             │  │ │ 시간: 2분 3초    │  │ │
    │  │ │ ...                     │  │ │                  │  │ │
    │  │ └─────────────────────────┘  │ │ 에러:            │  │ │
    │  │                              │ │ • NullPointer... │  │ │
    │  │                              │ │                  │  │ │
    │  │                              │ │ [스크린샷 보기]  │  │ │
    │  │                              │ └──────────────────┘  │ │
    │  └───────────────────────────────────────────────────────┘ │
    │                                                             │
    │  [📄 리포트 열기]  [📁 폴더 열기]  [🔄 다시 테스트]         │
    └─────────────────────────────────────────────────────────────┘
    
    Attributes:
        session_result: TestSessionResult
        
    Methods:
        load_result(session_result: TestSessionResult)
            - 테스트 결과 로드 및 표시
        
        show_app_detail(app_result: AppTestResult)
            - 선택한 앱의 상세 정보 표시
        
        open_report()
            - 생성된 리포트 파일 열기
        
        open_folder()
            - 리포트/스크린샷 폴더 열기
        
        retest_failed()
            - 실패한 앱만 다시 테스트
    """
```

### 5.4 GUI 이벤트 흐름

```
[앱 시작]
    │
    ▼
[MainWindow 생성]
    │
    ├─── 디바이스 연결 확인
    │         │
    │         ├─ 연결됨 → 상태바 업데이트, 앱 선택 화면
    │         └─ 미연결 → 연결 대기 다이얼로그
    │
    ▼
[AppSelectorFrame]
    │
    ├─── [새로고침] → 설치된 앱 목록 로드
    ├─── [앱 선택] → selected_apps 업데이트
    ├─── [저장] → apps.json 저장
    └─── [테스트 시작]
              │
              ▼
[TestProgressFrame]
    │
    ├─── 테스트 진행 (백그라운드 스레드)
    │         │
    │         ├─ 진행률 업데이트 (UI 스레드)
    │         ├─ 스크린샷 업데이트 (UI 스레드)
    │         └─ 로그 추가 (UI 스레드)
    │
    ├─── [일시정지/재개]
    ├─── [중지] → 확인 다이얼로그
    └─── 테스트 완료
              │
              ▼
[ResultsFrame]
    │
    ├─── 결과 요약 표시
    ├─── 앱별 상세 정보
    ├─── [리포트 열기]
    └─── [다시 테스트] → AppSelectorFrame
```

### 5.5 스레딩 모델

```
┌─────────────────────────────────────────────────────────────┐
│                       Main Thread (UI)                      │
│                                                             │
│  - 모든 UI 업데이트                                          │
│  - 사용자 입력 처리                                          │
│  - 이벤트 루프                                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Queue / Callback
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Worker Thread                            │
│                                                             │
│  - 앱 목록 로드 (ADB 호출)                                   │
│  - 테스트 실행                                               │
│  - 로그 수집                                                 │
│  - 스크린샷 촬영                                             │
└─────────────────────────────────────────────────────────────┘

UI 업데이트 방법:
- window.after(0, callback) 사용
- Queue를 통한 메시지 전달
- 스레드 안전한 콜백 패턴
```

---

## 5. 데이터 흐름

### 5.1 테스트 실행 데이터 흐름
```
[apps.json] ──▶ [ConfigManager] ──▶ [TestRunner]
                                         │
                                         ▼
                               ┌─────────────────┐
                               │   앱 1 테스트    │
                               │                 │
[settings.json] ──────────────▶│ DeviceManager   │
                               │ UIExplorer      │
                               │ LogCollector    │
                               │                 │
                               └────────┬────────┘
                                        │
                                        ▼
                               ┌─────────────────┐
                               │   앱 2 테스트    │
                               │      ...        │
                               └────────┬────────┘
                                        │
                                        ▼
                               [TestSessionResult]
                                        │
                                        ▼
                               [ReportGenerator]
                                        │
                                        ▼
                               [report_YYYYMMDD.md]
```

### 5.2 에러 감지 데이터 흐름
```
[Android Device]
      │
      ├── logcat ──────────▶ [LogCollector] ──▶ [에러 필터링]
      │                                               │
      ├── UI 상태 ─────────▶ [UIExplorer] ───▶ [다이얼로그 감지]
      │                                               │
      └── ANR 파일 ────────▶ [LogCollector] ──▶ [ANR 감지]
                                                      │
                                                      ▼
                                              [AppTestResult.errors]
```

---

## 6. 에러 처리

### 6.1 에러 유형 및 처리 방법

| 에러 유형 | 감지 방법 | 처리 방법 |
|----------|----------|----------|
| 앱 크래시 | logcat FATAL EXCEPTION | 스크린샷 저장, 스택트레이스 기록, 다음 앱으로 진행 |
| ANR | logcat ANR 태그 | 스크린샷 저장, 앱 강제 종료, 다음 앱으로 진행 |
| UI 에러 다이얼로그 | "Unfortunately" 텍스트 감지 | 스크린샷 저장, 다이얼로그 닫기 시도 |
| 앱 미응답 | 화면 변화 없음 (30초) | 앱 강제 종료, 재시도 또는 스킵 |
| ADB 연결 끊김 | adb devices 실패 | 재연결 시도 (3회), 실패 시 테스트 중단 |

### 6.2 재시도 정책
```python
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

def run_with_retry(func, *args):
    for attempt in range(MAX_RETRIES):
        try:
            return func(*args)
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                raise
```

---

## 7. 로깅 설계

### 7.1 로그 레벨
| 레벨 | 용도 |
|------|------|
| DEBUG | 상세한 디버깅 정보 |
| INFO | 일반적인 진행 상황 |
| WARNING | 주의가 필요한 상황 |
| ERROR | 에러 발생 |
| CRITICAL | 치명적 오류 |

### 7.2 로그 형식
```
[2025-02-04 14:30:45] [INFO] [TestRunner] 앱 테스트 시작: com.example.app1
[2025-02-04 14:30:48] [DEBUG] [UIExplorer] 클릭 가능한 요소 15개 발견
[2025-02-04 14:31:02] [WARNING] [LogCollector] ANR 감지됨
[2025-02-04 14:31:05] [ERROR] [DeviceManager] 앱 크래시 발생
```

### 7.3 로그 파일 저장
- 경로: `logs/test_YYYYMMDD_HHMMSS.log`
- 보관 기간: 최근 30일

---

## 8. 명령줄 인터페이스

### 8.1 사용법
```bash
# 모든 앱 테스트
python main.py

# 특정 앱만 테스트
python main.py --app com.example.app1

# 여러 앱 지정
python main.py --app com.example.app1 --app com.example.app2

# 테스트 시간 조정
python main.py --duration 300

# 상세 로그 출력
python main.py --verbose

# 설정 파일 지정
python main.py --config /path/to/apps.json

# 도움말
python main.py --help
```

### 8.2 종료 코드
| 코드 | 의미 |
|------|------|
| 0 | 모든 테스트 성공 |
| 1 | 일부 테스트 에러 |
| 2 | 디바이스 연결 실패 |
| 3 | 설정 파일 오류 |
| 4 | 치명적 오류 |

---

## 9. 확장 계획 (향후)

### 9.1 Phase 2 기능
- [ ] 스케줄러 연동 (cron / Windows Task Scheduler)
- [ ] 이메일 알림 기능
- [ ] Slack 알림 기능
- [ ] HTML 리포트 생성

### 9.2 Phase 3 기능
- [ ] 이전 테스트와 결과 비교 (회귀 테스트)
- [ ] 성능 메트릭 수집 (CPU, 메모리, 배터리)
- [ ] 다중 디바이스 동시 테스트
- [ ] 웹 대시보드

---

## 10. 참고 자료

### 10.1 공식 문서
- [uiautomator2 GitHub](https://github.com/openatx/uiautomator2)
- [Android ADB 문서](https://developer.android.com/studio/command-line/adb)
- [Python subprocess](https://docs.python.org/3/library/subprocess.html)

### 10.2 관련 명령어
```bash
# ADB 기본 명령어
adb devices                           # 연결된 디바이스 목록
adb shell pm list packages            # 설치된 패키지 목록
adb shell am start -n {pkg}/{activity} # 앱 실행
adb shell am force-stop {pkg}         # 앱 종료
adb logcat -c                         # logcat 클리어
adb logcat *:E                        # 에러만 출력
adb shell screencap /sdcard/screen.png # 스크린샷
adb pull /sdcard/screen.png ./        # 파일 가져오기
```
