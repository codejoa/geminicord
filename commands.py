from discord.ext import commands

def setup_commands(bot):
    @bot.command(name='저장')
    async def save_prompt(ctx, *, prompt: str):
        user_id = ctx.author.id
        bot.cursor.execute('REPLACE INTO user_prompts (user_id, system_prompt) VALUES (?, ?)', (user_id, prompt))
        bot.conn.commit()
        await ctx.send('시스템 프롬프트가 저장되었습니다.')

    @bot.command(name='로드')
    async def load_prompt(ctx):
        user_id = ctx.author.id
        bot.cursor.execute('SELECT system_prompt FROM user_prompts WHERE user_id = ?', (user_id,))
        result = bot.cursor.fetchone()
        if result:
            prompt = result[0]
            await ctx.send(f'유저(`{user_id}`)가 등록한 시스템 프롬프트\n```{prompt}```')
        else:
            await ctx.send('저장된 시스템 프롬프트가 없습니다.')

    @bot.command()
    async def hello(ctx):
        await ctx.send("응 나 살아있어.")