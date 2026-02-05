# Android App Auto Tester - TODO 리스트

## 프로젝트 정보
- **프로젝트명**: Android App Auto Tester
- **목적**: Google Play 비공개 테스트 자동화
- **개발 환경**: Windows / Ubuntu, VS Code, Python 3.8+

---

## 📋 개발 진행 체크리스트

### Phase 0: 프로젝트 초기 설정
> 예상 소요 시간: 30분

- [ ] **P0-1**: 프로젝트 디렉토리 구조 생성
  ```
  android-app-tester/
  ├── docs/
  ├── config/
  ├── src/
  ├── templates/
  ├── reports/
  ├── screenshots/
  └── logs/
  ```

- [ ] **P0-2**: requirements.txt 생성
  ```
  uiautomator2>=2.16.0
  Pillow>=9.0.0
  Jinja2>=3.0.0
  ```

- [ ] **P0-3**: .gitignore 생성
  ```
  __pycache__/
  *.pyc
  reports/*.md
  screenshots/*.png
  logs/*.log
  .venv/
  ```

- [ ] **P0-4**: README.md 작성
  - 프로젝트 소개
  - 설치 방법 (Windows/Ubuntu)
  - 사용 방법
  - 설정 파일 설명

- [ ] **P0-5**: setup_windows.bat 작성
  - Python 패키지 설치
  - uiautomator2 init
  - ADB 확인

- [ ] **P0-6**: setup_ubuntu.sh 작성
  - apt 패키지 설치
  - Python 패키지 설치
  - uiautomator2 init
  - USB 권한 설정 안내

---

### Phase 1: 플랫폼 유틸리티 및 설정 관리
> 예상 소요 시간: 2-3시간

- [ ] **P1-1**: `src/__init__.py` 생성

- [ ] **P1-2**: `src/platform_utils.py` 구현
  - [ ] PlatformUtils 클래스 생성
  - [ ] OS 감지 기능 (Windows/Linux)
  - [ ] ADB 명령어 경로 반환
  - [ ] 프로젝트 경로 관리 (screenshots, reports, logs, config)
  - [ ] 디렉토리 자동 생성
  - [ ] 시스템 명령어 실행 래퍼 (subprocess)

- [ ] **P1-3**: `src/config_manager.py` 구현
  - [ ] AppConfig 데이터클래스 정의
  - [ ] GlobalSettings 데이터클래스 정의
  - [ ] ConfigManager 클래스 생성
  - [ ] apps.json 로드 기능
  - [ ] settings.json 로드 기능
  - [ ] 설정 유효성 검사

- [ ] **P1-4**: `config/apps.json` 샘플 생성
  ```json
  {
    "apps": [
      {
        "name": "샘플 앱",
        "package": "com.example.app",
        "activity": ".MainActivity",
        "test_duration": 120,
        "test_actions": ["scroll", "click_buttons"]
      }
    ]
  }
  ```

- [ ] **P1-5**: `config/settings.json` 샘플 생성
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

- [ ] **P1-6**: 단위 테스트
  - [ ] PlatformUtils 테스트
  - [ ] ConfigManager 테스트

---

### Phase 2: 디바이스 관리
> 예상 소요 시간: 2-3시간

- [ ] **P2-1**: `src/device_manager.py` 구현
  - [ ] DeviceInfo 데이터클래스 정의
  - [ ] DeviceManager 클래스 생성
  - [ ] ADB 연결 확인 기능
  - [ ] uiautomator2 디바이스 연결
  - [ ] 디바이스 정보 조회 (모델, Android 버전)
  - [ ] 앱 실행 기능 (am start)
  - [ ] 앱 종료 기능 (am force-stop)
  - [ ] 앱 실행 상태 확인
  - [ ] 스크린샷 촬영 기능
  - [ ] 현재 액티비티 조회

- [ ] **P2-2**: 연결 에러 처리
  - [ ] ADB 연결 실패 시 재시도
  - [ ] 디바이스 미인식 에러 메시지
  - [ ] USB 디버깅 미활성화 안내

- [ ] **P2-3**: 단위 테스트
  - [ ] 디바이스 연결 테스트
  - [ ] 앱 실행/종료 테스트

---

### Phase 3: UI 자동 탐색
> 예상 소요 시간: 4-5시간

- [ ] **P3-1**: `src/ui_explorer.py` 구현
  - [ ] UIElement 데이터클래스 정의
  - [ ] ExplorationResult 데이터클래스 정의
  - [ ] UIExplorer 클래스 생성

- [ ] **P3-2**: UI 요소 탐지 기능
  - [ ] 현재 화면의 모든 요소 가져오기
  - [ ] 클릭 가능한 요소 필터링
  - [ ] 스크롤 가능한 요소 필터링
  - [ ] 텍스트 입력 필드 필터링

