#!/usr/bin/env python3

import os
import click
import inspect
import dotenv

from src import utils
from src.default_click_type import (
    DefaultBaseUrlPromptOptions,
    DefaultModelPathPromptOptions,
    DefaultResetPromptOptions,
    DefaultSamplePromptOptions,
    DefaultDebugPromptOptions,
    DefaultGPidPromptOptions,
    DefaultGLocPromptOptions,
    DefaultApiKeyPromptOptions,
    DefaultUseAsyncPromptOptions
)

# .env 파일 로드
dotenv.load_dotenv()

from src.payload_creator import PayloadCreatorFactory
from src.response_handler import ResponseHandler
from src.evaluation_handler import EvaluationHandler


REPO_PATH = os.path.dirname(os.path.abspath(__file__))


# program options
@click.group()
@click.option("-q", help="disable all prompts", flag_value=True, default=True)
@click.pass_context
def cli(ctx, q):
    ctx.ensure_object(dict)
    ctx.obj['q'] = q


def default_eval_options(f):
    f = click.option('--model', prompt='model name', help='gpt-3.5-turbo, gpt-4, bedrock ..etc')(f)
    f = click.option('--input_path', prompt='input file path', help='golden set file name (*.jsonl)')(f)
    # test option
    f = click.option('--reset', prompt='recreate request file', help='reset request file', cls=DefaultResetPromptOptions)(f)
    f = click.option('--sample', prompt='Run only 1 case.', help='run sample', cls=DefaultSamplePromptOptions)(f)
    f = click.option('--debug', prompt='debug flag', help='debugging', cls=DefaultDebugPromptOptions)(f)
    # openai type
    f = click.option('--temperature', prompt='temperature', help='generate temperature', default=0.1)(f)
    f = click.option('--api_key', prompt='model api key', help='api key', cls=DefaultApiKeyPromptOptions)(f)
    f = click.option('--base_url', prompt='model api url', help='base url', cls=DefaultBaseUrlPromptOptions)(f)
    # openai - hosting server type
    f = click.option('--model_path', prompt='inhouse model path', help='model path in header', cls=DefaultModelPathPromptOptions)(f)
    # gemini
    f = click.option('--gcloud_project_id', prompt='gemini project id', help='google pid', cls=DefaultGPidPromptOptions)(f)
    f = click.option('--gcloud_location', prompt='gemini location', help='google cloud location', cls=DefaultGLocPromptOptions)(f)
    # bedrock
    f = click.option('--aws_secret_key', prompt='aws secret key', help='AWS Secret Access Key', default=None)(f)
    f = click.option('--aws_region', prompt='aws region', help='AWS Region', default='us-west-2')(f)
    f = click.option('--bedrock_model_id', prompt='bedrock model id', help='Bedrock Model ID', default='anthropic.claude-3-sonnet-20240229-v1:0')(f)
    # batch processing
    f = click.option('--batch_size', prompt='batch size', help='Batch processing size', default=1, type=int)(f)
    f = click.option('--use_async', prompt='use async', help='Use async processing', is_flag=True, default=False, cls=DefaultUseAsyncPromptOptions)(f)
    # evaluation
    f = click.option('--only_exact', prompt='evaluate exact match', help='only exact match(True, False)', cls=DefaultDebugPromptOptions)(f)
    # judge model settings
    f = click.option('--judge_type', prompt='judge type', help='judge type (openai, azure, bedrock)', default='bedrock')(f)
    f = click.option('--judge_api_key', prompt='judge api key', help='judge api key', default=None)(f)
    f = click.option('--judge_aws_secret_key', prompt='judge aws secret key', help='Judge AWS Secret Access Key', default=None)(f)
    f = click.option('--judge_aws_region', prompt='judge aws region', help='Judge AWS Region', default='us-west-2')(f)
    f = click.option('--judge_bedrock_model_id', prompt='judge bedrock model id', help='Judge Bedrock Model ID', default='anthropic.claude-3-sonnet-20240229-v1:0')(f)
    return f


def dialog_eval_options(f):
    f = click.option('--system_prompt_path', prompt='system_prompt_path', help='system prompt file path')(f)
    return f


def singlecall_eval_options(f):
    f = click.option('--system_prompt_path', prompt='system_prompt_path', help='system prompt file path')(f)
    f = click.option('--tools_type', prompt='tools type', help='tools_type = {exact, 4_random, 4_close, 8_random, 8_close}')(f)
    return f


