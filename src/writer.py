"""使用 orjoson 生成json数据"""
from os import path, remove
import orjson
from src.parser import Parser


class Writer:
    """定义 Writer 根据parser 得到的数据 生成compile_commands.json"""

    def __init__(self, directory: str = None):
        self.__buffer: list = []
        self.__dir: str = directory
        self.__start: bool = False #写开始标志
        self.__file: str = ""

        default: str = "compile_commands.json"
        if self.__dir is not None and path.isdir(self.__dir):
            self.__file: str = (
                (self.__dir[:-1] if "/" in self.__dir else self.__dir) + "/" + default
            )
        else:
            self.__file: str = default

        if path.isfile(self.__file):
            remove(self.__file)

    def write(self, item: list):
        """获取一次有效数据, 将之写入__buffer 或者文件"""
        if len(self.__buffer) >= 1:
            with open(self.__file, "a+", encoding="utf-8") as f:
                f.write("[\n" if False is self.__start else ",\n")
                f.write(
                    orjson.dumps(self.__buffer, option=orjson.OPT_INDENT_2).decode(
                        "utf-8"
                    )[2:-2]
                )
                self.__start = True
                self.__buffer.clear()
        self.__buffer.extend(item)

    def flush(self):
        """写入 buffer 到文件"""
        with open(self.__file, "a+", encoding="utf-8") as f:
            f.write("[\n" if False is self.__start else ",\n")
            f.write(
                orjson.dumps(self.__buffer, option=orjson.OPT_INDENT_2).decode("utf-8")[2:] or "\n]"
            )
            self.__buffer.clear()
            f.flush()


if __name__ == "__main__":
    from src.reader import FileReader

    _reader = FileReader("read.txt")
    _parser = Parser(reader=_reader)

    _res: list = _parser.parseline()
    print(_res)
    _res: list = _parser.parseline()

    _writer = Writer()
    _writer.write(_res)
    _writer.flush()
