import os
import boto3
import ast
from langchain_aws import ChatBedrock
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


class LLM_model:
    def __init__(self, model_id='claude-3-5-sonnet'):
        self.model_id = model_id
        self.llm = None
        if (self.model_id=='claude-3-5-sonnet') | (self.api_key==None):
            self.llm = ChatBedrock(
                model_id=os.getenv('CLAUDE_MODEL_ID'),
                region_name=os.getenv('AWS_DEFAULT_REGION'),
                provider=os.getenv('PROVIDER'),
                model_kwargs=dict(temperature=0, top_p=0.1, max_tokens=5000)
            )
    def invoke(self, message):
        if self.model_id=='claude-3-5-sonnet':
            try:
                reply = self.llm.invoke([message]).content
            except Exception as e:
                reply = str(e)
        else:
            reply = ""

        return reply