- [ ] **P3-3**: UI 동작 구현
  - [ ] 요소 클릭 (click_element)
  - [ ] 화면 스크롤 (scroll_screen)
  - [ ] 텍스트 입력 (input_text)
  - [ ] 뒤로가기 (press_back)
  - [ ] 홈 버튼 (press_home)

- [ ] **P3-4**: 자동 탐색 알고리즘
  - [ ] 화면 서명 생성 (중복 방문 체크)
  - [ ] 방문한 화면 기록
  - [ ] 탐색 전략 (BFS/DFS/랜덤)
  - [ ] 막다른 화면 감지 및 뒤로가기
  - [ ] 탐색 시간 제한

- [ ] **P3-5**: 에러 감지
  - [ ] 에러 다이얼로그 감지 ("Unfortunately", "stopped")
  - [ ] 앱 비정상 종료 감지
  - [ ] 화면 프리즈 감지

- [ ] **P3-6**: 단위 테스트
  - [ ] UI 요소 탐지 테스트
  - [ ] 각 동작 테스트

---

### Phase 4: 로그 수집
> 예상 소요 시간: 2-3시간

- [ ] **P4-1**: `src/log_collector.py` 구현
  - [ ] LogEntry 데이터클래스 정의
  - [ ] CrashInfo 데이터클래스 정의
  - [ ] LogCollector 클래스 생성

- [ ] **P4-2**: logcat 수집 기능
  - [ ] logcat 시작 (백그라운드)
  - [ ] logcat 중지
  - [ ] 특정 패키지 필터링
  - [ ] 로그 레벨 필터링 (E, W, F)

- [ ] **P4-3**: 에러 분석 기능
  - [ ] 에러 로그 추출
  - [ ] 경고 로그 추출
  - [ ] FATAL EXCEPTION 감지 (크래시)
  - [ ] ANR 감지
  - [ ] 스택트레이스 파싱

- [ ] **P4-4**: 성능 정보 수집
  - [ ] 메모리 사용량 조회 (dumpsys meminfo)
  - [ ] CPU 사용량 조회 (선택적)

- [ ] **P4-5**: 단위 테스트
  - [ ] logcat 파싱 테스트
  - [ ] 에러 감지 테스트

---

### Phase 5: 테스트 실행 엔진
> 예상 소요 시간: 3-4시간

- [ ] **P5-1**: `src/test_runner.py` 구현
  - [ ] AppTestResult 데이터클래스 정의
  - [ ] TestSessionResult 데이터클래스 정의
  - [ ] TestRunner 클래스 생성

- [ ] **P5-2**: 테스트 실행 흐름
  - [ ] run_all_tests() - 전체 테스트 실행
  - [ ] run_single_app_test() - 단일 앱 테스트
  - [ ] _prepare_test() - 테스트 준비
  - [ ] _execute_test() - 테스트 실행
  - [ ] _collect_results() - 결과 수집
  - [ ] _cleanup_test() - 정리

- [ ] **P5-3**: 에러 처리 및 재시도
  - [ ] 앱 크래시 시 처리
  - [ ] ANR 시 처리
  - [ ] 타임아웃 처리
  - [ ] 재시도 로직 (최대 3회)

- [ ] **P5-4**: 개선 제안 생성
  - [ ] 에러 기반 제안
  - [ ] 성능 기반 제안
  - [ ] UI 접근성 제안

- [ ] **P5-5**: 진행 상황 출력
  - [ ] 콘솔 진행률 표시
  - [ ] 현재 테스트 중인 앱 표시
  - [ ] 예상 남은 시간

---

### Phase 6: 리포트 생성
> 예상 소요 시간: 2-3시간

- [ ] **P6-1**: `templates/report_template.md` 생성
  - 헤더 (날짜, 디바이스 정보)
  - 요약 섹션
  - 앱별 상세 결과
  - 에러 목록
  - 개선 제안
  - 스크린샷 섹션

- [ ] **P6-2**: `src/report_generator.py` 구현
  - [ ] ReportGenerator 클래스 생성
  - [ ] Jinja2 템플릿 로드
  - [ ] 리포트 렌더링
  - [ ] 파일 저장 (reports/report_YYYYMMDD_HHMMSS.md)

- [ ] **P6-3**: 리포트 내용 구성
  - [ ] 요약 섹션 렌더링
  - [ ] 앱별 상세 결과 렌더링
  - [ ] 에러 섹션 렌더링
  - [ ] 개선 제안 섹션 렌더링
  - [ ] 스크린샷 경로 처리

- [ ] **P6-4**: 스크린샷 관리
  - [ ] 리포트 전용 폴더 생성
  - [ ] 스크린샷 복사
  - [ ] 상대 경로로 리포트에 삽입

---

### Phase 7: 메인 실행 파일
> 예상 소요 시간: 2-3시간

