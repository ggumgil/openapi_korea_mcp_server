#!/usr/bin/env python3
"""
OpenAPI Korea MCP Server

A Model Context Protocol server that provides access to Korean Open API services.
Currently supports Sejong City parking lot information through resources.
"""

import asyncio
import json
import os
import aiofiles
import sys
import logging
import subprocess
import urllib.parse
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio



class DataCache:
    """데이터 캐싱 클래스"""
    def __init__(self, ttl_minutes: int = 30):
        self.cache = {}
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return data
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, data: Dict[str, Any]):
        self.cache[key] = (data, datetime.now())
    
    def clear(self):
        self.cache.clear()


class KoreanOpenAPIClient:
    """Client for Korean Open API services."""
    
    def __init__(self, service_key: str):
        self.service_key = service_key
        self.cache = DataCache()
        
    async def get_sejong_parking_info(
        self,
        page_index: int = 1,
        page_unit: int = 100,
        search_condition: str = "nm",
        search_keyword: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        세종시 주차장 정보를 조회합니다.
        """
        cache_key = f"parking_{page_index}_{page_unit}_{search_condition}_{search_keyword}"
        
        # 캐시 확인
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data
        
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
        
        data = await self._make_request(base_url, params)

        if data:
            self.cache.set(cache_key, data)
        return data

    async def get_sejong_smoking_area(
        self,
        page_index: int = 1,
        page_unit: int = 100,
        search_keyword: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        세종시 흡연구역 위치 정보를 조회합니다.
        """
        cache_key = f"smoking_{page_index}_{page_unit}_{search_keyword}"
        
        # 캐시 확인
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data
            
        base_url = "http://apis.data.go.kr/5690000/sjSmokingAreaLocation/sj_00001180"
        
        # 파라미터 설정
        params = {
            'serviceKey': self.service_key,
            'pageIndex': str(page_index),
            'pageUnit': str(page_unit),
            'dataTy': 'json',
            'searchCondition': 'nm',
            'searchKeyword': search_keyword
        }
        
        data = await self._make_request(base_url, params)
        if data:
            self.cache.set(cache_key, data)
        return data

    async def get_sejong_restaurant(
        self,
        page_index: int = 1,
        page_unit: int = 100,
        search_condition: str = "mtlty",
        search_keyword: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        세종시 음식점 정보를 조회합니다.
        """
        cache_key = f"restaurant_{page_index}_{page_unit}_{search_condition}_{search_keyword}"
        
        # 캐시 확인
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data
            
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
        
        data = await self._make_request(base_url, params)
        if data:
            self.cache.set(cache_key, data)
        return data
    
    async def get_sejong_cctv(
        self,
        page_index: int = 1,
        page_unit: int = 20,
        search_keyword: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        세종시 CCTV 정보를 조회합니다.
        
        Args:
            page_index: 페이지 번호 (기본값: 1)
            page_unit: 페이지당 조회 개수 (기본값: 20)
            search_keyword: 검색 키워드 (소재지 도로명주소) (선택사항)
            
        Returns:
            CCTV 정보 딕셔너리 또는 None (실패 시)
        """
        cache_key = f"restaurant_{page_index}_{page_unit}_{search_keyword}"
        
        # 캐시 확인
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data
        
        base_url = "http://apis.data.go.kr/5690000/sjCCTV/sj_00000030"
        
        # 파라미터 설정
        params = {
            'serviceKey': self.service_key,
            'pageIndex': str(page_index),
            'pageUnit': str(page_unit),
            'dataTy': 'json',
            'searchCondition': 'rdnmadr', # 소재지 도로명주소로 검색
            'searchKeyword': search_keyword
        }
        
        data = await self._make_request(base_url, params)
        if data:
            self.cache.set(cache_key, data)
        return data


    async def _make_request(self, base_url: str, params: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """공통 API 요청 메서드"""
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


# MCP Server 인스턴스 생성
server = Server("openapi-korea", "0.1.0")
                

# 전역 API 클라이언트
api_client: Optional[KoreanOpenAPIClient] = None

# 리소스 데이터 캐시
resource_data_cache: Dict[str, Any] = {}

@server.list_resources()
async def handle_list_resources() -> List[types.Resource]:
    """사용 가능한 리소스 목록을 반환합니다."""
    return [
        types.Resource(
            uri="sejong://parking/list", # type: ignore
            name="세종시 주차장 목록",
            description="세종시 모든 주차장 정보를 제공합니다",
            mimeType="application/json"
        ),
        types.Resource(
            uri="sejong://smoking_area/list",  # type: ignore
            name="세종시 흡연구역 목록",
            description="세종시 모든 흡연구역 정보를 제공합니다",
            mimeType="application/json"
        ),
        types.Resource(
            uri="sejong://restaurant/list", # type: ignore
            name="세종시 음식점 목록", 
            description="세종시 모든 음식점 정보를 제공합니다",
            mimeType="application/json"
        ),
        types.Resource(
            uri="sejong://cctv/list", # type: ignore
            name="세종시 CCTV 목록", 
            description="세종시 모든 CCTV 정보를 제공합니다",
            mimeType="application/json"
        ),
        types.Resource(
            uri="sejong://file/list", # type: ignore
            name="세종시 정보 파일", 
            description="세종시의 모든 정보를 담은 파일입니다.",
            mimeType="text/plain"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """리소스 내용을 읽어 반환합니다."""
    # logger.debug(f"handle_read_resource called with URI: {uri}")

    global resource_data_cache
    uri_str = str(uri)

    if not api_client:
        return json.dumps({
            "error": "API 클라이언트가 초기화되지 않았습니다. 서비스 키를 확인해주세요."
        }, ensure_ascii=False, indent=2)
    
    try:
        # 캐시 확인
        if uri_str in resource_data_cache:
            return resource_data_cache[uri_str]

        if uri_str == "sejong://parking/list":
            all_data = await fetch_all_pages(api_client.get_sejong_parking_info)
            formatted_data = format_parking_resource(all_data)
            
        elif uri_str == "sejong://smoking_area/list":
            all_data = await fetch_all_pages(api_client.get_sejong_smoking_area)
            formatted_data = format_smoking_area_resource(all_data)
            
        elif uri_str == "sejong://restaurant/list":
            all_data = await fetch_all_pages(api_client.get_sejong_restaurant)
            formatted_data = format_restaurant_resource(all_data)
        
        elif uri_str == "sejong://cctv/list":
            all_data = await fetch_all_pages(api_client.get_sejong_cctv)
            formatted_data = format_cctv_info(all_data)
            
        elif uri_str == "sejong://file/list":
            """Reads content from a specific log file asynchronously."""
            try:
                async with aiofiles.open( "/Users/dongsilguy/Documents/02.Dev/06.PythonProjects/python_mcp/openapi_korea/src/openapi_korea/resource_file.md", mode="r") as f:
                    content = await f.read()
                await asyncio.sleep(1)
                return content
            except FileNotFoundError:
                return "리소스 파일을 찾을 수 없습니다."        
        else:
            return json.dumps({
                "error": f"알 수 없는 리소스: {uri_str}"
            }, ensure_ascii=False, indent=2)
        
        # 캐시에 저장
        resource_data_cache[uri_str] = formatted_data
        return formatted_data
            
    except Exception as e:
        return json.dumps({
            "error": f"리소스 읽기 실패: {str(e)}"
        }, ensure_ascii=False, indent=2)


async def fetch_all_pages(api_method, max_pages: int = 1000) -> List[Dict[str, Any]]:
    """여러 페이지의 데이터를 모두 가져옵니다."""
    all_items = []
    page = 1
    
    while page <= max_pages:
        try:
            data = await api_method(page_index=page, page_unit=100)
            
            if not data or 'body' not in data:
                break
                
            if 'body' not in data or 'items' not in data['body']:
                break
                
            items = data['body']['items']
            if not items:
                break
                
            all_items.extend(items)
            
            # 더 이상 데이터가 없으면 중단
            if len(items) < 100:
                break
                
            page += 1
            
        except Exception as e:
            print(f"페이지 {page} 가져오기 실패: {e}", file=sys.stderr)
            break
    
    return all_items


def format_parking_resource(items: List[Dict[str, Any]]) -> str:
    """주차장 리소스 데이터를 JSON 형태로 포맷팅합니다."""
    
    formatted_items = []
    
    for item in items:
        formatted_item = {
            "id": item.get('prkplceNo', ''),
            "name": item.get('prkplceNm', ''),
            "address": item.get('rdnmadr', ''),
            "parking_spaces": item.get('prkcmprt', ''),
            "fee_info": item.get('feedingSe', ''),
            "phone": item.get('phoneNumber', ''),
            "open_time": item.get('operOpenHm', ''),
            "close_time": item.get('operCloseHm', ''),
            "operation_day": item.get('operDay', ''),
            "facility_type": item.get('prkplceSe', ''),
            "coordinates": {
                "latitude": item.get('latitude', ''),
                "longitude": item.get('longitude', '')
            }
        }
        formatted_items.append(formatted_item)
    
    result = {
        "type": "sejong_parking_lots",
        "total_count": len(formatted_items),
        "last_updated": datetime.now().isoformat(),
        "data": formatted_items
    }
    
    return json.dumps(result, ensure_ascii=False, indent=2)


def format_smoking_area_resource(items: List[Dict[str, Any]]) -> str:
    """흡연구역 리소스 데이터를 JSON 형태로 포맷팅합니다."""
    
    formatted_items = []
    
    for item in items:
        formatted_item = {
            "id": item.get('smkngAreaNo', ''),
            "name": item.get('smkngAreaNm', ''),
            "address": item.get('rdnmadr', ''),
            "management_org": item.get('mngmtInsttNm', ''),
            "management_phone": item.get('mngmtInsttPhoneNumber', ''),
            "coordinates": {
                "latitude": item.get('latitude', ''),
                "longitude": item.get('longitude', '')
            }
        }
        formatted_items.append(formatted_item)
    
    result = {
        "type": "sejong_smoking_areas",
        "total_count": len(formatted_items),
        "last_updated": datetime.now().isoformat(),
        "data": formatted_items
    }
    
    return json.dumps(result, ensure_ascii=False, indent=2)


def format_restaurant_resource(items: List[Dict[str, Any]]) -> str:
    """음식점 리소스 데이터를 JSON 형태로 포맷팅합니다."""
    
    formatted_items = []
    
    for item in items:
        formatted_item = {
            "id": item.get('restaurantId', ''),
            "name": item.get('mtlty', ''),
            "address": item.get('addr', ''),
            "main_menu": item.get('main_menu', ''),
            "phone": item.get('telno', ''),
            "business_type": item.get('bizestblSe', ''),
            "coordinates": {
                "latitude": item.get('latitude', ''),
                "longitude": item.get('longitude', '')
            }
        }
        formatted_items.append(formatted_item)
    
    result = {
        "type": "sejong_restaurants", 
        "total_count": len(formatted_items),
        "last_updated": datetime.now().isoformat(),
        "data": formatted_items
    }
    
    return json.dumps(result, ensure_ascii=False, indent=2)


def format_cctv_info(items: List[Dict[str, Any]]) -> str:
    """CCTV 정보를 보기 좋게 포맷팅합니다."""
    
    formatted_items = []

    for item in items:
        formatted_item = {
            "id": item.get('cctvId', ''),
            "address": item.get('rdnmadr', ''),
            "installation_purpose": item.get('instlPurpsSe', ''),
            "camera_pixel": item.get('cmeraPixel', ''),
            "installation_year": item.get('instlYear', ''),
            "management_org": item.get('mngmtInsttNm', ''),
            "management_phone": item.get('mngmtInsttPhoneNumber', ''),
            "coordinates": {
                "latitude": item.get('latitude', ''),
                "longitude": item.get('longitude', '')
            }
        }
        formatted_items.append(formatted_item)
    
    result = {
        "type": "sejong_cctv_info",
        "total_count": len(formatted_items),
        "last_updated": datetime.now().isoformat(),
        "data": formatted_items
    }
    
    return json.dumps(result, ensure_ascii=False, indent=2)

    # if not data:
    #     return "❌ 데이터가 없습니다."
    
    # result = "📹 **세종시 CCTV 정보 조회 결과**\n"
    # result += "=" * 50 + "\n\n"
    
    # # 응답 구조 확인 및 데이터 추출
    # if 'body' in data:
    #     response = data
    #     if 'body' in response and 'items' in response['body']:
    #         items = response['body']['items']
    #         total_count = response['body'].get('totalCount', 0)
            
    #         result += f"📊 **총 {total_count}개의 CCTV 정보**\n\n"
            
    #         for i, item in enumerate(items, 1):
    #             result += f"**{i}. {item.get('rdnmadr', '주소 없음')}**\n"
    #             result += f"   🎯 목적: {item.get('instlPurpsSe', '정보 없음')}\n"
    #             result += f"   📷 카메라 화소: {item.get('cmeraPixel', '정보 없음')}만 화소\n"
    #             result += f"   📅 설치 연도: {item.get('instlYear', '정보 없음')}년\n"
    #             result += f"   🏢 관리기관: {item.get('mngmtInsttNm', '정보 없음')}\n"
    #             result += f"   📞 연락처: {item.get('mngmtInsttPhoneNumber', '정보 없음')}\n"
    #             result += "\n" + "-" * 40 + "\n\n"
    #     else:
    #         # items가 없는 경우, 에러 메시지나 다른 정보가 있을 수 있음
    #         if 'header' in response and response['header'].get('resultCode') != '00':
    #             result += f"❌ API 오류: {response['header'].get('resultMsg', '알 수 없는 오류')}\n"
    #         else:
    #             result += "❌ CCTV 데이터가 없습니다.\n"
    # else:
    #     # 전체 JSON 출력 (구조를 모를 경우)
    #     result += "```json\n"
    #     result += json.dumps(data, ensure_ascii=False, indent=2)
    #     result += "\n```\n"
    
    # return result


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """데이터 관리를 위한 도구 목록을 반환합니다."""
    return [
        types.Tool(
            name="refresh_data",
            description="캐시된 데이터를 새로고침합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_type": {
                        "type": "string",
                        "enum": ["parking", "smoking_area", "restaurant", "cctv", "all"],
                        "description": "새로고침할 리소스 타입 (all은 모든 데이터)",
                        "default": "all"
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="search_data",
            description="특정 키워드로 데이터를 검색합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_type": {
                        "type": "string", 
                        "enum": ["parking", "smoking_area", "restaurant", "cctv"],
                        "description": "검색할 리소스 타입"
                    },
                    "keyword": {
                        "type": "string",
                        "description": "json 데이터의 body에 있는 주소에서 검색할 키워드"
                    }
                },
                "required": ["resource_type", "keyword"]
            }
        ),
        types.Tool(
            name="show_cached_data",
            description="현재 캐시된 데이터를 보여줍니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_type": {
                        "type": "string",
                        "enum": ["parking", "smoking_area", "restaurant", "cctv", "all"],
                        "description": "보여줄 리소스 타입 (all은 모든 데이터)",
                        "default": "all"
                    }
                },
                "required": []
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
    """도구 호출을 처리합니다."""
    
    global resource_data_cache

    if not api_client:
        return [types.TextContent(
            type="text",
            text="❌ API 클라이언트가 초기화되지 않았습니다. 서비스 키를 확인해주세요."
        )]
    
    if name == "refresh_data":
        resource_type = arguments.get("resource_type", "all")
        
        try:
            if resource_type in ["parking", "all"]:
                resource_data_cache.pop("sejong://parking/list", None)
                await handle_read_resource(AnyUrl("sejong://parking/list"))

            if resource_type in ["smoking_area", "all"]:
                resource_data_cache.pop("sejong://smoking_area/list", None)
                await handle_read_resource(AnyUrl("sejong://smoking_area/list"))

            if resource_type in ["restaurant", "all"]:
                resource_data_cache.pop("sejong://restaurant/list", None)
                await handle_read_resource(AnyUrl("sejong://restaurant/list"))
            
            if resource_type in ["cctv", "all"]:
                resource_data_cache.pop("sejong://cctv/list", None)
                await handle_read_resource(AnyUrl("sejong://cctv/list"))

            return [types.TextContent(
                type="text",
                text=f"✅ {resource_type} 데이터가 성공적으로 새로고침되었습니다."
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ 데이터 새로고침 실패: {str(e)}"
            )]
    
    elif name == "search_data":
        resource_type = arguments.get("resource_type")
        keyword = arguments.get("keyword", "").lower()
        
        try:
            resource_uri = f"sejong://{resource_type}/list"
            
            if resource_uri not in resource_data_cache:
                await handle_read_resource(AnyUrl(resource_uri))
            
            resource_json = json.loads(resource_data_cache[resource_uri])
            all_items = resource_json.get("data", [])
            
            search_results = []
            for item in all_items:
                # 이름 또는 주소에 키워드가 포함되어 있는지 확인
                if (
                    keyword in item.get('name', '').lower() or 
                    keyword in item.get('address', '').lower()
                ):
                    search_results.append(item)
            
            count = len(search_results)
            return [types.TextContent(
                type="text",
                text=f"🔍 '{keyword}' 검색 결과: {count}개의 항목을 찾았습니다.\n{json.dumps(search_results, ensure_ascii=False, indent=2)}"
            )]

        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ 검색 실패: {str(e)}"
            )]
    
    elif name == "show_cached_data":
        resource_type = arguments.get("resource_type", "all")
        
        if not api_client or not api_client.cache.cache:
            return [types.TextContent(
                type="text",
                text="ℹ️ 캐시가 비어있습니다."
            )]

        now = datetime.now()
        output_lines = [f"## 📦 캐시된 데이터 ({resource_type})"]
        
        cache_items = api_client.cache.cache.items()
        
        if resource_type != "all":
            cache_items = [(k, v) for k, v in cache_items if k.startswith(resource_type)]

        if not cache_items:
            return [types.TextContent(
                type="text",
                text=f"ℹ️ '{resource_type}'에 대한 캐시된 데이터가 없습니다."
            )]

        for key, (data, timestamp) in cache_items:
            ttl_remaining = api_client.cache.ttl - (now - timestamp)
            output_lines.append(
                f"- **키:** `{key}`\n  - **캐시 시간:** {timestamp.isoformat()}\n  - **남은 TTL:** {int(ttl_remaining.total_seconds())}초\n - **데이터 미리보기:** `{json.dumps(data, ensure_ascii=False)}...`"
            )
        
        return [types.TextContent(
            type="text",
            text="\n".join(output_lines)
        )]

    else:
        return [types.TextContent(
            type="text",
            text=f"❌ 알 수 없는 도구: {name}"
        )]


async def main():
    """MCP 서버를 시작합니다."""
    import os
    import sys
    
    # 환경변수에서 서비스 키 가져오기
    service_key = os.getenv('OPENAPI_KOREA_SERVICE_KEY')
    resource_file_path = os.getenv('OPENAPI_RESOURCE_FILE_PATH')
    
    if not service_key:
        # 설정 파일에서 키 가져오기 시도
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                service_key = config.get('serviceKey')
                resource_file_path = config.get('resourceFilePath', resource_file_path)
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
