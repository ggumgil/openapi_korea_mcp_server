#!/usr/bin/env python3
"""
OpenAPI Korea MCP Server

A Model Context Protocol server that provides access to Korean Open API services.
Currently supports Sejong City parking lot information.
"""

import asyncio
import json
import subprocess
import urllib.parse
from typing import Any, Dict, List, Optional

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio


class KoreanOpenAPIClient:
    """Client for Korean Open API services."""
    
    def __init__(self, service_key: str):
        self.service_key = service_key
        
    async def get_sejong_parking_info(
        self,
        page_index: int = 1,
        page_unit: int = 20,
        search_condition: str = "nm",
        search_keyword: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        세종시 주차장 정보를 조회합니다.
        
        Args:
            page_index: 페이지 번호 (기본값: 1)
            page_unit: 페이지당 조회 개수 (기본값: 20)
            search_condition: 검색 조건 (기본값: "nm")
            search_keyword: 검색 키워드 (선택사항)
            
        Returns:
            주차장 정보 딕셔너리 또는 None (실패 시)
        """
        base_url = "https://apis.data.go.kr/5690000/sjParkingLotInformation1/sj_00000949"
        
        # 파라미터 설정
        params = {
            'serviceKey': self.service_key,
            'pageIndex': str(page_index),
            'pageUnit': str(page_unit),
            'dataTy': 'json',
            'searchCondition': search_condition,
            'searchKeyword': search_keyword
        }
        
        # URL 인코딩
        query_string = urllib.parse.urlencode(params)
        full_url = f"{base_url}?{query_string}"
        
        try:
            # curl 명령어 실행 (M1 Mac SSL 문제 우회)
            curl_command = [
                'curl',
                '-s',  # silent
                '-k',  # insecure (SSL 검증 비활성화)
                '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                '-H', 'Accept: application/json',
                '--connect-timeout', '30',
                full_url
            ]
            
            # 비동기 subprocess 실행
            process = await asyncio.create_subprocess_exec(
                *curl_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            
            if process.returncode == 0:
                return json.loads(stdout.decode('utf-8'))
            else:
                raise Exception(f"API 요청 실패: {stderr.decode('utf-8')}")
                
        except asyncio.TimeoutError:
            raise Exception("요청 시간 초과 (30초)")
        except json.JSONDecodeError as e:
            raise Exception(f"응답 데이터 파싱 오류: {e}")
        except Exception as e:
            raise Exception(f"API 요청 중 오류: {e}")

    async def get_sejong_smoking_area(
        self,
        page_index: int = 1,
        page_unit: int = 20,
        search_keyword: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        세종시 흡연구역 위치 정보를 조회합니다.
        
        Args:
            page_index: 페이지 번호 (기본값: 1)
            page_unit: 페이지당 조회 개수 (기본값: 20)
            search_keyword: 검색 키워드 (장소명) (선택사항)
            
        Returns:
            흡연구역 정보 딕셔너리 또는 None (실패 시)
        """
        base_url = "http://apis.data.go.kr/5690000/sjSmokingAreaLocation/sj_00001180"
        
        # 파라미터 설정
        params = {
            'serviceKey': self.service_key,
            'pageIndex': str(page_index),
            'pageUnit': str(page_unit),
            'dataTy': 'json',
            'searchCondition': 'nm', # 장소명으로 검색
            'searchKeyword': search_keyword
        }
        
        # URL 인코딩
        query_string = urllib.parse.urlencode(params)
        full_url = f"{base_url}?{query_string}"
        
        try:
            # curl 명령어 실행
            curl_command = [
                'curl',
                '-s',  # silent
                '-k',  # insecure (SSL 검증 비활성화)
                '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                '-H', 'Accept: application/json',
                '--connect-timeout', '30',
                full_url
            ]
            
            # 비동기 subprocess 실행
            process = await asyncio.create_subprocess_exec(
                *curl_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            
            if process.returncode == 0:
                return json.loads(stdout.decode('utf-8'))
            else:
                raise Exception(f"API 요청 실패: {stderr.decode('utf-8')}")
                
        except asyncio.TimeoutError:
            raise Exception("요청 시간 초과 (30초)")
        except json.JSONDecodeError as e:
            raise Exception(f"응답 데이터 파싱 오류: {e}")
        except Exception as e:
            raise Exception(f"API 요청 중 오류: {e}")

    async def get_sejong_restaurant(
        self,
        page_index: int = 1,
        page_unit: int = 20,
        search_condition: str = "mtlty",
        search_keyword: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        세종시 음식점 정보를 조회합니다.
        
        Args:
            page_index: 페이지 번호 (기본값: 1)
            page_unit: 페이지당 조회 개수 (기본값: 20)
            search_condition: 검색 조건 (기본값: "mtlty")
            search_keyword: 검색 키워드 (상호명) (선택사항)
            
        Returns:
            음식점 정보 딕셔너리 또는 None (실패 시)
        """
        base_url = "http://apis.data.go.kr/5690000/sjRegularRestaurant/sj_00000760"
        
        # 파라미터 설정
        params = {
            'serviceKey': self.service_key,
            'pageIndex': str(page_index),
            'pageUnit': str(page_unit),
            'dataTy': 'json',
            'searchCondition': search_condition,
            'searchKeyword': search_keyword
        }
        
        # URL 인코딩
        query_string = urllib.parse.urlencode(params)
        full_url = f"{base_url}?{query_string}"
        
        try:
            # curl 명령어 실행
            curl_command = [
                'curl',
                '-s',  # silent
                '-k',  # insecure (SSL 검증 비활성화)
                '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                '-H', 'Accept: application/json',
                '--connect-timeout', '30',
                full_url
            ]
            
            # 비동기 subprocess 실행
            process = await asyncio.create_subprocess_exec(
                *curl_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            
            if process.returncode == 0:
                return json.loads(stdout.decode('utf-8'))
            else:
                raise Exception(f"API 요청 실패: {stderr.decode('utf-8')}")
                
        except asyncio.TimeoutError:
            raise Exception("요청 시간 초과 (30초)")
        except json.JSONDecodeError as e:
            raise Exception(f"응답 데이터 파싱 오류: {e}")
        except Exception as e:
            raise Exception(f"API 요청 중 오류: {e}")


# MCP Server 인스턴스 생성
server = Server("openapi-korea")

# 전역 API 클라이언트 (환경변수에서 키를 가져올 예정)
api_client: Optional[KoreanOpenAPIClient] = None


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """사용 가능한 도구 목록을 반환합니다."""
    return [
        types.Tool(
            name="get_sejong_parking_info",
            description="세종시 주차장 정보를 조회합니다. 페이지 번호, 조회 개수, 검색 키워드를 지정할 수 있습니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_index": {
                        "type": "integer",
                        "description": "조회할 페이지 번호 (기본값: 1)",
                        "default": 1,
                        "minimum": 1
                    },
                    "page_unit": {
                        "type": "integer", 
                        "description": "페이지당 조회할 항목 수 (기본값: 20, 최대: 100)",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 100
                    },
                    "search_keyword": {
                        "type": "string",
                        "description": "검색할 키워드 (선택사항)",
                        "default": ""
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="get_sejong_smoking_area",
            description="세종시 흡연구역 위치 정보를 조회합니다. 페이지 번호, 조회 개수, 검색 키워드를 지정할 수 있습니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_index": {
                        "type": "integer",
                        "description": "조회할 페이지 번호 (기본값: 1)",
                        "default": 1,
                        "minimum": 1
                    },
                    "page_unit": {
                        "type": "integer", 
                        "description": "페이지당 조회할 항목 수 (기본값: 20, 최대: 100)",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 100
                    },
                    "search_keyword": {
                        "type": "string",
                        "description": "검색할 키워드(장소명) (선택사항)",
                        "default": ""
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="get_sejong_restaurant",
            description="세종시 음식점 정보를 조회합니다. 페이지 번호, 조회 개수, 검색 조건, 검색 키워드를 지정할 수 있습니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_index": {
                        "type": "integer",
                        "description": "조회할 페이지 번호 (기본값: 1)",
                        "default": 1,
                        "minimum": 1
                    },
                    "page_unit": {
                        "type": "integer",
                        "description": "페이지당 조회할 항목 수 (기본값: 20, 최대: 100)",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 100
                    },
                    "search_condition": {
                        "type": "string",
                        "description": "검색 조건 (mtlty: 상호명, addr: 주소)",
                        "default": "mtlty"
                    },
                    "search_keyword": {
                        "type": "string",
                        "description": "검색할 키워드 (선택사항)",
                        "default": ""
                    }
                },
                "required": []
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
    """도구 호출을 처리합니다."""
    
    if not api_client:
        return [types.TextContent(
            type="text",
            text="❌ API 클라이언트가 초기화되지 않았습니다. 서비스 키를 확인해주세요."
        )]
    
    if name == "get_sejong_parking_info":
        try:
            # 파라미터 추출
            page_index = arguments.get("page_index", 1)
            page_unit = arguments.get("page_unit", 20)
            search_keyword = arguments.get("search_keyword", "")
            
            # API 호출
            result = await api_client.get_sejong_parking_info(
                page_index=page_index,
                page_unit=page_unit,
                search_keyword=search_keyword
            )
            
            if result:
                # 결과 포맷팅
                formatted_result = format_parking_info(result)
                return [types.TextContent(
                    type="text",
                    text=formatted_result
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text="❌ 주차장 정보를 가져오는데 실패했습니다."
                )]
                
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ 오류 발생: {str(e)}"
            )]
    elif name == "get_sejong_smoking_area":
        try:
            # 파라미터 추출
            page_index = arguments.get("page_index", 1)
            page_unit = arguments.get("page_unit", 20)
            search_keyword = arguments.get("search_keyword", "")
            
            # API 호출
            result = await api_client.get_sejong_smoking_area(
                page_index=page_index,
                page_unit=page_unit,
                search_keyword=search_keyword
            )
            
            if result:
                # 결과 포맷팅
                formatted_result = format_smoking_area_info(result)
                return [types.TextContent(
                    type="text",
                    text=formatted_result
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text="❌ 흡연구역 정보를 가져오는데 실패했습니다."
                )]
                
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ 오류 발생: {str(e)}"
            )]
    elif name == "get_sejong_restaurant":
        try:
            # 파라미터 추출
            page_index = arguments.get("page_index", 1)
            page_unit = arguments.get("page_unit", 20)
            search_condition = arguments.get("search_condition", "mtlty")
            search_keyword = arguments.get("search_keyword", "")
            
            # API 호출
            result = await api_client.get_sejong_restaurant(
                page_index=page_index,
                page_unit=page_unit,
                search_condition=search_condition,
                search_keyword=search_keyword
            )
            
            if result:
                # 결과 포맷팅
                formatted_result = format_restaurant_info(result)
                return [types.TextContent(
                    type="text",
                    text=formatted_result
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text="❌ 음식점 정보를 가져오는데 실패했습니다."
                )]
                
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ 오류 발생: {str(e)}"
            )]
    
    else:
        return [types.TextContent(
            type="text",
            text=f"❌ 알 수 없는 도구: {name}"
        )]


def format_parking_info(data: Dict[str, Any]) -> str:
    """주차장 정보를 보기 좋게 포맷팅합니다."""
    
    if not data:
        return "❌ 데이터가 없습니다."
    
    result = "🅿️ **세종시 주차장 정보 조회 결과**\n"
    result += "=" * 50 + "\n\n"
    
    # 응답 구조 확인 및 데이터 추출
    if 'response' in data:
        response = data['response']
        if 'body' in response and 'items' in response['body']:
            items = response['body']['items']
            total_count = response['body'].get('totalCount', 0)
            
            result += f"📊 **총 {total_count}개의 주차장 정보**\n\n"
            
            for i, item in enumerate(items, 1):
                result += f"**{i}. {item.get('prkplceNm', '이름 없음')}**\n"
                result += f"   📍 주소: {item.get('rdnmadr', '주소 정보 없음')}\n"
                result += f"   🚗 주차면수: {item.get('prkcmprt', '정보 없음')}면\n"
                result += f"   💰 요금정보: {item.get('feedingSe', '정보 없음')}\n"
                result += f"   📞 연락처: {item.get('phoneNumber', '정보 없음')}\n"
                result += f"   🕒 운영시간: {item.get('operOpenHm', '정보 없음')} ~ {item.get('operCloseHm', '정보 없음')}\n"
                result += "\n" + "-" * 40 + "\n\n"
        else:
            result += "❌ 주차장 데이터가 없습니다.\n"
    else:
        # 전체 JSON 출력 (구조를 모를 경우)
        result += "```json\n"
        result += json.dumps(data, ensure_ascii=False, indent=2)
        result += "\n```\n"
    
    return result


def format_smoking_area_info(data: Dict[str, Any]) -> str:
    """흡연구역 정보를 보기 좋게 포맷팅합니다."""
    
    if not data:
        return "❌ 데이터가 없습니다."
    
    result = "🚭 **세종시 흡연구역 정보 조회 결과**\n"
    result += "=" * 50 + "\n\n"
    
    # 응답 구조 확인 및 데이터 추출
    if 'response' in data:
        response = data['response']
        if 'body' in response and 'items' in response['body']:
            items = response['body']['items']
            total_count = response['body'].get('totalCount', 0)
            
            result += f"📊 **총 {total_count}개의 흡연구역 정보**\n\n"
            
            for i, item in enumerate(items, 1):
                result += f"**{i}. {item.get('smkngAreaNm', '이름 없음')}**\n"
                result += f"   📍 주소: {item.get('rdnmadr', '주소 정보 없음')}\n"
                result += f"   🏢 관리기관: {item.get('mngmtInsttNm', '정보 없음')}\n"
                result += f"   📞 연락처: {item.get('mngmtInsttPhoneNumber', '정보 없음')}\n"
                result += "\n" + "-" * 40 + "\n\n"
        else:
            # items가 없는 경우, 에러 메시지나 다른 정보가 있을 수 있음
            if 'header' in response and response['header'].get('resultCode') != '00':
                result += f"❌ API 오류: {response['header'].get('resultMsg', '알 수 없는 오류')}\n"
            else:
                result += "❌ 흡연구역 데이터가 없습니다.\n"
    else:
        # 전체 JSON 출력 (구조를 모를 경우)
        result += "```json\n"
        result += json.dumps(data, ensure_ascii=False, indent=2)
        result += "\n```\n"
    
    return result


def format_restaurant_info(data: Dict[str, Any]) -> str:
    """음식점 정보를 보기 좋게 포맷팅합니다."""
    
    if not data:
        return "❌ 데이터가 없습니다."
    
    result = "🍜 **세종시 음식점 정보 조회 결과**\n"
    result += "=" * 50 + "\n\n"
    
    # 응답 구조 확인 및 데이터 추출
    if 'response' in data:
        response = data['response']
        if 'body' in response and 'items' in response['body']:
            items = response['body']['items']
            total_count = response['body'].get('totalCount', 0)
            
            result += f"📊 **총 {total_count}개의 음식점 정보**\n\n"
            
            for i, item in enumerate(items, 1):
                result += f"**{i}. {item.get('mtlty', '이름 없음')}**\n"
                result += f"   📍 주소: {item.get('addr', '주소 정보 없음')}\n"
                result += f"   🍽️ 주요메뉴: {item.get('main_menu', '정보 없음')}\n"
                result += f"   📞 연락처: {item.get('telno', '정보 없음')}\n"
                result += "\n" + "-" * 40 + "\n\n"
        else:
            # items가 없는 경우, 에러 메시지나 다른 정보가 있을 수 있음
            if 'header' in response and response['header'].get('resultCode') != '00':
                result += f"❌ API 오류: {response['header'].get('resultMsg', '알 수 없는 오류')}\n"
            else:
                result += "❌ 음식점 데이터가 없습니다.\n"
    else:
        # 전체 JSON 출력 (구조를 모를 경우)
        result += "```json\n"
        result += json.dumps(data, ensure_ascii=False, indent=2)
        result += "\n```\n"
    
    return result



async def main():
    """MCP 서버를 시작합니다."""
    import os
    
    # 환경변수에서 서비스 키 가져오기
    service_key = os.getenv('OPENAPI_KOREA_SERVICE_KEY')
    
    if not service_key:
        # 설정 파일에서 키 가져오기 시도
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                service_key = config.get('serviceKey')
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    
    if service_key:
        global api_client
        api_client = KoreanOpenAPIClient(service_key)
        print("✅ OpenAPI Korea MCP Server가 시작되었습니다.", file=sys.stderr)
    else:
        print("⚠️  서비스 키가 설정되지 않았습니다. OPENAPI_KOREA_SERVICE_KEY 환경변수나 config.json 파일을 확인해주세요.", file=sys.stderr)
    
    # stdio를 통해 MCP 서버 실행
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="openapi-korea",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    import sys
    asyncio.run(main())