- [ ] **P7-1**: `main.py` 구현
  - [ ] argparse로 CLI 인터페이스 구현
  - [ ] 로깅 설정
  - [ ] 메인 실행 흐름

- [ ] **P7-2**: CLI 옵션 구현
  ```
  --app PACKAGE       특정 앱만 테스트
  --duration SECONDS  테스트 시간 조정
  --config PATH       설정 파일 경로
  --verbose           상세 로그 출력
  --dry-run           실제 테스트 없이 설정 확인
  --help              도움말
  ```

- [ ] **P7-3**: 종료 코드 처리
  - [ ] 0: 성공
  - [ ] 1: 일부 에러
  - [ ] 2: 디바이스 연결 실패
  - [ ] 3: 설정 오류
  - [ ] 4: 치명적 오류

- [ ] **P7-4**: 전체 통합 테스트
  - [ ] Windows에서 테스트
  - [ ] Ubuntu에서 테스트

---

### Phase 8: GUI 개발 - 메인 윈도우
> 예상 소요 시간: 2-3시간

- [ ] **P8-1**: `gui/__init__.py` 생성

- [ ] **P8-2**: `gui/main_window.py` 구현
  - [ ] MainWindow 클래스 생성 (customtkinter 기반)
  - [ ] 윈도우 크기, 제목 설정
  - [ ] 좌측 메뉴 (네비게이션) 구현
  - [ ] 메인 컨텐츠 영역 프레임
  - [ ] 하단 상태바 구현
  - [ ] 화면 전환 메서드 (show_app_selector, show_test_progress 등)

- [ ] **P8-3**: 디바이스 연결 상태 표시
  - [ ] 연결 상태 아이콘 (🟢/🔴)
  - [ ] 디바이스 정보 표시
  - [ ] 연결/해제 감지 콜백

---

### Phase 9: GUI 개발 - 앱 선택 화면
> 예상 소요 시간: 3-4시간

- [ ] **P9-1**: `gui/app_selector.py` 구현
  - [ ] AppSelectorFrame 클래스 생성
  - [ ] 상단 툴바 (새로고침, 필터, 검색)
  - [ ] 앱 목록 테이블/리스트 구현
  - [ ] 체크박스로 앱 선택

- [ ] **P9-2**: 앱 목록 로드 기능
  - [ ] ADB로 설치된 앱 목록 조회
  - [ ] 앱 이름 가져오기 (aapt 또는 dumpsys)
  - [ ] 백그라운드 스레드에서 로드
  - [ ] 로딩 인디케이터 표시

- [ ] **P9-3**: 앱 필터링 기능
  - [ ] 검색어로 필터링
  - [ ] 시스템 앱 표시/숨김 토글
  - [ ] 서드파티 앱만 표시 옵션

- [ ] **P9-4**: 선택 관리
  - [ ] 전체 선택 / 전체 해제
  - [ ] 선택된 앱 수 표시
  - [ ] 선택 상태 apps.json에 저장
  - [ ] 이전 선택 상태 로드

- [ ] **P9-5**: 테스트 시작 버튼
  - [ ] 테스트 시간 입력
  - [ ] 테스트 시작 시 TestProgressFrame으로 전환

---

### Phase 10: GUI 개발 - 테스트 진행 화면
> 예상 소요 시간: 3-4시간

- [ ] **P10-1**: `gui/test_progress.py` 구현
  - [ ] TestProgressFrame 클래스 생성
  - [ ] 전체 진행률 바
  - [ ] 현재 앱 진행률 바
  - [ ] 현재 테스트 중인 앱 정보 표시

- [ ] **P10-2**: 실시간 스크린샷 미리보기
  - [ ] 스크린샷 표시 영역
  - [ ] 주기적 업데이트 (5초마다)
  - [ ] 이미지 리사이즈

- [ ] **P10-3**: 로그 영역
  - [ ] 스크롤 가능한 로그 텍스트 영역
  - [ ] 자동 스크롤 (최신 로그로)
  - [ ] 로그 복사 버튼

- [ ] **P10-4**: 제어 버튼
  - [ ] 일시정지/재개 버튼
  - [ ] 중지 버튼 (확인 다이얼로그)

- [ ] **P10-5**: 테스트 실행 연동
  - [ ] TestRunner를 백그라운드 스레드에서 실행
  - [ ] 진행 상황 콜백으로 UI 업데이트
  - [ ] 테스트 완료 시 결과 화면으로 전환

---

### Phase 11: GUI 개발 - 결과 화면 및 설정
> 예상 소요 시간: 2-3시간

- [ ] **P11-1**: `gui/results_viewer.py` 구현
  - [ ] ResultsFrame 클래스 생성
  - [ ] 요약 정보 표시
  - [ ] 앱별 결과 목록 (성공/실패 아이콘)
  - [ ] 선택한 앱 상세 정보 패널

