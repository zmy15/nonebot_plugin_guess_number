import random
from nonebot import on_command
from nonebot.exception import FinishedException
from nonebot.internal.params import ArgPlainText
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, bot, event, GroupMessageEvent, Message

guess = on_command("猜数字", aliases={'cai', '猜猜看', '猜', }, priority=99, block=True)
answer = random.randint(1, 100)


@guess.handle()
async def handle(bot: Bot, event: MessageEvent, state: T_State):
    await guess.send(f"猜一个1到100的整数，你有5次机会,猜错了会被禁言哦")


@guess.got("user_input1")
async def got(user_input1: str = ArgPlainText('user_input1')):
    guess_number = int(user_input1)
    try:
        if guess_number == answer:
            await guess.finish('恭喜你猜对了！答案就是{}。'.format(answer))
        elif guess_number < answer:
            await guess.send('猜小了，再试试大一点的数字。')
        else:
            await guess.send('猜大了，再试试小一点的数字。')
    except ValueError:
        await guess.send('请输入一个有效的整数。')


@guess.got("user_input2")
async def got(user_input2: str = ArgPlainText('user_input2')):
    guess_number = int(user_input2)
    try:
        if guess_number == answer:
            await guess.finish('恭喜你猜对了！答案就是{}。'.format(answer))
        elif guess_number < answer:
            await guess.send('猜小了，再试试大一点的数字。')
        else:
            await guess.send('猜大了，再试试小一点的数字。')
    except ValueError:
        await guess.send('请输入一个有效的整数。')


@guess.got("user_input3")
async def got(user_input3: str = ArgPlainText('user_input3')):
    guess_number = int(user_input3)
    try:
        if guess_number == answer:
            await guess.finish('恭喜你猜对了！答案就是{}。'.format(answer))
        elif guess_number < answer:
            await guess.send('猜小了，再试试大一点的数字。')
        else:
            await guess.send('猜大了，再试试小一点的数字。')
    except ValueError:
        await guess.send('请输入一个有效的整数。')


@guess.got("user_input4")
async def got(user_input4: str = ArgPlainText('user_input4')):
    guess_number = int(user_input4)
    try:
        if guess_number == answer:
            await guess.finish('恭喜你猜对了！答案就是{}。'.format(answer))
        elif guess_number < answer:
            await guess.send('猜小了，再试试大一点的数字。')
        else:
            await guess.send('猜大了，再试试小一点的数字。')
    except ValueError:
        await guess.send('请输入一个有效的整数。')


@guess.got("user_input5")
async def got(bot: Bot,event: GroupMessageEvent, user_input5: str = ArgPlainText('user_input5')):
    guess_number = int(user_input5)
    guess_count = 5
    user_id = event.get_user_id()
    max_ban_time = random.randint(1, 3)
    try:
        if guess_number == answer:
            await guess.finish('恭喜你猜对了！答案就是{}。'.format(answer))
    except ValueError:
        await guess.send('请输入一个有效的整数。')
    if guess_count == 5:
        await guess.send('你已经用尽了5次机会，游戏结束。答案是{}。'.format(answer))
        try:
            await bot.set_group_ban(group_id=event.group_id, user_id=user_id, duration=60 * max_ban_time)
        except FinishedException:
            pass
        msg = "恭喜您获得" + format_minutes(max_ban_time) + "的禁言"
        await guess.finish(Message(f'{msg}'))


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
