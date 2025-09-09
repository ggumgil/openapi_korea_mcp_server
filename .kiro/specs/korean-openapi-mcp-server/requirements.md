# Requirements Document

## Introduction

한국 공공 API를 활용한 MCP(Model Context Protocol) 서버는 AI 모델이 한국의 공공 데이터에 쉽게 접근할 수 있도록 하는 도구입니다. 현재 세종시의 주차장, 흡연구역, 음식점, CCTV 정보를 조회할 수 있는 기능을 제공하며, 향후 다른 지역 및 다양한 공공 API로 확장 가능한 구조를 가지고 있습니다.

## Requirements

### Requirement 1

**User Story:** AI 모델 사용자로서, 세종시 주차장 정보를 조회하고 싶어서, 위치별 주차 가능 여부와 요금 정보를 확인할 수 있어야 한다.

#### Acceptance Criteria

1. WHEN 사용자가 주차장 정보 조회를 요청하면 THEN 시스템은 세종시 주차장 목록을 반환해야 한다
2. WHEN 사용자가 검색 키워드를 제공하면 THEN 시스템은 해당 키워드와 일치하는 주차장만 필터링해서 반환해야 한다
3. WHEN 사용자가 페이지 번호와 페이지 크기를 지정하면 THEN 시스템은 해당 페이지의 결과만 반환해야 한다
4. WHEN 주차장 정보가 조회되면 THEN 시스템은 주차장명, 주소, 주차면수, 요금정보, 연락처, 운영시간을 포함해야 한다

### Requirement 2

**User Story:** AI 모델 사용자로서, 세종시 흡연구역 위치를 조회하고 싶어서, 지정된 흡연 구역의 위치와 관리 정보를 확인할 수 있어야 한다.

#### Acceptance Criteria

1. WHEN 사용자가 흡연구역 정보 조회를 요청하면 THEN 시스템은 세종시 흡연구역 목록을 반환해야 한다
2. WHEN 사용자가 장소명으로 검색하면 THEN 시스템은 해당 장소명과 일치하는 흡연구역만 반환해야 한다
3. WHEN 흡연구역 정보가 조회되면 THEN 시스템은 흡연구역명, 주소, 관리기관, 연락처를 포함해야 한다

### Requirement 3

**User Story:** AI 모델 사용자로서, 세종시 음식점 정보를 조회하고 싶어서, 지역 내 음식점의 위치와 메뉴 정보를 확인할 수 있어야 한다.

#### Acceptance Criteria

1. WHEN 사용자가 음식점 정보 조회를 요청하면 THEN 시스템은 세종시 음식점 목록을 반환해야 한다
2. WHEN 사용자가 상호명 또는 주소로 검색하면 THEN 시스템은 해당 조건과 일치하는 음식점만 반환해야 한다
3. WHEN 음식점 정보가 조회되면 THEN 시스템은 상호명, 주소, 주요메뉴, 연락처를 포함해야 한다

### Requirement 4

**User Story:** AI 모델 사용자로서, 세종시 CCTV 정보를 조회하고 싶어서, 보안 카메라의 위치와 설치 목적을 확인할 수 있어야 한다.

#### Acceptance Criteria

1. WHEN 사용자가 CCTV 정보 조회를 요청하면 THEN 시스템은 세종시 CCTV 목록을 반환해야 한다
2. WHEN 사용자가 도로명주소로 검색하면 THEN 시스템은 해당 주소와 일치하는 CCTV만 반환해야 한다
3. WHEN CCTV 정보가 조회되면 THEN 시스템은 설치 주소, 목적, 화소, 설치연도, 관리기관, 연락처를 포함해야 한다

### Requirement 5

**User Story:** 개발자로서, API 서비스 키를 안전하게 관리하고 싶어서, 환경변수나 설정 파일을 통해 키를 설정할 수 있어야 한다.

#### Acceptance Criteria

1. WHEN 시스템이 시작될 때 THEN 환경변수 OPENAPI_KOREA_SERVICE_KEY에서 서비스 키를 읽어야 한다
2. IF 환경변수가 없으면 THEN 시스템은 config.json 파일에서 serviceKey를 읽어야 한다
3. IF 서비스 키가 설정되지 않았으면 THEN 시스템은 경고 메시지를 출력하고 API 호출 시 오류를 반환해야 한다

### Requirement 6

**User Story:** AI 모델로서, 공공 API 호출 시 발생할 수 있는 오류를 처리하고 싶어서, 명확한 오류 메시지와 함께 실패 원인을 알 수 있어야 한다.

#### Acceptance Criteria

1. WHEN API 호출이 타임아웃되면 THEN 시스템은 "요청 시간 초과" 메시지를 반환해야 한다
2. WHEN API 응답이 잘못된 JSON 형식이면 THEN 시스템은 "응답 데이터 파싱 오류" 메시지를 반환해야 한다
3. WHEN API 호출이 실패하면 THEN 시스템은 구체적인 오류 내용을 포함한 메시지를 반환해야 한다
4. WHEN SSL 인증서 문제가 발생하면 THEN 시스템은 insecure 옵션을 사용하여 우회해야 한다

### Requirement 7

**User Story:** AI 모델로서, 조회된 데이터를 이해하기 쉽게 받고 싶어서, 구조화되고 포맷팅된 형태로 정보를 제공받을 수 있어야 한다.

#### Acceptance Criteria

1. WHEN 데이터가 조회되면 THEN 시스템은 이모지와 함께 가독성 좋은 형태로 포맷팅해야 한다
2. WHEN 여러 항목이 조회되면 THEN 시스템은 각 항목을 구분선으로 분리해서 표시해야 한다
3. WHEN 총 개수 정보가 있으면 THEN 시스템은 조회 결과 상단에 총 개수를 표시해야 한다
4. IF 데이터가 없거나 오류가 발생하면 THEN 시스템은 원본 JSON 데이터를 표시해야 한다

### Requirement 8

**User Story:** MCP 클라이언트로서, 사용 가능한 도구들을 확인하고 싶어서, 각 도구의 기능과 파라미터 정보를 조회할 수 있어야 한다.

#### Acceptance Criteria

1. WHEN 도구 목록을 요청하면 THEN 시스템은 4개의 도구(주차장, 흡연구역, 음식점, CCTV)를 반환해야 한다
2. WHEN 각 도구 정보를 조회하면 THEN 시스템은 도구명, 설명, 입력 스키마를 포함해야 한다
3. WHEN 입력 스키마를 확인하면 THEN 각 파라미터의 타입, 설명, 기본값, 제약조건을 포함해야 한다