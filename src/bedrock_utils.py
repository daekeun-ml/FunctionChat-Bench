"""
Bedrock API 호출을 위한 유틸리티 함수
"""

import json
import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

def create_bedrock_client(region_name, aws_access_key_id=None, aws_secret_access_key=None):
    """
    Bedrock 클라이언트를 생성합니다.
    
    Parameters:
        region_name (str): AWS 리전 이름
        aws_access_key_id (str, optional): AWS 액세스 키 ID
        aws_secret_access_key (str, optional): AWS 시크릿 액세스 키
        
    Returns:
        boto3.client: Bedrock 클라이언트
    """
    if aws_access_key_id and aws_secret_access_key:
        return boto3.client(
            service_name='bedrock-runtime',
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
    else:
        return boto3.client(
            service_name='bedrock-runtime',
            region_name=region_name
        )

def convert_openai_to_bedrock_messages(messages):
    """
    OpenAI 형식의 메시지를 Bedrock 형식으로 변환합니다.
    
    Parameters:
        messages (list): OpenAI 형식의 메시지 목록
        
    Returns:
        list: Bedrock 형식의 메시지 목록
    """
    bedrock_messages = []
    system_content = None
    
    # 시스템 메시지가 있는지 확인하고 별도로 저장
    for msg in messages:
        if msg.get('role') == 'system':
            system_content = msg.get('content')
            break
    
    for msg in messages:
        role = msg.get('role')
        content = msg.get('content')
        
        if role == 'system':
            # 시스템 메시지는 건너뛰고 나중에 첫 번째 사용자 메시지에 추가
            continue
        elif role == 'user':
            user_content = content
            
            # 첫 번째 사용자 메시지이고 시스템 메시지가 있으면 결합
            if system_content and len(bedrock_messages) == 0:
                user_content = f"<system>\n{system_content}\n</system>\n\n{content}"
            
            bedrock_messages.append({
                'role': 'user',
                'content': [{'text': user_content}]
            })
        elif role == 'assistant':
            # 도구 호출이 있는 경우
            if 'tool_calls' in msg:
                tool_calls = msg.get('tool_calls', [])
                content_items = []
                
                for tool_call in tool_calls:
                    if tool_call.get('type') == 'function':
                        function_call = tool_call.get('function', {})
                        content_items.append({
                            'toolUse': {
                                'toolUseId': tool_call.get('id', ''),
                                'name': function_call.get('name', ''),
                                'input': json.loads(function_call.get('arguments', '{}'))
                            }
                        })
                
                if content:
                    content_items.insert(0, {'text': content})
                
                bedrock_messages.append({
                    'role': 'assistant',
                    'content': content_items
                })
            else:
                bedrock_messages.append({
                    'role': 'assistant',
                    'content': [{'text': content}]
                })
        elif role == 'tool':
            # 도구 응답 처리
            tool_call_id = msg.get('tool_call_id', '')
            bedrock_messages.append({
                'role': 'user',
                'content': [{
                    'toolResult': {
                        'toolUseId': tool_call_id,
                        'content': [{'json': json.loads(content)}]
                    }
                }]
            })
    
    return bedrock_messages

def convert_openai_to_bedrock_tools(tools):
    """
    OpenAI 형식의 도구를 Bedrock 형식으로 변환합니다.
    
    Parameters:
        tools (list): OpenAI 형식의 도구 목록
        
    Returns:
        dict: Bedrock 형식의 도구 설정
    """
    bedrock_tools = []
    
    for tool in tools:
        if tool.get('type') == 'function':
            function = tool.get('function', {})
            parameters = function.get('parameters', {})
            
            # Bedrock API는 inputSchema.json.type이 반드시 "object"여야 함
            if 'type' not in parameters:
                parameters['type'] = 'object'
            
            # 빈 parameters인 경우 기본 형식 제공
            if not parameters.get('properties'):
                parameters['properties'] = {}
            
            bedrock_tools.append({
                "toolSpec": {
                    "name": function.get('name', ''),
                    "description": function.get('description', ''),
                    "inputSchema": {
                        "json": parameters
                    }
                }
            })
    
    return {"tools": bedrock_tools}

def convert_bedrock_to_openai_response(bedrock_response):
    """
    Bedrock 응답을 OpenAI 형식으로 변환합니다.
    
    Parameters:
        bedrock_response (dict): Bedrock API 응답
        
    Returns:
        dict: OpenAI 형식의 응답
    """
    output_message = bedrock_response.get('output', {}).get('message', {})
    content_items = output_message.get('content', [])
    
    response_output = {
        'role': 'assistant',
        'content': None,
        'tool_calls': None
    }
    
    # 텍스트 응답과 도구 호출 분리
    text_content = []
    tool_calls = []
    
    for item in content_items:
        if 'text' in item:
            text_content.append(item['text'])
        elif 'toolUse' in item:
            tool_use = item['toolUse']
            tool_calls.append({
                'id': tool_use.get('toolUseId', f'call_{len(tool_calls)}'),
                'type': 'function',
                'function': {
                    'name': tool_use.get('name', ''),
                    'arguments': json.dumps(tool_use.get('input', {}))
                }
            })
    
    # 텍스트 응답 설정
    if text_content:
        response_output['content'] = ' '.join(text_content)
    
    # 도구 호출 설정
    if tool_calls:
        response_output['tool_calls'] = tool_calls
    
    return response_output

def call_bedrock_model(bedrock_client, model_id, messages, tools=None, temperature=0.1):
    """
    Bedrock 모델을 호출합니다.
    
    Parameters:
        bedrock_client (boto3.client): Bedrock 클라이언트
        model_id (str): 모델 ID
        messages (list): 메시지 목록
        tools (list, optional): 도구 목록
        temperature (float, optional): 온도 설정
        
    Returns:
        dict: 모델 응답
    """
    try:
        # 메시지 변환
        bedrock_messages = convert_openai_to_bedrock_messages(messages)
        
        # 요청 파라미터 구성
        request_params = {
            'modelId': model_id,
            'messages': bedrock_messages
        }
        
        # 도구 설정 추가
        if tools:
            bedrock_tools = convert_openai_to_bedrock_tools(tools)
            request_params['toolConfig'] = bedrock_tools
        
        # 모델 호출
        response = bedrock_client.converse(**request_params)
        
        # 응답 변환
        openai_response = convert_bedrock_to_openai_response(response)
        
        return openai_response
        
    except ClientError as err:
        logger.error(f"Bedrock API 호출 오류: {err}")
        raise
    except Exception as e:
        logger.error(f"일반 오류 발생: {e}")
        # 오류 발생 시 빈 응답 반환
        return {
            'role': 'assistant',
            'content': f"오류 발생: {str(e)}",
            'tool_calls': None
        }