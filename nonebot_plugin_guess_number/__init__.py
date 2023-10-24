import asyncio
import random
from datetime import datetime, timedelta
from nonebot import on_command
from nonebot.exception import FinishedException
from nonebot.internal.params import ArgPlainText
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message

guess = on_command("猜数字", aliases={'cai', '猜猜看'}, priority=99, block=True)
player_last_game_time = {}


@guess.handle()
async def handle(bot: Bot, event: MessageEvent, state: T_State):
    global answer, user_id
    user_id = event.get_user_id()
    now = datetime.now()
    hour = now.hour
    if 7 <= hour <= 22:
        await guess.finish(f"现在不是游戏时间,请在22点至次日7点进行游戏", at_sender=True)
    else:
        if state['player'] == 1:
            await guess.finish(f"有人正在进行游戏，你现在不能进行游戏", at_sender=True)
        elif user_id in player_last_game_time and now - player_last_game_time[user_id] < timedelta(minutes=10):
            remaining_time = (player_last_game_time[user_id] + timedelta(minutes=10)) - now
            await guess.finish(f"游戏休息中，请在{remaining_time.total_seconds():.0f}秒后再进行游戏。",
                               at_sender=True)
        else:
            del player_last_game_time[user_id]
            try:
                await guess.send(
                    f"猜一个1到100的整数，你有5次机会,猜错了会被禁言哦.输入 退出 来退出游戏，但会被禁言",
                    at_sender=True)
                answer = random.randint(1, 100)
                state['player'] = 1
            except FinishedException:
                pass
        state['times'] = 1
        state['bot_messages'] = []


@guess.got("user_input")
async def got(bot: Bot, event: MessageEvent, user_input: str = ArgPlainText('user_input'), state=T_State):
    global max_ban_time
    if user_input.isdigit() and 1 <= int(user_input) <= 100:
        guess_number = int(user_input)
    elif user_input in ["猜数字", "cai", "猜猜看"]:
        await guess.reject(f"你已经在游戏中，请勿重复进行游戏", at_sender=True)
    elif user_input in ["取消", "退出", "结束", "不玩了", "exit"]:
        try:
            await bot.set_group_ban(group_id=event.group_id, user_id=user_id, duration=60 * max_ban_time)
        except FinishedException:
            pass
        except Exception as e:
            print(e)
            msg = "禁言失败~机器人权限不足（请确认bot是否是管理员/禁言到群管）"
            await guess.send(Message(f'{msg}'), at_sender=True)
        await guess.send("游戏退出", at_sender=True)
        state['player'] = 0
        player_last_game_time[user_id] = datetime.now()
        await delete_messages(bot, state['bot_messages'])
    else:
        guess_number = None
        await guess.reject(None)
    if guess_number != answer:
        if state['times'] == 5:
            await guess.send('你已经用尽了5次机会，游戏结束。答案是{}。'.format(answer), at_sender=True)
            try:
                await bot.set_group_ban(group_id=event.group_id, user_id=user_id, duration=60 * max_ban_time)
                msg = "恭喜您获得" + format_minutes(max_ban_time) + "的禁言"
                await guess.send(Message(f'{msg}'))
            except FinishedException:
                pass
            except Exception as e:
                print(e)
                msg = "禁言失败~机器人权限不足（请确认bot是否是管理员/禁言到群管）"
                await guess.send(Message(f'{msg}'), at_sender=True)
            state['player'] = 0
            player_last_game_time[user_id] = datetime.now()
            await delete_messages(bot, state['bot_messages'])
        else:
            state['times'] = state['times'] + 1
    max_ban_time = random.randint(1, 5)
    try:
        if guess_number == answer:
            await guess.send('恭喜你猜对了！答案就是{}。'.format(answer), at_sender=True)
            state['player'] = 0
            player_last_game_time[user_id] = datetime.now()
            await delete_messages(bot, state['bot_messages'])
        elif guess_number < answer:
            await guess.send('猜小了，再试试大一点的数字。', at_sender=True)
            message_id = event.message_id
            state['bot_messages'].append(message_id)
            await guess.reject(None)
        else:
            await guess.send('猜大了，再试试小一点的数字。', at_sender=True)
            message_id = event.message_id
            state['bot_messages'].append(message_id)
            await guess.reject(None)
    except ValueError:
        await guess.reject('请输入一个有效的整数。', at_sender=True)


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
        except FinishedException:
            pass
        except Exception as e:
            print(e)
            msg = "撤回失败~机器人权限不足（请确认bot是否是管理员/撤回到群管的消息）"
            await guess.finish(Message(f'{msg}'), at_sender=True)
    await guess.finish(None)
