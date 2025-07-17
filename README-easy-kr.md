# FunctionChat-Bench 간편 사용 가이드

FunctionChat-Bench는 한국어 도구 사용(Function Calling) 대화에서 언어 모델의 생성 능력을 평가하기 위한 벤치마크입니다. 이 가이드에서는 벤치마크를 쉽게 실행하는 방법을 소개합니다.

## 개선 사항

포크한 버전에서는 원래 구현에서 다음과 같은 기능들이 추가되었습니다:

- **AWS Bedrock 지원**: 원래 구현에서는 지원하지 않았던 AWS Bedrock API를 통한 모델 평가 기능 추가
- **배치 및 비동기 처리**: 대량의 평가 작업을 효율적으로 처리할 수 있는 배치 처리 및 비동기 호출 기능 추가
- **세분화된 설정 관리**: 평가 답변 생성용 모델과 Judge 판단용 모델의 설정을 분리하여 각각 독립적으로 구성 가능
- **쉘 스크립트 지원**: 복잡한 명령어 없이 간단한 쉘 스크립트로 벤치마크를 쉽게 실행할 수 있는 기능 제공

*참고: 코드 수정의 90%는 Kiro IDE(Sonnet 3.7)를 사용하여 작업되었습니다.*

## 설치

### pip
```bash
cd FunctionChat-Bench
pip3 install -r requirements.txt
```

### uv
```bash
cd FunctionChat-Bench
uv init
uv sync
```

## 환경 설정

1. `.env.example` 파일을 `.env`로 복사하고 API 키 정보를 입력합니다.

```bash
cp .env.example .env
```

2. `.env` 파일을 열고 사용할 모델에 따라 API 키와 엔드포인트 정보를 입력합니다.

## 간편 실행 방법

### 대화 평가 실행 (Dialog)

```bash
# OpenAI 모델로 평가
./run-dialog.sh
```

### 단일 호출 평가 실행 (SingleCall)

```bash
# 모든 도구 유형
./run-singlecall.sh --tools_type all

# 특정 도구 유형만 평가 (exact, 4_random, 4_close, 8_random, 8_close)
./run-singlecall.sh --tools_type exact

```

## 주요 옵션

- `--model`: 평가할 모델 이름 (gpt-4-0125-preview, azure, bedrock 등)
- `--judge_type`: 평가에 사용할 판사 모델 유형 (openai, azure, bedrock)
- `--judge_api_key`: 판사 모델의 API 키 (OpenAI/Azure 사용 시)
- `--judge_aws_secret_key`: AWS 시크릿 키 (Bedrock 판사 모델 사용 시)
- `--batch_size`: 배치 처리할 요청 수 (기본값: 1)
- `--use_async`: 비동기 처리 활성화
- `--tools_type`: SingleCall 평가에서 사용할 도구 유형 (all, exact, 4_random, 4_close, 8_random, 8_close)

## 설정 파일

평가에 필요한 설정은 `config` 디렉토리의 파일들을 수정하여 변경할 수 있습니다:

- `config/openai.cfg`: OpenAI API 평가 설정
- `config/azure.cfg`: Azure OpenAI API 평가 설정
- `config/bedrock.cfg`: AWS Bedrock API 평가 설정
- `config/judge_openai.cfg`: OpenAI 판사 모델 설정
- `config/judge_azure.cfg`: Azure OpenAI 판사 모델 설정
- `config/judge_bedrock.cfg`: AWS Bedrock 판사 모델 설정

## 자세한 사용법

더 자세한 사용법과 평가 방법, 데이터셋 구성 등은 [README.md](README.md)를 참고하세요.
