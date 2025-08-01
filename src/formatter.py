import json
from typing import Optional, List, Dict
from pydantic import BaseModel, root_validator


def convert_eval_key(response):
    """
      A method determines pass/fail based on the pattern of the evaluation text generated by the LLM.

      Parameters:
          dict: API response json (OpenAI, Azure, Bedrock, etc.)
      Returns:
          str: pass or fail
    """
    def contain_is_pass(key):
        if 'pass' in key.lower():
            return 'pass'
        if 'fail' in key.lower():
            return 'fail'
        if '패스' in key.lower():
            return 'pass'
        if '패쓰' in key.lower():
            return 'pass'
        if '통과' in key:
            return 'pass'
        if '합격' in key:
            return 'pass'
        return key
    
    # 다양한 API 응답 형식 처리
    content = None
    
    # OpenAI API 형식
    if 'choices' in response and len(response['choices']) > 0:
        if 'message' in response['choices'][0] and 'content' in response['choices'][0]['message']:
            content = response['choices'][0]['message']['content']
    
    # Bedrock API 형식 (Claude)
    elif 'completion' in response:
        content = response['completion']
    
    # Bedrock API 형식 (다른 모델)
    elif 'results' in response and len(response['results']) > 0:
        if 'outputText' in response['results'][0]:
            content = response['results'][0]['outputText']
    
    # 다른 API 형식
    elif 'content' in response:
        content = response['content']
    
    # 응답에서 내용을 찾을 수 없는 경우
    if content is None:
        print("Warning: Could not find content in API response")
        print(f"Response structure: {response.keys()}")
        return 'fail'  # 기본값으로 'fail' 반환
    
    key = ''.join(content.strip().split('\n')[-2:])
    key = contain_is_pass(key)
    if key in ['pass', 'fail']:
        return key
    if '입니다.' == key:
        key = ''.join(content.strip().split('\n')[-4:])
        key = contain_is_pass(key)
        if key in ['pass', 'fail']:
            return key
    return key


class RequestFormatter(BaseModel):
    serial_num: int
    messages: list
    tools: list
    temperature: float
    tool_choice: str
    ground_truth: dict
    acceptable_arguments: Optional[str] = None

    @root_validator(pre=True)
    def ensure_acceptable_arguments(cls, values):
        acceptable_arguments = values.get('acceptable_arguments', '')
        if isinstance(acceptable_arguments, dict):
            values['acceptable_arguments'] = json.dumps(acceptable_arguments, ensure_ascii=False)
        return values

    @root_validator(pre=True)
    def clean_ground_truth(cls, values):
        ground_truth = values.get('ground_truth', '')
        if isinstance(ground_truth, str):
            args = ground_truth.split('arguments')[1]
            new_args = args.replace('"include_lowercase"', '\\"include_lowercase\\"')
            if not new_args.endswith('"}'):
                new_args = new_args + '"}'
            elif new_args.endswith('\\"}'):
                new_args = new_args + '"}'
            elif new_args.endswith('\\"}"}'):
                pass
            elif new_args.endswith('"}"}'):
                new_args = new_args[:-4] + '\\"}"}'
            ground_truth = ground_truth.replace(args, new_args)
            try:
                ground_truth = json.loads(ground_truth)
            except Exception as e:
                print(f"[ERROR] ground_truth format error : {ground_truth}")
                raise e
        values['ground_truth'] = ground_truth
        return values

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    def to_dict(self):
        return self.dict()


class CommonRequestFormatter(RequestFormatter):
    category: str
    type_of_output: str


class DialogRequestFormatter(RequestFormatter):
    type_of_output: str


class SingleCallRequestFormatter(RequestFormatter):
    messages: list
    tools: list
    tools_type: str


