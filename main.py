import discord
from discord.ext import commands
import os
import sqlite3
from dotenv import load_dotenv
from events import setup_events
from commands import setup_commands

# .env 파일 로드
load_dotenv()

# 환경 변수에서 토큰 가져오기
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# 봇 인스턴스 생성
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# 데이터베이스 연결 (봇 실행 시 한 번만)
db_path = os.path.join(os.path.dirname(__file__), 'user_data.db')
bot.conn = sqlite3.connect(db_path)
bot.cursor = bot.conn.cursor()
bot.cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_prompts (
        user_id INTEGER PRIMARY KEY,
        system_prompt TEXT
    )
''')
bot.conn.commit()

# 이벤트와 명령어 설정
setup_commands(bot)
setup_events(bot)

# 봇 실행
bot.run(DISCORD_TOKEN)