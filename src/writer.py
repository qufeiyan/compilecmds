"""使用 orjoson 生成json数据"""
from os import path, remove
import orjson
from .parser import Parser

class Writer:
    """定义 Writer 根据parser 得到的数据 生成compile_commands.json"""

    def __init__(self, directory: str = None):
        self.buffer = []
        self.dir = directory

        default: str = "compile_commands.json"
        if self.dir is not None and path.isdir(self.dir):
            self.file: str = self.dir.removesuffix("/") + "/" + default
        else:
            self.file: str = default
        
        if path.isfile(self.file):
            remove(self.file)

    def write(self, item: list):
        """获取一次有效数据, 将之写入buffer 或者文件"""
        if len(self.buffer) >= 10:
            with open(self.file, "a+", encoding="utf-8") as f:
                f.write(orjson.dumps(self.buffer, option=orjson.OPT_INDENT_2).decode("utf-8"))
                self.buffer.clear()
        self.buffer.extend(item)

    def flush(self):
        """写入buffer 到文件"""
        if len(self.buffer) == 0:
            return

        with open(self.file, "a+", encoding="utf-8") as f:
            f.write(orjson.dumps(self.buffer, option=orjson.OPT_INDENT_2).decode("utf-8"))
            self.buffer.clear()
            f.flush()


if __name__ == "__main__":
    from .reader import FileReader
    _reader = FileReader("read.txt")
    _parser = Parser(reader=_reader)

    _res: list = _parser.parseline()
    print(_res)
    _res: list = _parser.parseline()
   
    _writer = Writer() 
    _writer.write(_res)
    _writer.flush()