class ResponseFormatter(BaseModel):
    # UserWarning: Field "model_response" has conflict with protected namespace "model_".
    request_model: Dict
    response_model: Dict
    evaluate_prompt: str
    evaluate_response: Dict
    # report
    tsv_keys: Optional[List[str]] = []
    report_arguments: Optional[dict] = None

    def to_dict(self):
        convert_dict = self.dict()
        convert_dict['model_request'] = convert_dict['request_model']
        convert_dict['model_response'] = convert_dict['response_model']
        del convert_dict['request_model']
        del convert_dict['response_model']
        return convert_dict

    def to_tsv(self):
        output_str = ''
        for key in self.tsv_keys:
            if key == 'input_messages':
                key = 'messages'
            output_str += f"{self.report_arguments[key]}\t"
        return output_str

    def get_tsv_title(self):
        output_str = '#'
        for key in self.tsv_keys:
            output_str += f"{key}\t"
        return output_str


class CommonResponseFormatter(ResponseFormatter):
    tsv_keys: Optional[List[str]] = ['serial_num', 'is_pass', 'category', 'type_of_output',
                                     'ground_truth', 'acceptable_arguments',
                                     'model_output', 'reasoning', 'input_messages']

    @root_validator(pre=True)
    def set_report_params(cls, values):
        model_request = values.get('request_model', {})
        model_response = values.get('response_model', {})
        evaluate_response = values.get('evaluate_response', {})
        serial_num = model_request['serial_num']
        is_pass = convert_eval_key(evaluate_response)
        category = model_request['category']
        type_of_output = model_request['type_of_output']
        ground_truth = json.dumps(model_request['ground_truth'], ensure_ascii=False)
        acceptable_arguments = json.dumps(model_request['acceptable_arguments'], ensure_ascii=False)
        model_output = json.dumps(model_response, ensure_ascii=False)
        
        # 다양한 API 응답 형식 처리
        content = None
        
        # OpenAI API 형식
        if 'choices' in evaluate_response and len(evaluate_response['choices']) > 0:
            if 'message' in evaluate_response['choices'][0] and 'content' in evaluate_response['choices'][0]['message']:
                content = evaluate_response['choices'][0]['message']['content']
        
        # Bedrock API 형식 (Claude)
        elif 'completion' in evaluate_response:
            content = evaluate_response['completion']
        
        # Bedrock API 형식 (다른 모델)
        elif 'results' in evaluate_response and len(evaluate_response['results']) > 0:
            if 'outputText' in evaluate_response['results'][0]:
                content = evaluate_response['results'][0]['outputText']
        
        # 다른 API 형식
        elif 'content' in evaluate_response:
            content = evaluate_response['content']
        
        # 응답에서 내용을 찾을 수 없는 경우
        if content is None:
            print("Warning: Could not find content in API response for reasoning")
            print(f"Response structure: {evaluate_response.keys()}")
            content = "No reasoning available"
        
        reasoning = json.dumps({'reasoning': content}, ensure_ascii=False)
        messages = json.dumps(model_request['messages'], ensure_ascii=False)
        values['report_arguments'] = {
            'serial_num': serial_num,
            'is_pass': is_pass,
            'category': category,
            'type_of_output': type_of_output,
            'ground_truth': ground_truth,
            'acceptable_arguments': acceptable_arguments,
            'model_output': model_output,
            'reasoning': reasoning,
            'messages': messages
        }
        return values


