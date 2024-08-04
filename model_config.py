import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
MODEL = 'gpt-4o-mini'

llm_config = {
    "config_list": [
        {
            "model": MODEL,
            "api_key": OPENAI_API_KEY
        },
    ],
    "cache_seed": 42,
}
