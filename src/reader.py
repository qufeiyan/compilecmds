""" 
导入abc, 以定义抽象接口Reader
"""
from abc import abstractmethod, ABCMeta
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
        '''判断是否已无数据,注意必须是文件读完且缓存为空,才为True'''
        return self._eof is False or len(self._buffer) != 0


class StdinReader(Reader):
    """从标准输入获取Reader"""

    def __init__(self):
        self._buffer = []
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

        with open_file("-", "r", encoding="utf-8", errors="ignore") as f:
            for _ in range(10):
                content: str = f.readline(size)
                if len(content) == 0:
                    self._eof = True
                    break
                if not line:
                    line = content
                else:
                    self._buffer.append(content)
        return line

    def readable(self) -> bool:
        '''判断是否已无数据,注意必须是文件读完且缓存为空,才为True'''
        return self._eof is False or len(self._buffer) != 0


if __name__ == "__main__":
    reader = FileReader(filepath="./read.txt")
    reader.readline()
    reader.readline()
    lines = reader.readline()
    print(lines)
    print(len(lines))
