
from unittest.mock import patch
from mirrcore.redis_check import is_redis_available, load_redis
from mirrmock.mock_redis import BusyRedis, ReadyRedis


def test_when_redis_loading_is_unavailable():
    database = BusyRedis()
    is_available = is_redis_available(database)
    assert is_available is False


def test_when_redis_done_loading_is_available():
    database = ReadyRedis()
    is_available = is_redis_available(database)
    assert is_available is True


@patch('mirrcore.redis_check.is_redis_available', return_value=False)
@patch('time.sleep', return_value=None)
def test_sleeps_when_redis_is_unavailable(patched_available, patched_sleep):
    def side_effect(_):
        patched_available.return_value = True
    patched_sleep.side_effect = side_effect

    load_redis()

    patched_sleep.assert_called_once()