class SingleCallResponseFormatter(ResponseFormatter):
    tsv_keys: Optional[List[str]] = ['serial_num', 'is_pass', 'tools_type',
                                     'ground_truth', 'acceptable_arguments',
                                     'model_output', 'reasoning', 'query']

    @root_validator(pre=True)
    def set_report_params(cls, values):
        model_request = values.get('request_model', {})
        model_response = values.get('response_model', {})
        evaluate_response = values.get('evaluate_response', {})
        serial_num = model_request['serial_num']
        is_pass = convert_eval_key(evaluate_response)
        tools_type = model_request['tools_type']
        ground_truth = json.dumps(model_request['ground_truth'], ensure_ascii=False)
        acceptable_arguments = json.dumps(model_request['acceptable_arguments'], ensure_ascii=False)
        model_output = json.dumps(model_response, ensure_ascii=False)
        
        # 다양한 API 응답 형식 처리
        content = None
        
        # OpenAI API 형식
        if 'choices' in evaluate_response and len(evaluate_response['choices']) > 0:
            if 'message' in evaluate_response['choices'][0] and 'content' in evaluate_response['choices'][0]['message']:
                content = evaluate_response['choices'][0]['message']['content']
        
        # Bedrock API 형식 (Claude)
        elif 'completion' in evaluate_response:
            content = evaluate_response['completion']
        
        # Bedrock API 형식 (다른 모델)
        elif 'results' in evaluate_response and len(evaluate_response['results']) > 0:
            if 'outputText' in evaluate_response['results'][0]:
                content = evaluate_response['results'][0]['outputText']
        
        # 다른 API 형식
        elif 'content' in evaluate_response:
            content = evaluate_response['content']
        
        # 응답에서 내용을 찾을 수 없는 경우
        if content is None:
            print("Warning: Could not find content in API response for reasoning")
            print(f"Response structure: {evaluate_response.keys()}")
            content = "No reasoning available"
        
        reasoning = json.dumps({'reasoning': content}, ensure_ascii=False)
        messages = json.dumps(model_request['messages'], ensure_ascii=False)
        values['report_arguments'] = {
            'serial_num': serial_num,
            'is_pass': is_pass,
            'tools_type': tools_type,
            'ground_truth': ground_truth,
            'acceptable_arguments': acceptable_arguments,
            'model_output': model_output,
            'reasoning': reasoning,
            'query': messages
        }
        return values


class DialogResponseFormatter(ResponseFormatter):
    tsv_keys: Optional[List[str]] = ['serial_num', 'is_pass', 'type_of_output',
                                     'ground_truth', 'acceptable_arguments',
                                     'model_output', 'reasoning', 'query']

    @root_validator(pre=True)
    def set_report_params(cls, values):
        model_request = values.get('request_model', {})
        model_response = values.get('response_model', {})
        evaluate_response = values.get('evaluate_response', {})
        serial_num = model_request['serial_num']
        is_pass = convert_eval_key(evaluate_response)
        type_of_output = model_request['type_of_output']
        ground_truth = json.dumps(model_request['ground_truth'], ensure_ascii=False)
        acceptable_arguments = json.dumps(model_request['acceptable_arguments'], ensure_ascii=False)
        model_output = json.dumps(model_response, ensure_ascii=False)
        
        # 다양한 API 응답 형식 처리
        content = None
        
        # OpenAI API 형식
        if 'choices' in evaluate_response and len(evaluate_response['choices']) > 0:
            if 'message' in evaluate_response['choices'][0] and 'content' in evaluate_response['choices'][0]['message']:
                content = evaluate_response['choices'][0]['message']['content']
        
        # Bedrock API 형식 (Claude)
        elif 'completion' in evaluate_response:
            content = evaluate_response['completion']
        
        # Bedrock API 형식 (다른 모델)
        elif 'results' in evaluate_response and len(evaluate_response['results']) > 0:
            if 'outputText' in evaluate_response['results'][0]:
                content = evaluate_response['results'][0]['outputText']
        
        # 다른 API 형식
        elif 'content' in evaluate_response:
            content = evaluate_response['content']
        
        # 응답에서 내용을 찾을 수 없는 경우
        if content is None:
            print("Warning: Could not find content in API response for reasoning")
            print(f"Response structure: {evaluate_response.keys()}")
            content = "No reasoning available"
        
        reasoning = json.dumps({'reasoning': content}, ensure_ascii=False)
        messages = json.dumps(model_request['messages'], ensure_ascii=False)
        values['report_arguments'] = {
            'serial_num': serial_num,
            'is_pass': is_pass,
            'type_of_output': type_of_output,
            'ground_truth': ground_truth,
            'acceptable_arguments': acceptable_arguments,
            'model_output': model_output,
            'reasoning': reasoning,
            'query': messages
        }
        return values
