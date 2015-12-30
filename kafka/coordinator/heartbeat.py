import time

import kafka.common as Errors


class Heartbeat(object):
    _heartbeat_interval_ms = 3000
    _session_timeout_ms = 30000

    def __init__(self, **kwargs):
        for config in ('heartbeat_interval_ms', 'session_timeout_ms'):
            if config in kwargs:
                setattr(self, '_' + config, kwargs.pop(config))

        if self._heartbeat_interval_ms > self._session_timeout_ms:
            raise Errors.IllegalArgumentError("Heartbeat interval must be set"
                                              " lower than the session timeout")

        self.interval = self._heartbeat_interval_ms / 1000.0
        self.timeout = self._session_timeout_ms / 1000.0
        self.last_send = 0
        self.last_receive = 0
        self.last_reset = time.time()

    def sent_heartbeat(self):
        self.last_send = time.time()

    def received_heartbeat(self):
        self.last_receive = time.time()

    def ttl(self):
        last_beat = max(self.last_send, self.last_reset)
        return max(0, last_beat + self.interval - time.time())

    def should_heartbeat(self):
        return self.ttl() == 0

    def session_expired(self):
        last_recv = max(self.last_receive, self.last_reset)
        return (time.time() - last_recv) > self.timeout

    def reset_session_timeout(self):
        self.last_reset = time.time()