import os
from openai import AzureOpenAI
endpoint = "https://kraft-050.openai.azure.com"
model_name = "gpt-4o-mini"
deployment = "gpt-4o-mini"

api_version = "2024-12-01-preview"
client = AzureOpenAI(
 api_version=api_version,
 azure_endpoint=endpoint,
 api_key=os.getenv("AZURE_KEY"),
)