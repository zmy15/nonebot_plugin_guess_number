import asyncio
import random
import os
import json
from datetime import datetime, timedelta

import nonebot
from nonebot import on_command
from nonebot.exception import FinishedException
from nonebot.internal.params import ArgPlainText
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message
from .config import Config

global_config = nonebot.get_driver().config
guess_number_config = Config.parse_obj(global_config.dict())
game_start_time = guess_number_config.game_start_time
game_end_time = guess_number_config.game_end_time
interval_time = guess_number_config.interval_time
min_ban_time = guess_number_config.min_ban_time
max_ban_time = guess_number_config.max_ban_time
number_range_min = guess_number_config.number_range_min
number_range_max = guess_number_config.number_range_max
try_times = guess_number_config.try_times
ban = guess_number_config.ban
withdraw = guess_number_config.withdraw


player_last_game_time = {}
player = []
user_game_data = {}
data_folder = "data"
data_file_name = "user_game_data.json"

if not os.path.exists(data_folder):
    os.makedirs(data_folder)

data_file_path = os.path.join(data_folder, data_file_name)

if os.path.exists(data_file_path):
    with open(data_file_path, "r") as file:
        user_game_data = json.load(file)


guess = on_command("猜数字", aliases={'cai', '猜猜看'}, priority=99, block=True)
game_stats = on_command("游戏统计", aliases={"胜率", "统计", "游戏胜率"}, priority=99, block=True)
ranking = on_command("排名", aliases={"游戏排名", "胜率排名", "胜场排名"}, priority=99, block=True)


@guess.handle()
async def handle(bot: Bot, event: MessageEvent, state: T_State):
    global answer, user_id, user_nickname
    user_id = event.get_user_id()
    user_nickname = event.sender.nickname
    now = datetime.now()
    hour = now.hour
    if game_start_time <= hour <= game_end_time:
        if len(player) != 0:
            await guess.finish(f"有人正在进行游戏，你现在不能进行游戏", at_sender=True)
        elif user_id in player_last_game_time and now - player_last_game_time[user_id] < timedelta(
                minutes=interval_time):
            remaining_time = (player_last_game_time[user_id] + timedelta(minutes=interval_time)) - now
            await guess.finish(f"游戏休息中，请在{remaining_time.total_seconds():.0f}秒后再进行游戏。",
                               at_sender=True)
        else:
            try:
                msg = "猜一个" + str(number_range_min) + "到" + str(number_range_max) + "的整数，你有" + str(
                    try_times) + "机会"
                await guess.send(Message(f'{msg}'), at_sender=True)
                player.append(user_id)
                answer = random.randint(number_range_min, number_range_max)
            except FinishedException:
                pass
        state["user_id"] = []
        if len(state["user_id"]) != 1:
            state["user_id"].append(user_id)
        state['times'] = 1
        state['bot_messages'] = []
    else:
        msg = "现在不是游戏时间，请在" + str(game_start_time) + "点到" + str(game_end_time) + "进行游戏"
        await guess.finish(Message(f'{msg}'), at_sender=True)


