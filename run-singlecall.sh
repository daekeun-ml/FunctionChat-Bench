#!/bin/bash

# .env 파일에서 환경 변수 로드
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# 기본 설정값 (환경 변수가 설정되어 있으면 해당 값 사용)
BATCH_SIZE=${DEFAULT_BATCH_SIZE:-3}
USE_ASYNC=false
export DEFAULT_JUDGE_TYPE=${DEFAULT_JUDGE_TYPE:-"bedrock"}
MODEL="bedrock"
AWS_REGION=${AWS_REGION:-"us-west-2"}
BEDROCK_MODEL_ID=${BEDROCK_MODEL_ID:-"anthropic.claude-3-sonnet-20240229-v1:0"}
TOOLS_TYPE="all"

# Judge 모델 설정 (기본값은 환경변수에서 가져옴)
JUDGE_TYPE=${DEFAULT_JUDGE_TYPE}
JUDGE_API_KEY=""
JUDGE_AWS_SECRET_KEY=${JUDGE_AWS_SECRET_ACCESS_KEY}
JUDGE_AWS_REGION=${JUDGE_AWS_REGION:-"us-west-2"}
JUDGE_BEDROCK_MODEL_ID=${JUDGE_BEDROCK_MODEL_ID:-"anthropic.claude-3-sonnet-20240229-v1:0"}

# 명령줄 인자 처리
while [[ $# -gt 0 ]]; do
  case $1 in
    --batch_size)
      BATCH_SIZE="$2"
      shift 2
      ;;
    --use_async)
      USE_ASYNC=true
      shift
      ;;
    --judge_type)
      JUDGE_TYPE="$2"
      shift 2
      ;;
    --judge_api_key)
      JUDGE_API_KEY="$2"
      shift 2
      ;;
    --judge_aws_secret_key)
      JUDGE_AWS_SECRET_KEY="$2"
      shift 2
      ;;
    --judge_aws_region)
      JUDGE_AWS_REGION="$2"
      shift 2
      ;;
    --judge_bedrock_model_id)
      JUDGE_BEDROCK_MODEL_ID="$2"
      shift 2
      ;;
    --model)
      MODEL="$2"
      shift 2
      ;;
    --aws_region)
      AWS_REGION="$2"
      shift 2
      ;;
    --bedrock_model_id)
      BEDROCK_MODEL_ID="$2"
      shift 2
      ;;
    --tools_type)
      TOOLS_TYPE="$2"
      shift 2
      ;;
    *)
      # 알 수 없는 옵션
      echo "알 수 없는 옵션: $1"
      echo "사용법: $0 [--batch_size 숫자] [--use_async] [--judge_type azure|openai|bedrock] [--judge_api_key 키] [--judge_aws_secret_key 키] [--judge_aws_region 리전] [--judge_bedrock_model_id 모델ID] [--model bedrock|gpt-4|...] [--aws_region 리전] [--bedrock_model_id 모델ID] [--tools_type all|4_random|4_close|8_random|8_close]"
      exit 1
      ;;
  esac
done

# 설정 파일 업데이트
CONFIG_FILE="config/judge_${JUDGE_TYPE}.cfg"
if [ ! -f "$CONFIG_FILE" ]; then
  CONFIG_FILE="config/${JUDGE_TYPE}.cfg"
fi

# batch_size 설정
if [ -f "$CONFIG_FILE" ]; then
  if grep -q "\"batch_size\":" $CONFIG_FILE; then
    sed -i '' "s/\"batch_size\":[[:space:]]*[0-9]*/\"batch_size\": $BATCH_SIZE/" $CONFIG_FILE 2>/dev/null || sed -i "s/\"batch_size\":[[:space:]]*[0-9]*/\"batch_size\": $BATCH_SIZE/" $CONFIG_FILE
  else
    # batch_size가 없으면 추가
    sed -i '' "s/{/{\"batch_size\": $BATCH_SIZE, /" $CONFIG_FILE 2>/dev/null || sed -i "s/{/{\"batch_size\": $BATCH_SIZE, /" $CONFIG_FILE
  fi
fi

echo "실행 설정:"
echo "- 평가 대상 모델: $MODEL"
echo "- 판사 모델 유형: $JUDGE_TYPE"
echo "- 도구 유형: $TOOLS_TYPE"
echo "- 배치 크기: $BATCH_SIZE"
echo "- 비동기 처리: $USE_ASYNC"
echo "- AWS 리전: $AWS_REGION"
echo "- Bedrock 모델 ID: $BEDROCK_MODEL_ID"
echo "- Judge AWS 리전: $JUDGE_AWS_REGION"
echo "- Judge Bedrock 모델 ID: $JUDGE_BEDROCK_MODEL_ID"

# API 키 설정 (모델에 따라 다른 API 키 사용)
if [ "$MODEL" = "azure" ]; then
  API_KEY=${AZURE_OPENAI_API_KEY}
elif [ "$MODEL" = "bedrock" ]; then
  API_KEY=${AWS_ACCESS_KEY_ID}
else
  API_KEY=${OPENAI_API_KEY}
fi

# 모델 실행
ASYNC_FLAG=""
if [ "$USE_ASYNC" = true ]; then
  ASYNC_FLAG="--use_async"
fi

# tools_type이 "all"인 경우 모든 타입에 대해 실행
if [ "$TOOLS_TYPE" = "all" ]; then
  for type in "exact" "4_random" "4_close" "8_random" "8_close"; do
    echo "=== $type 평가 시작 ==="
    python evaluate.py -q singlecall \
    --input_path data/FunctionChat-Singlecall.jsonl \
    --tools_type $type \
    --system_prompt_path data/system_prompt.txt \
    --temperature 0.1 \
    --model $MODEL \
    --api_key "$API_KEY" \
    --aws_secret_key "${AWS_SECRET_ACCESS_KEY}" \
    --aws_region $AWS_REGION \
    --bedrock_model_id $BEDROCK_MODEL_ID \
    --batch_size $BATCH_SIZE \
    --judge_type $JUDGE_TYPE \
    --judge_api_key "$JUDGE_API_KEY" \
    --judge_aws_secret_key "$JUDGE_AWS_SECRET_KEY" \
    --judge_aws_region $JUDGE_AWS_REGION \
    --judge_bedrock_model_id $JUDGE_BEDROCK_MODEL_ID \
    $ASYNC_FLAG
  done
else
  # 특정 tools_type에 대해서만 실행
  python evaluate.py -q singlecall \
  --input_path data/FunctionChat-Singlecall.jsonl \
  --tools_type $TOOLS_TYPE \
  --system_prompt_path data/system_prompt.txt \
  --temperature 0.1 \
  --model $MODEL \
  --api_key "$API_KEY" \
  --aws_secret_key "${AWS_SECRET_ACCESS_KEY}" \
  --aws_region $AWS_REGION \
  --bedrock_model_id $BEDROCK_MODEL_ID \
  --batch_size $BATCH_SIZE \
  --judge_type $JUDGE_TYPE \
  --judge_api_key "$JUDGE_API_KEY" \
  --judge_aws_secret_key "$JUDGE_AWS_SECRET_KEY" \
  --judge_aws_region $JUDGE_AWS_REGION \
  --judge_bedrock_model_id $JUDGE_BEDROCK_MODEL_ID \
  $ASYNC_FLAG
fi
