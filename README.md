## mcp 실행 방법

1. python 가상환경 생성
   - python3 -m venv venv
   - 가상환경 진입
     - 윈도우 : venv\Scripts\activate.bat
     - 맥 : source venv/bin/activate
2.  mcp, pydantic 패키지 설치
   - pip install mcp pydantic
3. openapi_mcp_server 폴더 아래에서 python3 -m venv venv 실행하세요.
4. pip install mcp pydantic을 실행하세요.
5. python3 .\src\openapi_korea\server.py를 실행합니다.
6. 그럼 OpenAPI Korea MCP Sever가 시작되었다는 메시지가 나옵니다.
7. python3 .\test_mcp_server.py를 실행합니다.
8. 테스트 결과 요약이 나오면 정상 작동 확인입니다.
9.  다른 LLM에 연결하는 것은 추가 후 다시 말씀드리겠습니다.
10. 테스트 해보실 분은 한 번 해보시고 공유 부탁드립니다!
    

## Problem:
1. python.exe 실행 파일이 여러 곳에 있어 어떤 실행파일이 실행되는지 모르는 경우가 있습니다. 따라서 적절한 package가 설치된 환경의 python으로 파일을 실행해야 합니다.


## mcp server LLM 연결 (윈도우 버전) - gemini_cli 
1. gemini_cli를 실행해주세요. 구글 계정이 있으면 일정 토큰까지 무료로 사용할 수 있습니다.
   - gemini_cli가 설치되어 있지 않을 경우
     - node.js를 설치합니다. 버전 18 이상 - 최신을 설치하세요.
     - npm install -g @google/gemini-cli 실행
     - 구글 계정 인증
2. mcp server 설정
   - .gemini 폴더 아래 settings.json 파일을 열어주세요.
   - OPENAPI_KOREA_SERVICE_KEY 항목에 있는 your_api_key를 공공데이터포털에서 받은 API_KEY 값으로 변경해주세요.
3. openapi_mcp_server 코드가 있는 곳에서 gemini 실행
   - 화면에 Using : 1 MCP Server (ctrl+t to view) 가 나오는지 확인해주세요.
   - 있다면 ctrl+t를 눌러서 mcp server 정보를 확인해주세요.
   - 프롬프트에 '세종시에서 주차장 정보를 조회해줘'라고 입력해주세요.
   - get_sejong_parking_info (openapi-korea MCP Server)가 나오면 성공입니다.


## Problem:
1. 이번에 참여하신 분 중에 윈도우 사용하시는 분이 많아 윈도우 버전으로 진행했습니다. 맥을 쓰시는 분은 차후 필요하시다면 다시 작성해보도록 하겠습니다.


