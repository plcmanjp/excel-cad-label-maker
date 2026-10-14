"""Cancellable jobs and a serialized final file-replacement boundary."""
from dataclasses import dataclass
from queue import Queue
from threading import Event, Lock, Thread


class Cancelled(Exception):
    pass


class Cancellation:
    def __init__(self):
        self._event = Event()
        self._lock = Lock()
        self.committed = False

    def cancel(self):
        with self._lock:
            if self.committed:
                return False
            self._event.set()
            return True

    def check(self):
        if self._event.is_set():
            raise Cancelled("작업이 취소되었습니다.")

    def commit(self, action):
        with self._lock:
            self.check()
            action()
            self.committed = True


@dataclass(frozen=True)
class JobResult:
    generation: int
    kind: str
    status: str
    value: object


class Jobs:
    """Workers use values and queues only. The owner polls from its Tk loop."""
    def __init__(self):
        self.queue = Queue()
        self.generation = 0
        self.token = None
        self.closed = False

    def start(self, kind, action):
        if self.closed:
            raise RuntimeError("종료한 작업 관리자입니다.")
        if self.token:
            self.token.cancel()
        self.generation += 1
        generation = self.generation
        self.token = token = Cancellation()

        def report(message):
            token.check()
            self.queue.put(JobResult(generation, kind, "progress", message))

        def work():
            try:
                token.check()
                result = action(token, report)
                if not token.committed:
                    token.check()
                self.queue.put(JobResult(generation, kind, "done", result))
            except Cancelled as error:
                self.queue.put(JobResult(generation, kind, "cancelled", error))
            except Exception as error:
                self.queue.put(JobResult(generation, kind, "error", error))

        Thread(target=work, daemon=True).start()
        return generation

    def invalidate(self):
        if self.token:
            self.token.cancel()
        self.generation += 1

    def close(self):
        self.closed = True
        self.invalidate()
