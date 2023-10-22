import asyncio
import random
from nonebot import on_command
from nonebot.exception import FinishedException
from nonebot.internal.params import ArgPlainText
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message
from nonebot import require

require("nonebot-plugin-follow-withdraw")

guess = on_command("猜数字", aliases={'cai', '猜猜看', '猜', }, priority=99, block=True)


@guess.handle()
async def handle(bot: Bot, event: MessageEvent, state: T_State):
    global answer
    try:
        await guess.send(f"猜一个1到100的整数，你有5次机会,猜错了会被禁言哦")
        answer = random.randint(1, 100)
    except FinishedException:
        pass
    state['times'] = 1
    state['bot_messages'] = []


@guess.got("user_input")
async def got(bot: Bot, event: MessageEvent, user_input: str = ArgPlainText('user_input'), state=T_State):
    if user_input.isdigit() and 1 <= int(user_input) <= 100:
        guess_number = int(user_input)
    elif user_input in ["取消", "退出", "结束", "不玩了", "exit"]:
        await guess.finish("游戏退出")
    else:
        guess_number = None
        await guess.reject(None)
    user_id = event.get_user_id()
    max_ban_time = random.randint(1, 5)
    if guess_number != answer:
        if state['times'] == 5:
            await delete_messages(bot, state['bot_messages'])
            await guess.send('你已经用尽了5次机会，游戏结束。答案是{}。'.format(answer))
            await bot.set_group_ban(group_id=event.group_id, user_id=user_id, duration=60 * max_ban_time)
            msg = "恭喜您获得" + format_minutes(max_ban_time) + "的禁言"
            await guess.finish(Message(f'{msg}'))
        else:
            state['times'] = state['times'] + 1
    try:
        if guess_number == answer:
            await delete_messages(bot, state['bot_messages'])
            await guess.finish('恭喜你猜对了！答案就是{}。'.format(answer))
        elif guess_number < answer:
            await guess.send('猜小了，再试试大一点的数字。')
            message_id = event.message_id
            state['bot_messages'].append(message_id)
            await guess.reject(None)
        else:
            await guess.send('猜大了，再试试小一点的数字。')
            message_id = event.message_id
            state['bot_messages'].append(message_id)
            await guess.reject(None)
    except ValueError:
        await guess.reject('请输入一个有效的整数。')


def format_minutes(minutes):
    days = minutes // (60 * 24)
    hours = (minutes % (60 * 24)) // 60
    remaining_minutes = minutes % 60

    result = ""
    if days > 0:
        result += str(days) + "天"
    if hours > 0:
        result += str(hours) + "小时"
    if remaining_minutes > 0:
        result += str(remaining_minutes) + "分钟"

    return result


# 撤回消息的函数
async def delete_messages(bot: Bot, message_ids: list):
    for message_id in message_ids:
        try:
            await bot.delete_msg(message_id=message_id)
            await asyncio.sleep(random.randint(1, 3))
        except Exception as e:
            pass
