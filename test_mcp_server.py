#!/usr/bin/env python3
"""
MCP Server 테스트 스크립트
"""

import asyncio
import json
import sys
import os
from src.openapi_korea.server import KoreanOpenAPIClient, format_parking_info

async def test_api_client():
    """API 클라이언트 직접 테스트"""
    print("🧪 API 클라이언트 테스트 시작...")
    
    # 설정 파일에서 API 키 로드
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            service_key = config.get('serviceKey')
    except (FileNotFoundError, json.JSONDecodeError):
        print("❌ config.json 파일을 찾을 수 없거나 형식이 잘못되었습니다.")
        return False
    
    if not service_key or service_key == "YOUR_SERVICE_KEY_HERE":
        print("❌ 유효한 서비스 키가 설정되지 않았습니다.")
        return False
    
    # API 클라이언트 생성
    client = KoreanOpenAPIClient(service_key)
    
    try:
        print("📡 세종시 주차장 정보 조회 중...")
        result = await client.get_sejong_parking_info(
            page_index=1,
            page_unit=5,  # 테스트용으로 5개만
            search_keyword=""
        )
        
        if result:
            print("✅ API 호출 성공!")
            formatted = format_parking_info(result)
            print("\n" + "="*50)
            print("포맷팅된 결과:")
            print("="*50)
            print(formatted)
            return True
        else:
            print("❌ API 호출 실패 - 결과가 None입니다.")
            return False
            
    except Exception as e:
        print(f"❌ API 호출 중 오류: {e}")
        return False

def test_mcp_server_startup():
    """MCP 서버 시작 테스트"""
    print("\n🧪 MCP 서버 시작 테스트...")
    
    try:
        # 환경변수 설정
        if os.path.exists('config.json'):
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                service_key = config.get('serviceKey')
                if service_key and service_key != "YOUR_SERVICE_KEY_HERE":
                    os.environ['OPENAPI_KOREA_SERVICE_KEY'] = service_key
                    print("✅ 환경변수에 서비스 키 설정 완료")
        
        # 서버 모듈 import 테스트
        from src.openapi_korea.server import server, handle_list_tools
        print("✅ MCP 서버 모듈 import 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP 서버 시작 테스트 실패: {e}")
        return False

async def test_tools():
    """도구 목록 테스트"""
    print("\n🧪 도구 목록 테스트...")
    
    try:
        from src.openapi_korea.server import handle_list_tools
        tools = await handle_list_tools()
        
        print(f"✅ 등록된 도구 수: {len(tools)}")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
        
        return True
        
    except Exception as e:
        print(f"❌ 도구 목록 테스트 실패: {e}")
        return False

async def main():
    """메인 테스트 함수"""
    print("🚀 OpenAPI Korea MCP Server 테스트 시작")
    print("="*60)
    
    # 1. MCP 서버 시작 테스트
    startup_ok = test_mcp_server_startup()
    
    # 2. 도구 목록 테스트
    if startup_ok:
        tools_ok = await test_tools()
    else:
        tools_ok = False
    
    # 3. API 클라이언트 테스트
    if startup_ok:
        api_ok = await test_api_client()
    else:
        api_ok = False
    
    # 결과 요약
    print("\n" + "="*60)
    print("🏁 테스트 결과 요약")
    print("="*60)
    print(f"MCP 서버 시작: {'✅ 성공' if startup_ok else '❌ 실패'}")
    print(f"도구 목록 조회: {'✅ 성공' if tools_ok else '❌ 실패'}")
    print(f"API 클라이언트: {'✅ 성공' if api_ok else '❌ 실패'}")
    
    if startup_ok and tools_ok and api_ok:
        print("\n🎉 모든 테스트 통과! MCP 서버가 정상적으로 작동합니다.")
        print("\n📋 다음 단계:")
        print("1. Kiro IDE의 MCP 설정에 서버 추가")
        print("2. 'get_sejong_parking_info' 도구 사용 테스트")
    else:
        print("\n⚠️  일부 테스트가 실패했습니다. 설정을 확인해주세요.")

if __name__ == "__main__":
    asyncio.run(main())