@guess.got("user_input")
async def got(bot: Bot, event: MessageEvent, user_input: str = ArgPlainText('user_input'), state=T_State):
    if user_input.isdigit() and 1 <= int(user_input) <= 100:
        guess_number = int(user_input)
    elif user_input in ["猜数字", "cai", "猜猜看"]:
        await guess.reject(f"你已经在游戏中，请勿重复进行游戏", at_sender=True)
    elif user_input in ["取消", "退出", "结束", "不玩了", "exit"]:
        if ban:
            set_group_ban(bot, event.group_id, state["user_id"][0])
        if user_id in user_game_data:
            user_game_data[user_id]["games_played"] += 1
            user_game_data[user_id]["nickname"] = user_nickname
        else:
            user_game_data[user_id] = {"games_played": 1, "games_won": 0, "nickname": user_nickname}
        with open(data_file_path, "w") as file:
            json.dump(user_game_data, file)
        await guess.send("游戏退出", at_sender=True)
        del player[0]
        player_last_game_time[user_id] = datetime.now()
        await delete_messages(bot, state['bot_messages'])
    else:
        guess_number = None
        await guess.reject(None)
    if guess_number != answer:
        if state['times'] == try_times:
            if user_id in user_game_data:
                user_game_data[user_id]["games_played"] += 1
                user_game_data[user_id]["nickname"] = user_nickname
            else:
                user_game_data[user_id] = {"games_played": 1, "games_won": 0, "nickname": user_nickname}
            with open(data_file_path, "w") as file:
                json.dump(user_game_data, file)
            msg = "你已用尽了" + str(try_times) + "次机会，游戏结束，答案是" + str(answer)
            await guess.send(Message(f'{msg}'), at_sender=True)
            if ban:
                set_group_ban(bot, event.group_id, state["user_id"][0])
            player_last_game_time[user_id] = datetime.now()
            del player[0]
            await delete_messages(bot, state['bot_messages'])
        else:
            state['times'] = state['times'] + 1
    try:
        if guess_number == answer:
            if user_id in user_game_data:
                user_game_data[user_id]["games_played"] += 1
                user_game_data[user_id]["games_won"] += 1
                user_game_data[user_id]["nickname"] = user_nickname
            else:
                user_game_data[user_id] = {"games_played": 1, "games_won": 1, "nickname": user_nickname}
            with open(data_file_path, "w") as file:
                json.dump(user_game_data, file)
            await guess.send('恭喜你猜对了！答案就是{}。'.format(answer), at_sender=True)
            player_last_game_time[user_id] = datetime.now()
            del player[0]
            await delete_messages(bot, state['bot_messages'])
        elif guess_number < answer:
            msg = "猜小了，你还有" + str((try_times + 1) - state['times']) + "次机会"
            await guess.send(Message(f'{msg}'), at_sender=True)
            message_id = event.message_id
            state['bot_messages'].append(message_id)
            await guess.reject(None)
        else:
            msg = "猜大了，你还有" + str((try_times + 1) - state['times']) + "次机会"
            await guess.send(Message(f'{msg}'), at_sender=True)
            message_id = event.message_id
            state['bot_messages'].append(message_id)
            await guess.reject(None)
    except ValueError:
        await guess.reject('请输入一个有效的整数。', at_sender=True)


async def set_group_ban(bot: Bot, group_id: int, user_id: int):
    ban_time = random.randint(min_ban_time, max_ban_time)
    try:
        bot.set_group_ban(group_id=group_id, user_id=user_id, duration=60 * ban_time)
        msg = "恭喜您获得" + format_minutes(max_ban_time) + "的禁言服务"
        await guess.send(Message(f'{msg}'), reply_message=True)
    except FinishedException:
        pass
    except Exception as e:
        print(e)
        msg = "禁言失败~机器人权限不足（请确认bot是否是管理员/禁言到群管）"
        await guess.send(Message(f'{msg}'), at_sender=True)


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
    if withdraw:
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
    else:
        await guess.finish(None)


@game_stats.handle()
async def handle(event: MessageEvent, bot: Bot):
    user_id = event.user_id
    with open(data_file_path, "r") as file:
        user_game_data = json.load(file)

    if user_id in user_game_data:
        games_played = user_game_data[user_id]["games_played"]
        games_won = user_game_data[user_id]["games_won"]
        user_nickname = user_game_data[user_id]["nickname"]

        if games_played > 0:
            win_rate = (games_won / games_played) * 100  # 计算胜率
        else:
            win_rate = 0

        await game_stats.finish(
            f"{user_nickname} 的游戏统计数据：\n已玩游戏场数: {games_played}\n获胜场数: {games_won}\n"
            f",胜率：{win_rate:.2f}%", at_sender=True)
    else:
        await game_stats.finish("您还没有玩过游戏。", at_sender=True)


@ranking.handle()
async def handle(bot: Bot):
    if not user_game_data:
        await game_stats.finish("尚无用户游戏数据。")

        # 计算每个用户的胜率
    user_win_rates = {}
    for user_id, data in user_game_data.items():
        games_played = data.get("games_played", 0)
        games_won = data.get("games_won", 0)
        if games_played > 0:
            win_rate = (games_won / games_played) * 100
        else:
            win_rate = 0
        user_win_rates[user_id] = {"nickname": data["nickname"], "win_rate": win_rate}

    # 对用户胜率进行排序
    ranked_users = sorted(user_win_rates.items(), key=lambda x: x[1]["win_rate"], reverse=True)

    # 显示排名
    rank_msg = "胜率排名：\n"
    for rank, (user_id, data) in enumerate(ranked_users, start=1):
        user_nickname = data["nickname"]
        win_rate = data["win_rate"]
        rank_msg += f"{rank}. {user_nickname} - 胜率: {win_rate:.2f}%\n"

    await game_stats.finish(rank_msg)
