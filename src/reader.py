""" 
导入abc, 以定义抽象接口Reader
"""
from abc import abstractmethod, ABCMeta
from multiprocessing import Queue, Process, Value
import sys
import os
import queue
from click import open_file

class Reader(metaclass=ABCMeta):
    """
    Notes: Reader is abastract class. FileReader and BufferReader is the subclass.
    Attributes:
    """

    @abstractmethod
    def readline(self, size: int) -> str:
        """returns one line from the reader."""

    @abstractmethod
    def readable(self) -> bool:
        """returns true if the reader is readable"""


class FileReader(Reader):
    """实现一个读取文件 IO 的 Reader"""

    def __init__(self, filepath: str):
        self._filepath: str = filepath
        self._buffer: list = []
        self._position: int = 0
        self._eof = False

    def readline(self, size: int = 4096) -> str:
        line: str = ""
        if len(self._buffer) > 0:
            # 从头读取一行
            line = self._buffer.pop(0)
            assert len(line) <= size
            return line

        if self._eof is True:
            return ""

        with open_file(self._filepath, "r", encoding="utf-8", errors="ignore") as f:
            f.seek(self._position)
            for _ in range(10):
                content: str = f.readline(size)
                if len(content) == 0:
                    self._eof = True
                    break
                if not line:
                    line = content
                else:
                    self._buffer.append(content)
            self._position = f.tell()
        return line

    def readable(self) -> bool:
        """判断是否已无数据,注意必须是文件读完且缓存为空,才为True"""
        return self._eof is False or len(self._buffer) != 0


class StdinReader(Reader):
    """从标准输入获取Reader"""

    def __init__(self):
        self._raw_eof = Value("b", 0)
        self._queue = Queue()
        self._fd: int = sys.stdin.fileno()
        self._process = Process(target=self._fill_buffer, args=(self._fd, self._queue))
        self._process.start()

    def readline(self, size: int = 4096) -> str:
        line: str = ""
        try:
            line = self._queue.get(timeout=1)
        except (queue.Empty, ValueError) as error:
            if not self.readable:
                raise error
        return line

    def readable(self) -> bool:
        """判断是否已无数据,注意必须是文件读完且缓存为空,才为True"""
        return self._eof is False or not self._queue.empty()

    @property
    def _eof(self) -> bool:
        """self._process 还在运行，exitcode 为 None；exitcode为 int 类型的退出码，表示退出"""
        return self._process.exitcode is not None

    @staticmethod
    def _fill_buffer(fd: int, buffer: Queue):
        sys.stdin = os.fdopen(os.dup(fd), mode="r", encoding="utf-8", errors="ignore")
        for line in sys.stdin:
            if not line:  # 要么阻塞读数据，要么返回空数据，表示eof
                break
            buffer.put(line)
        sys.stdin.close()

    def __del__(self):
        if not sys.stdin.closed:
            sys.stdin.close()
        assert self._process.exitcode == 0
        self._process.close()


if __name__ == "__main__":
    reader = FileReader(filepath="./read.txt")
    reader.readline()
    reader.readline()
    lines = reader.readline()
    print(lines)
    print(len(lines))
