# nonebot_plugin_guess_number
基于Nonebot2的猜数字小游戏插件

猜一个1到100的整数，猜错了会被禁言（需要管理员权限）

支持撤回消息防止刷屏（需要管理员权限，并依赖插件nonebot-plugin-follow-withdraw）

不确定是否有奇奇怪怪的bug  ~~(毕竟没特意学过python,还有的是chatgpt帮忙写的)~~

以后可能会加入的功能：胜场统计，计算胜率，排名

## 🔧 ️配置    .env.*

| 配置名            | 类型            | 默认值          | 说明                       |
| ----------------- | -------------- | --------------- | -------------------------- |
| game_start_time    | int           | 0               | 游戏开始时间（小时） |
| game_end_time      | int           | 0               | 游戏结束时间（小时） |
| interval_time      | int           | 10              | 单人游戏间隔时间（分钟） |
| min_ban_time       | int           | 1               | 最小禁言时间（分钟） |
| max_ban_time       | int           | 5               | 最大禁言时间（分钟） |
| number_range_min   | int           | 1               | 猜数字的范围（最小数） |
| number_range_max   | int           | 100             | 猜数字的范围（最大数） |
| try_times          | int           | 5               | 猜数字次数 |
| ban                | bool          | True            | 是否禁言 |
| withdraw           | bool          | True            | 是否撤回 |


