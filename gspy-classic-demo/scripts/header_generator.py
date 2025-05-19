import re


class CmdRange:
    def __init__(self, num=0):
        self.num = num
        self.cmds = []

    def add_cmd(self, cmd):
        self.cmds.append(cmd)

    def __str__(self):
        return "    (\n        %s\n    ) = range(%d, %d)" % (
            ",\n        ".join(self.cmds), self.num, len(self.cmds) + self.num)


class CmdEnum:
    def __init__(self, name, prefix=""):
        self.name = name
        self.prefix = prefix
        self.ranges = []

    def add_range(self, range):
        self.ranges.append(range)

    def __str__(self):
        return "class %s:\n%s" % (self.name, ''.join([str(r) for r in self.ranges]))


def header_generate(file):
    orig = ""
    with open(file, 'r') as f:
        orig = f.read()

    orig = orig.replace('\n', ' ')

    enums = []

    for m in re.finditer(r'typedef\s+enum\s*{(.*?)}\s*(\w+);', orig):
        e: str = m.group(2)
        if re.match(r'^te', e):
            e = e[2:]
        prefix = e
        if re.match(r'.*Cmds$', prefix):
            prefix = prefix[:-4]
        cmd_enum = CmdEnum(e, prefix)
        range = None
        for n in re.finditer(r'\s*(\w+)(\s*?=\s*([^\s,]+))?\s*(,|$)', m.group(1)):
            cmd = n.group(1)
            if re.match(r'^e', cmd):
                cmd = cmd[1:]
            if cmd.startswith(cmd_enum.prefix):
                cmd = cmd[len(cmd_enum.prefix):]
            if re.match(r'^CmdGrp', cmd):
                cmd = cmd[6:]
            if re.match(r'^_', cmd):
                cmd = cmd[1:]
            if n.group(2):
                num = int(n.group(3), 0)
                if range is not None:
                    cmd_enum.add_range(range)
                range = CmdRange(num)
            range.add_cmd(cmd)
        if range is not None:
            cmd_enum.add_range(range)
        enums.append(cmd_enum)

    return "\n\n".join([str(e) for e in enums])


if __name__ == "__main__":
    import os

    print(header_generate("/home/ida/janussvn/Programs/TC/juice_tc_cmd.h"))
