""" 
1. 导入pickle 以提升深拷贝效率
2. 导入popen 以获取编译路径
3. 导入Reader接口, Parser 只依赖抽象Reader 
"""
import pickle
from typing import Optional
from os import path

# import copy
from os import popen
from src.reader import Reader


class ParseException(Exception):
    """定义解析异常"""

    def __init__(self, msg: str):
        Exception.__init__(self)
        self.message = msg

    def __str__(self):
        return f"Error: {{{self.message}}}"


class Parser:
    """
    从reader读取数据, 并将之解析为字典类型的数据
    """

    def __init__(self, reader: Reader, build_dir: Optional[str] = None):
        """Notes that build_dir must be absolute path."""
        self.reader = reader
        self._format = {"directory": "", "arguments": [], "file": ""}
        self._build_dir = build_dir
        if self._build_dir != "":  # and path.isdir(self._build_dir):
            self._dir: str = self._build_dir
        else:
            self._dir = self._build_dir = path.abspath(".")

        print(f"self._dir: {self._dir} \nself._build_dir: {self._build_dir} ")

    def __iter__(self):
        return self

    def __next__(self) -> list:
        if self.parseable:
            return self.parseline()
        else:
            raise StopIteration

    def parsedirectory(self, line: str) -> Optional[str]:
        """解析一行字符串，如果符合要求，即该串为make进入子目录构建的字符串，则返回构建目录"""
        res: Optional = None
        if len(line) != 0:
            if ("make[1]" in line and "Entering directory" in line) or ("+ cd" in line):
                res = self._dir = self.__directory(line)
            elif "make[1]" in line and "Leaving directory" in line:
                res = self.__directory(line)
                assert res == self._dir
                self._dir = ""
        return res

    def parsecommand(self, line: str) -> list:
        """解析一行字符串，如果符合要求，即该串为编译命令字符串，则返回子项为字典的列表项"""
        cc: str = ""
        files: list = []
        res: list = []
        if len(line) == 0:
            return res

        raw_lines: list = line.split()
        if self.__valid(raw_lines) is False:
            return []

        # 搜索编译工具链及编译文件, 以及处理文件路径
        index: int = 0
        target: list = ["-I", "-D"]
        lines: list = []
        while index < len(raw_lines):
            if (
                raw_lines[index].endswith("gcc")
                or raw_lines[index].endswith("g++")
                or raw_lines[index].endswith("clang")
                or raw_lines[index].endswith("clang++")
            ):
                cc = raw_lines[index]
                index += 1
            elif raw_lines[index] in target:
                combine: str = (
                    "".join((raw_lines[index], raw_lines[index + 1]))
                    if raw_lines[index] == "-D"
                    else "".join(
                        (
                            raw_lines[index],
                            self.__normpath(
                                self.__relpath(self.__abspath(raw_lines[index + 1]))
                            ),
                        )
                    )
                )
                lines.append(combine)
                index += 2
            elif raw_lines[index].startswith("-I"):
                inc_str: str = "".join(
                    (
                        "-I",
                        self.__normpath(
                            self.__relpath(self.__abspath(raw_lines[index][2:]))
                        ),
                    )
                )
                lines.append(inc_str)
                index += 1
            elif (
                raw_lines[index].endswith(".o")
                or raw_lines[index].endswith(".c")
                or raw_lines[index].endswith(".cc")
                or raw_lines[index].endswith(".cpp")
                or raw_lines[index].endswith(".cxx")
            ):
                filestr: str = self.__normpath(
                    self.__relpath(self.__abspath(raw_lines[index]))
                )
                lines.append(filestr)
                if raw_lines[index].endswith(".o") is False:
                    files.append(filestr)
                index += 1
            else:
                lines.append(raw_lines[index])
                index += 1

        file_num = len(files)
        if cc == "" or file_num == 0:
            return []

        with popen("which " + cc, "r") as pip:
            cc_path = self.__trim(pip.readline())

        if not cc_path:
            self._format.get("arguments").append(cc)
        else:
            self._format.get("arguments").append(cc_path)

        for argument in lines[1:]:
            if (
                not argument.endswith(".c")
                and not argument.endswith(".cc")
                and not argument.endswith(".cpp")
                and not argument.endswith(".cxx")
            ):
                self._format.get("arguments").append(argument)

        for i in range(file_num):
            # item = copy.deepcopy(self._format)
            item = pickle.loads(pickle.dumps(self._format, -1))
            item.get("arguments").append(files[i])

            if self._build_dir != "":
                directory = self._build_dir
            else:
                with popen("pwd", "r") as pip:
                    directory = self.__trim(pip.readline())

            item.update({"directory": directory})
            if "/" == files[i][0]:
                item["file"] = self.__normpath(self.__trim(files[i]))
            else:
                item["file"] = self.__normpath(directory + "/" + self.__trim(files[i]))
            res.append(item)
        self.__reset()
        return res

    def __trim(self, src: str) -> str:
        """去掉换行符与当前目录符 "./" """
        if "\n" in src:
            src = src[:-1]
        if "./" in src:
            src = src[2:]

        return src

    def parseline(self) -> list:
        """解析一行字符串，先解析目录，如果解析到目录，返回。如果没解析到目录, 尝试解析命令"""
        line: str = self.reader.readline()
        if not self.parsedirectory(line):
            return self.parsecommand(line)
        else:
            return []

    @property
    def parseable(self) -> bool:
        """是否有数据可解析"""
        return self.reader.readable()

    def __reset(self):
        """解析完一次命令后，重置解析字典为初始状态"""
        self._format.update({"directory": ""})
        self._format.get("arguments").clear()
        self._format.update({"file": ""})

    def __directory(self, line: str) -> str:
        """从字符串中解析处目录项"""
        lines = line.split()
        res: str = ""
        res_list = [s for s in lines if "'/" in s or '"/' in s or s.startswith("/")]
        if len(res_list) == 1:
            raw_res = res_list.pop()
            res = raw_res if raw_res.startswith("/") else raw_res[1:-1]
        else:
            raise ParseException("only one directory string is expected.")
        return self.__normpath(res)

    def __normpath(self, filepath: str) -> str:
        return path.normpath(filepath)

    def __relpath(self, filepath: str) -> str:
        """filepath 为全路径，获取基于 self._build_dir 的相对路径"""
        if self._build_dir != "":
            return path.relpath(filepath, self._build_dir)
        raise ParseException(f"can not parse relative path for {self._build_dir}")

    def __abspath(self, filepath: str) -> str:
        """假定 filepath 为相对于 self._dir 的相对路径，则基于此构造filepath的绝对路径."""
        if filepath.startswith("/") is True:
            return filepath
        elif self._dir != "":
            return self.__normpath(self._dir + "/" + filepath)
        raise ParseException(
            f"can not parse absolute path for {filepath} based on {self._dir or None}"
        )

    def __valid(self, raws: str) -> bool:
        valid: bool = False
        for s in raws:
            if (
                s.endswith("gcc")
                or s.endswith("g++")
                or s.endswith("clang")
                or s.endswith("clang++")
            ):
                valid = True
                break
        return valid


if __name__ == "__main__":
    import orjson
    from src.reader import FileReader

    _reader = FileReader("reads.txt")
    _parser = Parser(reader=_reader, build_dir="~/coder")

    for pi in _parser:
        if len(pi) > 0:
            print(pi)
    # _res: list = _parser.parseline()
    # print(_res)
    # _res: list = _parser.parseline()

    # with open("cmd.json", "w", encoding="utf-8") as f:
    #     f.write(orjson.dumps(_res, option=orjson.OPT_INDENT_2).decode("utf-8"))
