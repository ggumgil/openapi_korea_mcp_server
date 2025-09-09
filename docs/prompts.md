# 프로젝트 진행 과정 - 사용자 프롬프트 모음

이 문서는 세종시 주차장 정보 조회 API 프로그램 개발 및 MCP 서버 구축 과정에서 사용된 모든 사용자 프롬프트를 시간순으로 정리한 것입니다.

## 1. 초기 요구사항 정의

### 프롬프트 1
``` 주차장정보 API에서 정보 가져오는 프롬프트
파이썬으로 RESTful API를 이용해서 정보를 가져와서 Json으로 보여주는 프로그램을 짜고 싶어. API 주소는 https://apis.data.go.kr/5690000/sjParkingLotInformation1/sj_00000949야. 그런데 Parameter가 필요한데, serviceKey=&pageIndex=1&pageUnit=20&dataTy=json&searchCondition=ty_Se&searchKeyword= 이런 형태로 넣어주려고 해. serviceKey는 민감정보여서 설정파일을 통해서 가져올 수 있게 해주면 좋겠어. 만들어줘 ( kiro claude-sonnet-4 )
```

### 프롬프트 3
```이 코드를 기준으로 해서 API를 통해 가져오는 데이터는 tool 말고 resource에서 처리할 수 있도록 해줘 ( claude sonnet 4)
```

### 프롬프트 4
```캐쉬된 데이터를 보여주는 tool을 추가해줘 ( gemini_cli 2.5 pro )
```
### 프롬프트 5
```지금 tool에서 키워드 검색이 안되는데 API 데이터에 있는 주소에서 검색을 해서 가져오게 해줘 ( gemini_cli 2.5 pro)
```
---

## 프로젝트 요약

이 프로젝트는 다음과 같은 단계로 진행되었습니다:


## 주요 성과

- ✅ 세종시 주차장 정보 조회 API 클라이언트 완성
- ✅ MCP 서버로 기능 확장
- ✅ 다양한 AI 도구에서 사용 가능한 통합 솔루션 구축
- ✅ 완전한 문서화 및 설정 가이드 제공

## 기술 스택

- **언어**: Python 3.8+
- **주요 라이브러리**: mcp, pydantic, requests, urllib3
- **프로토콜**: Model Context Protocol (MCP)
- **API**: 공공데이터포털 세종시 주차장 정보 API
- **플랫폼**: macOS (M1 최적화), Kiro IDE, Gemini CLI