# program command
@cli.command()
@default_eval_options
@dialog_eval_options
def dialog(model,
           input_path, system_prompt_path,
           temperature, api_key, base_url, model_path,
           reset, sample, debug,
           gcloud_project_id, gcloud_location, 
           aws_secret_key, aws_region, bedrock_model_id,
           batch_size, use_async, only_exact,
           judge_type, judge_api_key, judge_aws_secret_key, judge_aws_region, judge_bedrock_model_id):
    eval_type = inspect.stack()[0][3]
    TEST_PREFIX = f'FunctionChat-{eval_type.capitalize()}'

    print(f"[[{model} {TEST_PREFIX} evaluate start]]")
    utils.create_directory(f'{REPO_PATH}/output/')

    request_file_path = f'{REPO_PATH}/output/{TEST_PREFIX}.input.jsonl'
    predict_file_path = f'{REPO_PATH}/output/{TEST_PREFIX}.{model}.output.jsonl'
    eval_file_path = f'{REPO_PATH}/output/{TEST_PREFIX}.{model}.eval.jsonl'
    eval_log_file_path = f'{REPO_PATH}/output/{TEST_PREFIX}.{model}.eval_report.tsv'

    api_request_list = PayloadCreatorFactory.get_payload_creator(
        eval_type, temperature, system_prompt_path
    ).create_payload(
        input_file_path=input_path, request_file_path=request_file_path, reset=reset)
    api_response_list = ResponseHandler(
        model, api_key, base_url, model_path, 
        gcloud_project_id, gcloud_location,
        aws_secret_key, aws_region, bedrock_model_id,
        batch_size, use_async
    ).fetch_and_save(
        api_request_list, predict_file_path, reset, sample, debug
    )
    EvaluationHandler(eval_type, judge_type, judge_api_key, judge_aws_secret_key, judge_aws_region, judge_bedrock_model_id).evaluate(
        api_request_list, api_response_list,
        eval_file_path, eval_log_file_path,
        reset, sample, debug
    )


@cli.command()
@default_eval_options
@singlecall_eval_options
def singlecall(model,
               input_path, tools_type,
               system_prompt_path,
               temperature, api_key, base_url, model_path,
               reset, sample, debug, only_exact,
               gcloud_project_id, gcloud_location,
               aws_secret_key, aws_region, bedrock_model_id,
               batch_size, use_async,
               judge_type, judge_api_key, judge_aws_secret_key, judge_aws_region, judge_bedrock_model_id):

    eval_type = inspect.stack()[0][3]
    TEST_PREFIX = f'FunctionChat-{eval_type.capitalize()}'

    print(f"[[{model} {TEST_PREFIX} {tools_type} evaluate start]]")
    utils.create_directory(f'{REPO_PATH}/output/')

    request_file_path = f'{REPO_PATH}/output/{TEST_PREFIX}.input.jsonl'
    predict_file_path = f'{REPO_PATH}/output/{TEST_PREFIX}.{model}.{tools_type}.output.jsonl'
    eval_file_path = f'{REPO_PATH}/output/{TEST_PREFIX}.{model}.{tools_type}.eval.jsonl'
    eval_log_file_path = f'{REPO_PATH}/output/{TEST_PREFIX}.{model}.{tools_type}.eval_report.tsv'

    api_request_list = PayloadCreatorFactory.get_payload_creator(
        eval_type, temperature, system_prompt_path
    ).create_payload(
        input_file_path=input_path, request_file_path=request_file_path,
        reset=reset, tools_type=tools_type
    )
    api_response_list = ResponseHandler(
        model, api_key, base_url, model_path,
        gcloud_project_id, gcloud_location,
        aws_secret_key, aws_region, bedrock_model_id,
        batch_size, use_async
    ).fetch_and_save(
        api_request_list, predict_file_path, reset, sample, debug
    )
    EvaluationHandler(eval_type, judge_type, judge_api_key, judge_aws_secret_key, judge_aws_region, judge_bedrock_model_id).evaluate(
        api_request_list, api_response_list,
        eval_file_path, eval_log_file_path,
        reset, sample, debug, only_exact
    )


@cli.command()
@default_eval_options
def common(model, input_path,
           temperature, api_key, base_url, model_path,
           reset, sample, debug, only_exact,
           gcloud_project_id, gcloud_location,
           aws_secret_key, aws_region, bedrock_model_id,
           batch_size, use_async,
           judge_type, judge_api_key, judge_aws_secret_key, judge_aws_region, judge_bedrock_model_id):

    eval_type = inspect.stack()[0][3]
    TEST_PREFIX = os.path.splitext(os.path.basename(input_path))[0]

    print(f"[[{model} {TEST_PREFIX} evaluate start]]")
    utils.create_directory(f'{REPO_PATH}/output/')

    request_file_path = f'{REPO_PATH}/output/{TEST_PREFIX}.input.jsonl'
    predict_file_path = f'{REPO_PATH}/output/{TEST_PREFIX}.{model}.output.jsonl'
    eval_file_path = f'{REPO_PATH}/output/{TEST_PREFIX}.{model}.eval.jsonl'
    eval_log_file_path = f'{REPO_PATH}/output/{TEST_PREFIX}.{model}.eval_report.tsv'

    api_request_list = PayloadCreatorFactory.get_payload_creator(
        eval_type, temperature
    ).create_payload(
        input_file_path=input_path, request_file_path=request_file_path,
        reset=reset
    )
    api_response_list = ResponseHandler(
        model, api_key, base_url, model_path,
        gcloud_project_id, gcloud_location,
        aws_secret_key, aws_region, bedrock_model_id,
        batch_size, use_async
    ).fetch_and_save(
        api_request_list, predict_file_path, reset, sample, debug
    )
    EvaluationHandler(eval_type, judge_type, judge_api_key, judge_aws_secret_key, judge_aws_region, judge_bedrock_model_id).evaluate(
        api_request_list, api_response_list,
        eval_file_path, eval_log_file_path,
        reset, sample, debug, only_exact
    )


if __name__ == '__main__':
    cli()
