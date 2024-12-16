from discord.ext import commands
import google.generativeai as genai
import json

from google.ai.generativelanguage_v1beta.types import content
from collections import defaultdict, deque
import requests
import os
import random
from dotenv import load_dotenv
load_dotenv()

# Google GenAI 설정
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
genai.configure(api_key=GENAI_API_KEY)

def get_function_definitions():
    return [
        genai.protos.FunctionDeclaration(
            name="roll_dice",
            description="유저가 명시적으로 주사위를 요구할떄 주사위를 돌려주는 도구입니다.",
            parameters=content.Schema(
                type=content.Type.OBJECT,
                properties={
                    "sides": content.Schema(
                        type=content.Type.INTEGER,
                        description="Number of sides on the dice."
                    ),
                },
                required=["sides"],
            ),
        ),
        genai.protos.FunctionDeclaration(
            name="weather",
            description="유저가 명시적으로 날씨를 물어볼떄 사용하는 날씨도구입니다.",
            parameters=content.Schema(
                type=content.Type.OBJECT,
                properties={
                    "location": content.Schema(
                        type=content.Type.STRING,
                        description="The location for the weather report. (반드시 영어로)"
                    ),
                },
                required=["location"],
            ),
        ),
        genai.protos.FunctionDeclaration(
            name="google_search",
            description="유저가 명시적으로 구글 검색을 이용할떄 사용하는 날씨도구입니다.",
            parameters=content.Schema(
                type=content.Type.OBJECT,
                properties={
                    "query": content.Schema(
                        type=content.Type.STRING,
                        description="검색어"
                    ),
                },
                required=["query"],
            ),
        ),
        genai.protos.FunctionDeclaration(
            name="get_user_settings",
            description="유저가 명시적으로 세팅 로드를 요구할때 호출하는 도구입니다.",
            parameters=content.Schema(
                type=content.Type.OBJECT,
                properties={
                    "user_id": content.Schema(
                        type=content.Type.STRING,
                        description="The ID of the user."
                    ),
                },
                required=["user_id"],
            ),
        ),
    ]

# 사용자별 채팅 기록 저장
user_chat_history = defaultdict(lambda: deque(maxlen=10))

# 날씨 API 호출 함수
async def fetch_weather(location):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=metric&lang=kr"
    response = requests.get(url)
    data = response.json()

    if data.get("cod") == 200:
        description = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return f"{location}의 현재 날씨는 {description}이며, 온도는 {temp}°C입니다."
    else:
        return f"{location}의 날씨 정보를 가져올 수 없습니다."

import discord

async def fetch_google_search(query):
    url = f"https://serpapi.com/search.json?q={query}&api_key={SERPAPI_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "error" not in data:
        results = data.get("organic_results", [])
        if results:
            embed_list = []
            for idx, res in enumerate(results[:3]):  # 상위 3개의 결과만 표시
                # 검색 결과의 세부 정보 추출
                title = res.get("title", "제목 없음")
                link = res.get("link", "링크 없음")
                snippet = res.get("snippet", "설명이 없습니다.")
                source = res.get("source", "출처 정보 없음")
                thumbnail = res.get("thumbnail")  # 썸네일 URL (있을 경우만 사용)

                # Discord Embed 생성
                embed = discord.Embed(
                    title=title,  # 제목
                    url=link,  # 링크 연결
                    description=f"{snippet}\n\n**출처:** {source}"  # 설명 및 출처
                )
                embed.set_footer(text=f"검색 결과 {idx + 1}")  # 순번 표시
                if thumbnail:  # 썸네일이 있을 경우 이미지 추가
                    embed.set_thumbnail(url=thumbnail)

                embed_list.append(embed)

            return embed_list  # 생성된 Embed 리스트 반환
        else:
            return [discord.Embed(
                title="검색 결과 없음",
                description=f"'{query}'에 대한 검색 결과를 찾을 수 없습니다.",
                color=discord.Color.red()
            )]
    else:
        return [discord.Embed(
            title="오류 발생",
            description="구글 검색 API 호출 중 문제가 발생했습니다.",
            color=discord.Color.red()
        )]


