import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_Hblr5oemsu2R@ep-super-snowflake-adqim63b-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require")
BRIDGIT_AI_API_KEY = os.getenv("BRIDGIT_AI_API_KEY")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ABLY_API_KEY = os.getenv("ABLY_API_KEY")
DOMAIN = "https://bridgit-ai.com"