"""Request limits enforced in code (Ingestion IG-07, decision C-45).

A caller asks for a slot with `acquire()` and waits when the window is full. Waiting is not a
failure. The in-memory limiter serves one process. The Redis limiter is shared by every worker
process, so two workers together stay under the source's limit.
"""

import time
import uuid
from collections import deque
from collections.abc import Callable

import redis

Clock = Callable[[], float]
Sleep = Callable[[float], None]

# Atomic sliding window: returns 0 when a slot was taken, else the seconds to wait.
_LUA = """
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
redis.call('ZREMRANGEBYSCORE', KEYS[1], 0, now - window)
if redis.call('ZCARD', KEYS[1]) < limit then
  redis.call('ZADD', KEYS[1], now, ARGV[4])
  redis.call('PEXPIRE', KEYS[1], math.ceil(window * 1000) + 1000)
  return '0'
end
local oldest = redis.call('ZRANGE', KEYS[1], 0, 0, 'WITHSCORES')
return tostring(tonumber(oldest[2]) + window - now)
"""


class SlidingWindowLimiter:
    """At most `max_calls` in any window of `period` seconds, within one process."""

    def __init__(
        self,
        max_calls: int,
        period: float = 1.0,
        clock: Clock = time.monotonic,
        sleep: Sleep = time.sleep,
    ) -> None:
        self.max_calls, self.period, self._clock, self._sleep = max_calls, period, clock, sleep
        self._stamps: deque[float] = deque()

    def acquire(self) -> None:
        while True:
            now = self._clock()
            while self._stamps and now - self._stamps[0] >= self.period:
                self._stamps.popleft()
            if len(self._stamps) < self.max_calls:
                self._stamps.append(now)
                return
            self._sleep(max(self._stamps[0] + self.period - now, 0.001))


class RedisSlidingWindowLimiter:
    """The same limit, shared by every process that uses the same key."""

    def __init__(
        self,
        client: "redis.Redis",
        key: str,
        max_calls: int,
        period: float = 1.0,
        clock: Clock = time.time,
        sleep: Sleep = time.sleep,
    ) -> None:
        self._redis, self._key = client, key
        self.max_calls, self.period, self._clock, self._sleep = max_calls, period, clock, sleep
        self._script = client.register_script(_LUA)

    def acquire(self) -> None:
        while True:
            wait = float(
                self._script(
                    keys=[self._key],
                    args=[self._clock(), self.period, self.max_calls, uuid.uuid4().hex],
                )
            )
            if wait <= 0:
                return
            self._sleep(max(wait, 0.001))