- [ ] **P11-2**: 결과 상세 기능
  - [ ] 에러 메시지 표시
  - [ ] 스크린샷 보기 버튼
  - [ ] 리포트 열기 버튼
  - [ ] 폴더 열기 버튼

- [ ] **P11-3**: `gui/settings_panel.py` 구현
  - [ ] SettingsFrame 클래스 생성
  - [ ] 테스트 설정 입력 필드
  - [ ] 스크린샷 설정
  - [ ] 로그 설정
  - [ ] 디바이스 정보 표시

- [ ] **P11-4**: 설정 저장/로드
  - [ ] settings.json 연동
  - [ ] 기본값 복원 버튼
  - [ ] 저장 버튼

---

### Phase 12: GUI 메인 실행 파일
> 예상 소요 시간: 1-2시간

- [ ] **P12-1**: `main_gui.py` 구현
  - [ ] GUI 애플리케이션 진입점
  - [ ] customtkinter 테마 설정
  - [ ] MainWindow 생성 및 실행

- [ ] **P12-2**: 에러 처리
  - [ ] 전역 예외 핸들러
  - [ ] 에러 다이얼로그 표시
  - [ ] 로그 파일 기록

- [ ] **P12-3**: 통합 테스트
  - [ ] Windows에서 GUI 테스트
  - [ ] Ubuntu에서 GUI 테스트
  - [ ] 전체 플로우 테스트

---

### Phase 13: 문서화 및 마무리
> 예상 소요 시간: 1-2시간

- [ ] **P8-1**: README.md 완성
  - [ ] 설치 가이드 (Windows/Ubuntu)
  - [ ] 빠른 시작 가이드
  - [ ] 설정 파일 설명
  - [ ] 자주 묻는 질문

- [ ] **P8-2**: 주석 및 docstring 추가
  - [ ] 모든 클래스에 docstring
  - [ ] 주요 함수에 docstring
  - [ ] 복잡한 로직에 주석

- [ ] **P8-3**: 최종 점검
  - [ ] 코드 정리 및 포맷팅
  - [ ] 불필요한 파일 제거
  - [ ] 테스트 실행 확인

---

## 🎯 바이브코딩 가이드

### 프롬프트 예시

각 태스크 진행 시 아래와 같은 형식으로 요청하세요:

```
P1-2 태스크를 진행해줘.

src/platform_utils.py 파일을 만들어줘.
- Windows와 Ubuntu 양쪽에서 동작해야 함
- ADB 명령어 경로를 OS에 맞게 반환
- subprocess로 명령어 실행하는 래퍼 함수 포함
- 프로젝트 경로 관리 (screenshots, reports, logs)
```

```
P3-4 태스크를 진행해줘.

UI 자동 탐색 알고리즘을 구현해줘.
- 화면별 고유 서명을 만들어서 중복 방문 체크
- 방문하지 않은 버튼을 우선 클릭
- 막다른 화면이면 뒤로가기로 돌아가기
- 지정된 시간(duration) 동안만 탐색
```

### 테스트 방법

```bash
# Windows
python main.py --dry-run          # 설정만 확인
python main.py --verbose          # 상세 로그로 실행
python main.py --app com.example.app  # 특정 앱만 테스트

# Ubuntu
python3 main.py --dry-run
python3 main.py --verbose
python3 main.py --app com.example.app
```

---

## 📊 진행 상황 요약

| Phase | 내용 | 태스크 | 완료 | 진행중 | 미시작 |
|-------|------|--------|------|--------|--------|
| 0 | 초기 설정 | 6 | 0 | 0 | 6 |
| 1 | 플랫폼/설정 | 6 | 0 | 0 | 6 |
| 2 | 디바이스 관리 | 3 | 0 | 0 | 3 |
| 3 | UI 탐색 | 6 | 0 | 0 | 6 |
| 4 | 로그 수집 | 5 | 0 | 0 | 5 |
| 5 | 테스트 엔진 | 5 | 0 | 0 | 5 |
| 6 | 리포트 생성 | 4 | 0 | 0 | 4 |
| 7 | CLI 메인 | 4 | 0 | 0 | 4 |
| 8 | GUI 메인윈도우 | 3 | 0 | 0 | 3 |
| 9 | GUI 앱선택 | 5 | 0 | 0 | 5 |
| 10 | GUI 테스트진행 | 5 | 0 | 0 | 5 |
| 11 | GUI 결과/설정 | 4 | 0 | 0 | 4 |
| 12 | GUI 메인 | 3 | 0 | 0 | 3 |
| 13 | 문서화 | 3 | 0 | 0 | 3 |
| **합계** | | **62** | **0** | **0** | **62** |

---

## 🔗 관련 문서

- [소프트웨어 설계서](./SOFTWARE_DESIGN.md)
- [README](../README.md)