# 사용자 설정 조회 함수
def get_user_settings(bot, user_id):
    bot.cursor.execute('SELECT * FROM user_prompts WHERE user_id = ?', (user_id,))
    result = bot.cursor.fetchone()
    if result:
        columns = [col[0] for col in bot.cursor.description]
        return dict(zip(columns, result))
    return "설정이 없습니다."

async def handle_function_call(function_name, args, message, bot):
    try:
        if function_name == "roll_dice":
            sides = int(args.get("sides", 6))  # 기본값 6면
            result = random.randint(1, sides)
            await message.channel.send(f"🎲 {sides}면 주사위를 굴려서 {result}이 나왔어!")

        elif function_name == "weather":
            location = args.get("location")
            if location:
                weather_data = await fetch_weather(location)
                await message.channel.send(weather_data)
            else:
                await message.channel.send("지역 정보를 제공하지 않았어.")

        elif function_name == "google_search":
            query = args.get("query")
            if query:
                search_results = await fetch_google_search(query)

                if isinstance(search_results, list):  # 반환값이 Embed 리스트인지 확인
                    for embed in search_results:  # Embed 하나씩 채널에 전송
                        await message.channel.send(embed=embed)
                else:
                    await message.channel.send("검색 결과를 표시하는 중 문제가 발생했습니다.")
            else:
                await message.channel.send("검색어를 입력하지 않았습니다.")

        elif function_name == "get_user_settings":
            user_id = args.get("user_id")
            if user_id:
                user_settings = get_user_settings(bot, user_id)
                await message.channel.send(f"사용자 설정: {user_settings}")
            else:
                await message.channel.send("사용자 ID가 없어.")

        else:
            await message.channel.send("알 수 없는 Function Call이야.")

    except Exception as e:
        print(f"Error in function handling: {e}")
        await message.channel.send("기능 처리 중 문제가 발생했어.")

# 이벤트 설정
def setup_events(bot):
    @bot.event
    async def on_ready():
        await bot.change_presence(status=discord.Status.online, activity=discord.Game("뭐? 심심해?"))
        print("Bot is ready")

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        if message.content.startswith("!"):
            await bot.process_commands(message)
            return

        user_id = message.author.id
        user_chat_history[user_id].append({"role": "user", "parts": [message.content]})

        # 사용자 프롬프트 가져오기
        bot.cursor.execute('SELECT system_prompt FROM user_prompts WHERE user_id = ?', (user_id,))
        result = bot.cursor.fetchone()
        system_prompt = result[0] if result else "기본 프롬프트입니다."

        # GenAI 모델 생성 (동적 시스템 프롬프트)
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config={
                "temperature": 0.5,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 300,
                "response_mime_type": "text/plain",
            },
            tools=[
                genai.protos.Tool(
                    function_declarations=get_function_definitions()
                )
            ],
            tool_config={"function_calling_config": "AUTO"},
            system_instruction=system_prompt  # 사용자별 시스템 프롬프트 설정
        )

        # GenAI 응답 생성
        try:
            chat_session = model.start_chat(history=list(user_chat_history[user_id]))
            response = chat_session.send_message(message.content)

            for part in response.parts:
                if hasattr(part, "function_call") and part.function_call:
                    function_call = part.function_call
                    args = {key: val for key, val in function_call.args.items()}  # args 파싱
                    await message.channel.send(
                        "```(..." + function_call.name + " tool 이걸 한번 써보자!!)\n" + json.dumps(args, ensure_ascii=False)+"```")
                    await handle_function_call(function_call.name, args, message, bot)
                    return  # Function 처리 후 종료
                elif hasattr(part, "text"):
                    # 일반 텍스트 응답
                    user_chat_history[user_id].append({"role": "model", "parts": [part.text]})
                    await message.channel.send(part.text)

        except Exception as e:
            print(f"Error: {e}")
            await message.channel.send("뭐야, 뭔가 꼬였네. 다시 말해봐.")

