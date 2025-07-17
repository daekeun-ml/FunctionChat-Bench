import json
import asyncio
from tqdm import tqdm
from src import utils
from src.api_executor import APIExecutorFactory


class ResponseHandler:
    """
    A class responsible for managing API responses, including loading cached responses.
    """
    def __init__(self, model, api_key, base_url, model_path, gcloud_project_id, gcloud_location, 
                aws_secret_key=None, aws_region=None, bedrock_model_id=None, batch_size=1, use_async=False):
        """
        Initializes the ResponseHandler with a specific API executor based on the model configuration.

        Parameters:
            model (str): The model identifier used for the API executor.
            api_key (str): API key for authentication with the API service.
            base_url (str): Base URL of the API service.
            model_path (str): Path to the model (if applicable).
            gcloud_project_id (str): Google Cloud project ID (if applicable).
            gcloud_location (str): Location of the Google Cloud project (if applicable).
            aws_secret_key (str, optional): AWS 시크릿 액세스 키 (Bedrock 모델용)
            aws_region (str, optional): AWS 리전 (Bedrock 모델용)
            bedrock_model_id (str, optional): Bedrock 모델 ID
            batch_size (int, optional): 배치 처리 크기
            use_async (bool, optional): 비동기 처리 여부
        """
        self.executor = APIExecutorFactory().get_model_api(
            model_name=model, 
            api_key=api_key,
            base_url=base_url, 
            model_path=model_path,
            gcloud_project_id=gcloud_project_id,
            gcloud_location=gcloud_location,
            aws_secret_key=aws_secret_key,
            aws_region=aws_region,
            bedrock_model_id=bedrock_model_id
        )
        self.batch_size = batch_size
        self.use_async = use_async

    def load_cached_response(self, predict_file_path, max_size):
        """
        Loads cached responses from a file if available and the number of responses meets the max size.

        Parameters:
            predict_file_path (str): Path to the file containing cached responses.
            max_size (int): Maximum number of responses expected.

        Returns:
            list: A list of cached responses if they exist and meet the expected size; otherwise, an empty list.
        """
        if utils.is_exist_file(predict_file_path):
            outputs = utils.load_to_jsonl(predict_file_path)
            if len(outputs) == max_size:
                print(f"[[already existed response jsonl file]]\npath : {predict_file_path}")
                return outputs
            else:
                print(f"[[continue .. {len(outputs)}/{max_size}]]\n")
                return outputs
        return []

    async def predict_async(self, api_request):
        """
        비동기적으로 API 요청을 처리합니다.
        
        Parameters:
            api_request (dict): API 요청 데이터
            
        Returns:
            dict: API 응답 데이터
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.executor.predict, api_request)
    
    async def process_batch_async(self, batch_requests, fp):
        """
        배치 요청을 비동기적으로 처리합니다.
        
        Parameters:
            batch_requests (list): 배치 처리할 API 요청 목록
            fp (file): 결과를 저장할 파일 객체
            
        Returns:
            list: 응답 결과 목록
        """
        tasks = [self.predict_async(request) for request in batch_requests]
        batch_results = await asyncio.gather(*tasks)
        
        # 결과 저장
        for result in batch_results:
            fp.write(f'{json.dumps(result, ensure_ascii=False)}\n')
            
        return batch_results
    
    def process_batch(self, batch_requests, fp):
        """
        배치 요청을 동기적으로 처리합니다.
        
        Parameters:
            batch_requests (list): 배치 처리할 API 요청 목록
            fp (file): 결과를 저장할 파일 객체
            
        Returns:
            list: 응답 결과 목록
        """
        batch_results = []
        for request in batch_requests:
            result = self.executor.predict(request)
            batch_results.append(result)
            fp.write(f'{json.dumps(result, ensure_ascii=False)}\n')
            
        return batch_results

    def fetch_and_save(self, api_request_list, predict_file_path, reset, sample, debug):
        """
        Fetches responses from the API and saves them. If responses are partially cached, it continues from where it left off.

        Parameters:
            api_request_list (list): List of API requests to process.
            predict_file_path (str): File path to save the responses.
            reset (bool): If True, it overwrite existing cached responses; if False, append to them.
            sample (bool): If True, it executes only a single input to fetch the response. (e.g., for quick testing).
            debug (bool): If True, it print detailed debug information.

        Returns:
            list: A list of all responses fetched and saved.
        """
        outputs = []
        # 1. check continuos
        if reset is False:
            outputs = self.load_cached_response(predict_file_path, len(api_request_list))
            if len(outputs) == len(api_request_list):
                return outputs
        write_option = 'a' if reset is False else 'w'
        start_index = len(outputs)
        
        # 2. fetch
        print(f" ** start index : {start_index} ..(reset is {reset})")
        print(f" ** batch size : {self.batch_size}, async mode : {self.use_async}")
        
        # 샘플 모드인 경우 한 개만 처리
        if sample:
            api_request_list = api_request_list[start_index:start_index+1]
        else:
            api_request_list = api_request_list[start_index:]
        
        with open(predict_file_path, write_option) as fp:
            # 배치 처리
            if self.batch_size > 1:
                # 배치 단위로 분할
                batches = [api_request_list[i:i+self.batch_size] 
                          for i in range(0, len(api_request_list), self.batch_size)]
                
                # 비동기 처리
                if self.use_async:
                    loop = asyncio.get_event_loop()
                    for batch in tqdm(batches):
                        batch_results = loop.run_until_complete(self.process_batch_async(batch, fp))
                        outputs.extend(batch_results)
                # 동기 처리
                else:
                    for batch in tqdm(batches):
                        batch_results = self.process_batch(batch, fp)
                        outputs.extend(batch_results)
            # 단일 처리 (기존 방식)
            else:
                for api_request in tqdm(api_request_list):
                    response_output = self.executor.predict(api_request)
                    outputs.append(response_output)
                    fp.write(f'{json.dumps(response_output, ensure_ascii=False)}\n')
        
        print(f"[[model response file : {predict_file_path}]]")
        return outputs
