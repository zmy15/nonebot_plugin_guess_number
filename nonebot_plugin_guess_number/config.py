from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    game_start_time: int = 0
    game_end_time: int = 23
    interval_time: int = 10
    min_ban_time: int = 1
    max_ban_time: int = 5
    number_range_min: int = 1
    number_range_max: int = 100
    try_times: int = 5
    ban: bool = True
    withdraw: bool = True
