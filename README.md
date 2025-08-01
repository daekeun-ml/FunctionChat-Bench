# FunctionChat-Bench: Comprehensive Evaluation of Language Model's Generative Capabilities in Korean Tool-use Dialogs

## Introduction

The FunctionChat-Bench is a benchmark dataset specifically designed to evaluate the Tool-Use (Function Calling) capabilities of Language Models within conversational settings.

This dataset is built on Korean dialogs data and is meticulously crafted to precisely assess various functionalities required in both single-turn and multi-turn situations.

![FunctionChat-Bench-img](https://github.com/kakao/FunctionChat-Bench/blob/main/img/example-img.png)

## Dataset Composition

The FunctionChat-Bench consists of the following datasets:

- **SingleCall**
    - SingleCall evaluates how accurately the LM can select and call the necessary function among several options.
    - SingleCall contains four single-turn prompts for each of 25 different functions.
        - For example, for the function 'informDday', there are four dialogs prompts related to it:

            ```
          "오늘이 결혼한지 며칠째야?" (How many days have i been married?)
          "크리스마스까지 얼마나 남았나요?" (How many days are left until Christmas?)
          "1차 심사일이 언제인가요?" (When is the first round of judging?)
          "디데이목록에서 원고마감일 찾아줘" (Find the manuscript deadline in the D-Day list.)
            ```

    - **Five types of tools are defined as follows.**
        - **exact**: Only the target function is provided to the Assistant as a candidate.
        - **4_random**: The target function along with 3 randomly selected functions are provided as candidates to the Assistant.
        - **4_close**: The target function and 3 functions from a similar domain are provided as candidates to the Assistant.
        - **8_random**: The target function along with 7 randomly selected functions are provided as candidates to the Assistant.
        - **8_close**: The target function and 7 functions from a similar domain are provided as candidates to the Assistant.
    - The dataset contains 500 single dialogue turns, combining single-turn prompts built around 25 designated functions with various tools types.
- **Dialog**
    - Dialog contains 45 diverse dialogs scenarios.
    - Each scenario reflects multi-turn interactions between real users and LM.
    - Defines four types of situations and evaluates how accurately the LM provides appropriate responses in each.
    - Examples of each of the four types of situations are included below to aid understanding within the dialog evaluation. 
    - In the dialog evaluation, it assesses how accurately the assistant provides appropriate responses for each type of situation
        - **call**: An LM must accurately select functions and extract the necessary parameters to respond to a user prompt
            
            ```
            tools:
             [{"type":"function","function":{"name":"informWeather","description":"특정 지역의 현재 날씨 정보 제공","parameters":{"type":"object","properties":{"location":{"type":"string","description":"날씨 정보를 가져올 지역 이름"}},"required":["location"]}}},{"type":"function","function":{"name":"add_task","description":"to-do list에 새로운 할 일을 저장합니다.","parameters":{"type":"object","properties":{"task_name":{"type":"string","description":"The name of the task"},"deadline":{"type":"string","description":"The deadline for the task(사용자의 표현 그대로 추출. 예: 다음주 수요일, 내일 7시 등)"}},"required":["task_name","deadline"]}}},{"type":"function","function":{"name":"setupDday","description":"이름과 날짜를 입력받아 디데이 목록에 새로운 디데이를 생성한다.","parameters":{"type":"object","properties":{"ddayName":{"type":"string","description":"디데이의 이름"},"ddayDate":{"type":"string","description":"디데이 날짜(YYYY-MM-DD)"},"includeStartDay":{"type":"boolean","description":"남은 일수 또는 지난 일수 계산시 디데이 당일 날짜를 1일로 포함해 계산할지 여부.(true이면 당일이 1일, false이면 당일이 0일)"}},"required":["ddayName","ddayDate","includeStartDay"]}}},{"type":"function","function":{"name":"informDday","description":"저장된 디데이 목록을 검색해 특정 디데이 정보를 반환한다.","parameters":{"type":"object","properties":{"searchTerm":{"type":"string","description":"디데이 목록을 검색할 디데이의 이름이나 키워드"}},"required":["searchTerm"]}}},{"type":"function","function":{"name":"addMemo","description":"새로운 메모를 추가","parameters":{"type":"object","properties":{"title":{"type":"string","description":"메모의 제목(사용자가 제목을 직접 언급하지 않으면 메모 내용을 통해 적절한 제목을 생성해 지정)"},"content":{"type":"string","description":"메모 내용"}},"required":["title","content"]}}}]
            
            context:
             user: 제리 출국날이 언제였지?
            
            assistant: tool_calls 
                        {"type": "function", "function": {"name": "informDday", "arguments": "{\"searchTerm\": \"제리 출국날\"}"}}
            ```
            
        - **completion**: An LM must generate appropriate responses based on the results of the tool.
            
            ```
            tools:
             [{"type":"function","function":{"name":"informWeather","description":"특정 지역의 현재 날씨 정보 제공","parameters":{"type":"object","properties":{"location":{"type":"string","description":"날씨 정보를 가져올 지역 이름"}},"required":["location"]}}},{"type":"function","function":{"name":"add_task","description":"to-do list에 새로운 할 일을 저장합니다.","parameters":{"type":"object","properties":{"task_name":{"type":"string","description":"The name of the task"},"deadline":{"type":"string","description":"The deadline for the task(사용자의 표현 그대로 추출. 예: 다음주 수요일, 내일 7시 등)"}},"required":["task_name","deadline"]}}},{"type":"function","function":{"name":"setupDday","description":"이름과 날짜를 입력받아 디데이 목록에 새로운 디데이를 생성한다.","parameters":{"type":"object","properties":{"ddayName":{"type":"string","description":"디데이의 이름"},"ddayDate":{"type":"string","description":"디데이 날짜(YYYY-MM-DD)"},"includeStartDay":{"type":"boolean","description":"남은 일수 또는 지난 일수 계산시 디데이 당일 날짜를 1일로 포함해 계산할지 여부.(true이면 당일이 1일, false이면 당일이 0일)"}},"required":["ddayName","ddayDate","includeStartDay"]}}},{"type":"function","function":{"name":"informDday","description":"저장된 디데이 목록을 검색해 특정 디데이 정보를 반환한다.","parameters":{"type":"object","properties":{"searchTerm":{"type":"string","description":"디데이 목록을 검색할 디데이의 이름이나 키워드"}},"required":["searchTerm"]}}},{"type":"function","function":{"name":"addMemo","description":"새로운 메모를 추가","parameters":{"type":"object","properties":{"title":{"type":"string","description":"메모의 제목(사용자가 제목을 직접 언급하지 않으면 메모 내용을 통해 적절한 제목을 생성해 지정)"},"content":{"type":"string","description":"메모 내용"}},"required":["title","content"]}}}]
            
            context: 
             user: 제리 출국날이 언제였지?
             assistant: tool_calls 
                        {"type": "function", "function": {"name": "informDday", "arguments": "{\"searchTerm\": \"제리 출국날\"}"}}
             tool: {"name": "informDday", "content": "{\"ddayName\": \"제리 출국날\", \"ddayDate\": \"2024-04-23\", \"daysRemaining\": 48, \"daysSince\": None}"}
            
            assistant: 제리 출국날은 2024년 4월 23일입니다. 앞으로 48일 남았습니다.
            ```
            
        - **slot**: An LM must query the user for the necessary parameters to make a function call.
            
            ```
            tools:
             [{"type":"function","function":{"name":"informWeather","description":"특정 지역의 현재 날씨 정보 제공","parameters":{"type":"object","properties":{"location":{"type":"string","description":"날씨 정보를 가져올 지역 이름"}},"required":["location"]}}},{"type":"function","function":{"name":"add_task","description":"to-do list에 새로운 할 일을 저장합니다.","parameters":{"type":"object","properties":{"task_name":{"type":"string","description":"The name of the task"},"deadline":{"type":"string","description":"The deadline for the task(사용자의 표현 그대로 추출. 예: 다음주 수요일, 내일 7시 등)"}},"required":["task_name","deadline"]}}},{"type":"function","function":{"name":"setupDday","description":"이름과 날짜를 입력받아 디데이 목록에 새로운 디데이를 생성한다.","parameters":{"type":"object","properties":{"ddayName":{"type":"string","description":"디데이의 이름"},"ddayDate":{"type":"string","description":"디데이 날짜(YYYY-MM-DD)"},"includeStartDay":{"type":"boolean","description":"남은 일수 또는 지난 일수 계산시 디데이 당일 날짜를 1일로 포함해 계산할지 여부.(true이면 당일이 1일, false이면 당일이 0일)"}},"required":["ddayName","ddayDate","includeStartDay"]}}},{"type":"function","function":{"name":"informDday","description":"저장된 디데이 목록을 검색해 특정 디데이 정보를 반환한다.","parameters":{"type":"object","properties":{"searchTerm":{"type":"string","description":"디데이 목록을 검색할 디데이의 이름이나 키워드"}},"required":["searchTerm"]}}},{"type":"function","function":{"name":"addMemo","description":"새로운 메모를 추가","parameters":{"type":"object","properties":{"title":{"type":"string","description":"메모의 제목(사용자가 제목을 직접 언급하지 않으면 메모 내용을 통해 적절한 제목을 생성해 지정)"},"content":{"type":"string","description":"메모 내용"}},"required":["title","content"]}}}]
            
            context: 
             user: 제리 출국날이 언제였지?
             assistant: tool_calls 
                        {"type": "function", "function": {"name": "informDday", "arguments": "{\"searchTerm\": \"제리 출국날\"}"}}
             tool: {"name": "informDday", "content": "{\"ddayName\": \"제리 출국날\", \"ddayDate\": \"2024-04-23\", \"daysRemaining\": 48, \"daysSince\": None}"}
             assistant: 제리 출국날은 2024년 4월 23일입니다. 앞으로 48일 남았습니다.
             user: 송별회 일정 잡기 to do list에 추가해줘.
            
            assistant: 알겠습니다. 데드라인이 언제인가요?
            ```
            
        - **relevance**: An LM must generate an appropriate response when it cannot provide a function for a user prompt.
            
            ```
            tools:
             [{"type":"function","function":{"name":"informWeather","description":"특정 지역의 현재 날씨 정보 제공","parameters":{"type":"object","properties":{"location":{"type":"string","description":"날씨 정보를 가져올 지역 이름"}},"required":["location"]}}},{"type":"function","function":{"name":"add_task","description":"to-do list에 새로운 할 일을 저장합니다.","parameters":{"type":"object","properties":{"task_name":{"type":"string","description":"The name of the task"},"deadline":{"type":"string","description":"The deadline for the task(사용자의 표현 그대로 추출. 예: 다음주 수요일, 내일 7시 등)"}},"required":["task_name","deadline"]}}},{"type":"function","function":{"name":"setupDday","description":"이름과 날짜를 입력받아 디데이 목록에 새로운 디데이를 생성한다.","parameters":{"type":"object","properties":{"ddayName":{"type":"string","description":"디데이의 이름"},"ddayDate":{"type":"string","description":"디데이 날짜(YYYY-MM-DD)"},"includeStartDay":{"type":"boolean","description":"남은 일수 또는 지난 일수 계산시 디데이 당일 날짜를 1일로 포함해 계산할지 여부.(true이면 당일이 1일, false이면 당일이 0일)"}},"required":["ddayName","ddayDate","includeStartDay"]}}},{"type":"function","function":{"name":"informDday","description":"저장된 디데이 목록을 검색해 특정 디데이 정보를 반환한다.","parameters":{"type":"object","properties":{"searchTerm":{"type":"string","description":"디데이 목록을 검색할 디데이의 이름이나 키워드"}},"required":["searchTerm"]}}},{"type":"function","function":{"name":"addMemo","description":"새로운 메모를 추가","parameters":{"type":"object","properties":{"title":{"type":"string","description":"메모의 제목(사용자가 제목을 직접 언급하지 않으면 메모 내용을 통해 적절한 제목을 생성해 지정)"},"content":{"type":"string","description":"메모 내용"}},"required":["title","content"]}}}]
            
            context:
             user: 제리 출국날이 언제였지?
             assistant: tool_calls 
                        {"type": "function", "function": {"name": "informDday", "arguments": "{\"searchTerm\": \"제리 출국날\"}"}}
             tool: {"name": "informDday", "content": "{\"ddayName\": \"제리 출국날\", \"ddayDate\": \"2024-04-23\", \"daysRemaining\": 48, \"daysSince\": None}"}
             assistant: 제리 출국날은 2024년 4월 23일입니다. 앞으로 48일 남았습니다.
             user: 송별회 일정 잡기 to do list에 추가해줘.
             assistant: 알겠습니다. 데드라인이 언제인가요?
             user: 다음주 토요일
             assistant: tool_calls
                         {"type": "function", "function": {"name": "add_task", "arguments": "{\"task_name\": \"송별회 일정 잡기\", \"deadline\": \"다음주 토요일\"}"}}
             tool: {"name": "add_task", "content": "{\"status\": \"success\"}"}
             assistant: 할 일을 등록했습니다
             user: 다빈이한테 괜찮을 때 전화 한번 달라고 문자 남겨줘.
             
            assistant: 문자 전송 기능은 없습니다.
            ```
            

## Evaluation Method

The FunctionChat-Bench utilizes a rubric evaluation method called LLM-as-Judge, where OpenAI GPT-4 serves as the evaluator. This specially designed evaluation system quantitatively measures the performance of each dialogs and function call without human intervention. Using the evaluation rubric, OpenAI GPT-4 assesses the accuracy and relevance of the responses generated by LMs and assigns scores accordingly.

## **Installation**

```bash
cd FunctionChat-Bench
pip3 install -r requirements.txt
```

## **Config**
API settings required for evaluation. 
The evaluation API is configured in config files based on the judge type you want to use:

- `config/openai.cfg`: For OpenAI API evaluation
- `config/azure.cfg`: For Azure OpenAI API evaluation
- `config/bedrock.cfg`: For AWS Bedrock API evaluation

**Judge Model Configuration**: Judge models (LLM-as-Judge) can be configured separately:
- `config/judge_openai.cfg`: For OpenAI API judge model
- `config/judge_azure.cfg`: For Azure OpenAI API judge model  
- `config/judge_bedrock.cfg`: For AWS Bedrock API judge model

**Important**: All sensitive information like API keys are managed through environment variables in the `.env` file for security purposes.

### Environment Variables Setup
Copy the `.env` file and update it with your actual API credentials:

```bash
# OpenAI 설정
OPENAI_API_KEY=your_actual_openai_key_here

# Azure OpenAI 설정
AZURE_OPENAI_API_KEY=your_actual_azure_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_MODEL=gpt-4o

# AWS Bedrock 설정
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=us-west-2
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# 기본 설정
DEFAULT_BATCH_SIZE=1
DEFAULT_JUDGE_TYPE=bedrock

# Judge 모델 설정 (평가용 - LLM-as-Judge)
JUDGE_OPENAI_API_KEY=your_judge_openai_key_here
JUDGE_AZURE_OPENAI_API_KEY=your_judge_azure_key_here
JUDGE_AZURE_OPENAI_ENDPOINT=https://your-judge-resource.openai.azure.com/
JUDGE_AZURE_OPENAI_API_VERSION=2024-02-15-preview
JUDGE_AZURE_OPENAI_MODEL=gpt-4o
JUDGE_AWS_ACCESS_KEY_ID=your_judge_aws_access_key_here
JUDGE_AWS_SECRET_ACCESS_KEY=your_judge_aws_secret_key_here
JUDGE_AWS_REGION=us-west-2
JUDGE_BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

### openai config format 
```
{
  "api_type": "openai",
  "api_key": "${OPENAI_API_KEY}",
  "api_version": "gpt-4-1106-preview",
  "temperature": 0.1,
  "max_tokens": 4096,
  "n": 3
}
```
### openai azure config format 
```
{
  "api_type": "azure",
  "api_key": "${AZURE_OPENAI_API_KEY}",
  "api_base": "${AZURE_OPENAI_ENDPOINT}",
  "api_version": "${AZURE_OPENAI_API_VERSION}",
  "model": "${AZURE_OPENAI_MODEL}",
  "temperature": 0.1,
  "max_tokens": 4096,
  "n": 3
}
```

### aws bedrock config format
```
{
  "api_type": "bedrock",
  "api_key": "${AWS_ACCESS_KEY_ID}",
  "aws_secret_key": "${AWS_SECRET_ACCESS_KEY}",
  "aws_region": "${AWS_REGION}",
  "bedrock_model_id": "${BEDROCK_MODEL_ID}",
  "temperature": 0.1,
  "max_tokens": 4096,
  "n": 3
}
```

## Evaluation

### Using Shell Scripts

The easiest way to run evaluations is using the provided shell scripts:

```bash
# Run dialog evaluation
./run-dialog.sh --model gpt-4-0125-preview --judge_type openai --judge_api_key YOUR_JUDGE_API_KEY

# Run singlecall evaluation
./run-singlecall.sh --model gpt-4-0125-preview --judge_type openai --judge_api_key YOUR_JUDGE_API_KEY --tools_type all

# Run with Bedrock judge model
./run-dialog.sh --model gpt-4-0125-preview --judge_type bedrock --judge_aws_secret_key YOUR_JUDGE_AWS_SECRET_KEY --judge_bedrock_model_id anthropic.claude-3-sonnet-20240229-v1:0
```

Available options for the scripts:
- `--model`: Model name to evaluate (e.g., gpt-4-0125-preview, bedrock, etc.)
- `--judge_type`: Type of judge to use for evaluation (openai, azure, bedrock)
- `--judge_api_key`: API key for the judge model (OpenAI/Azure)
- `--judge_aws_secret_key`: AWS secret key for judge model (Bedrock only)
- `--judge_aws_region`: AWS region for judge model (Bedrock only, default: us-west-2)
- `--judge_bedrock_model_id`: Bedrock model ID for judge (default: anthropic.claude-3-sonnet-20240229-v1:0)
- `--batch_size`: Number of requests to process in a batch (default: 3)
- `--use_async`: Enable asynchronous processing
- `--aws_region`: AWS region for Bedrock (default: us-west-2)
- `--bedrock_model_id`: Bedrock model ID (default: anthropic.claude-3-sonnet-20240229-v1:0)
- `--tools_type`: Tool type for singlecall evaluation (all, 4_random, 4_close, 8_random, 8_close)

### Using Python Directly

Evaluation for openai api

```bash
# run dialog evaluation
python3 evaluate.py dialog \
--input_path data/FunctionChat-Dialog.jsonl \
--system_prompt_path data/system_prompt.txt \
--temperature 0.1 \
--model {model_name} \
--api_key {api_key} \
--judge_type openai \
--judge_api_key {judge_api_key}

# run singlecall evaluation
python3 evaluate.py singlecall \
--input_path data/FunctionChat-Singlecall.jsonl \
--tools_type all \
--system_prompt_path data/system_prompt.txt \
--temperature 0.1 \
--model {model_name} \
--api_key {api_key} \
--judge_type openai \
--judge_api_key {judge_api_key}
```
- A model_name like `gpt-3.5-turbo-0125` is needed. 

Evaluation for local api

```bash
# run dialog evaluation
python3 evaluate.py dialog \
--input_path data/FunctionChat-Dialog.jsonl \
--system_prompt_path data/system_prompt.txt \
--temperature 0.1 \
--model inhouse \
--base_url {base_url} \
--api_key {api_key} \
--model_path {model_path} \
--judge_type bedrock \
--judge_aws_secret_key {judge_aws_secret_key} \
--judge_bedrock_model_id {judge_bedrock_model_id}

# run singlecall evaluation
python3 evaluate.py singlecall \
--input_path data/FunctionChat-Singlecall.jsonl \
--tools_type all \
--system_prompt_path data/system_prompt.txt \
--temperature 0.1 \
--model inhouse \
--base_url {base_url} \
--api_key {api_key} \
--model_path {model_path} \
--judge_type bedrock \
--judge_aws_secret_key {judge_aws_secret_key} \
--judge_bedrock_model_id {judge_bedrock_model_id}
```

- If the `model_path` is required in the request header, add the `--model_path` parameter.
- Follows OpenAI's API specifications.

Evaluation for gemini api

```bash
# run dialog evaluation
python3 evaluate.py dialog \
--input_path data/FunctionChat-Dialog.jsonl \
--system_prompt_path data/system_prompt.txt \
--temperature 0.1 \
--model {gemini_model_name} \
--gcloud_project_id {base_url} \
--gcloud_location {api_key} 

# run singlecall evaluation
python3 evaluate.py singlecall \
--input_path data/FunctionChat-Singlecall.jsonl \
--tools_type all \
--system_prompt_path data/system_prompt.txt \
--temperature 0.1 \
--model {gemini_model_name} \
--gcloud_project_id {base_url} \
--gcloud_location {api_key} 
```
- A gemini_model_name like `gemini-1.0-pro-002` is needed.
- For installing the gcloud CLI to use the Gemini API, you can set it up by following the link below.
  https://cloud.google.com/sdk/docs/install

Evaluation for mistral api

```
# run dialog evaluation
python3 evaluate.py dialog \
--input_path data/FunctionChat-Dialog.jsonl \
--system_prompt_path data/system_prompt.txt \
--temperature 0.1 \
--model {mistral_model_name} \
--api_key {api_key} 

# run singlecall evaluation
python3 evaluate.py singlecall \
--input_path data/FunctionChat-Singlecall.jsonl \
--tools_type all \
--system_prompt_path data/system_prompt.txt \
--temperature 0.1 \
--model {mistral_model_name} \
--api_key {api_key} 
```
- A mistral_model_name like `mistral-small-latest` is needed.

Evaluation for solar api

```
# run dialog evaluation
python3 evaluate.py dialog \
--input_path data/FunctionChat-Dialog.jsonl \
--system_prompt_path data/system_prompt.txt \
--temperature 0.1 \
--model {solar_model_name} \
--base_url {base_url} \
--api_key {api_key} 

# run singlecall evaluation
python3 evaluate.py singlecall \
--input_path data/FunctionChat-Singlecall.jsonl \
--tools_type all \
--system_prompt_path data/system_prompt.txt \
--temperature 0.1 \
--model {solar_model_name} \
--base_url {base_url} \
--api_key {api_key} 
```
- A solar_model_name like `solar-1-mini-chat-240502` is needed. 

## Additional option - **common**
An option added to support a highly compatible data structure that allows for flexible content specification.

```
# openai evaluation
python3 evaluate.py common \
--input_path data/{common-evaluation-file}.jsonl \
--temperature 0.1 \
--model {model_name} \
--api_key {api_key} 

# inhouse evaluation
python3 evaluate.py common \
--input_path data/{common-evaluation-file}.jsonl \
--temperature 0.1 \
--model inhouse \
--base_url {base_url} \
--api_key {api_key} \
--model_path {model_path}
```
- {common-evaluation-file}.jsonl : An evaluation dataset file in a format that follows the common option.


# License

This software is licensed under the Apache 2 license, quoted below.

Copyright 2024 Kakao Corp. http://www.kakaocorp.com

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this project except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

# Citation 
```
@misc{lee2024functionchatbenchcomprehensiveevaluationlanguage,
      title={FunctionChat-Bench: Comprehensive Evaluation of Language Models' Generative Capabilities in Korean Tool-use Dialogs}, 
      author={Shinbok Lee and Gaeun Seo and Daniel Lee and Byeongil Ko and Sunghee Jung and Myeongcheol Shin},
      year={2024},
      eprint={2411.14054},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2411.14054}, 
}
```
