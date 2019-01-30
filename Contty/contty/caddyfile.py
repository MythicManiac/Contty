import sys
import json


CONTTY_PREFIX = "# CONTTY"
START_BLOCK_KEYWORD = "STARTBLOCK"
END_BLOCK_KEYWORD = "ENDBLOCK"

MANUAL_BLOCK_MODE = "MANUAL"
AUTOMATIC_BLOCK_MODE = "AUTOMATIC"

"""
Files may have automatic, commented, or manual configurations
mixed together. For example, the following would be considered
a valid configuration:

https://example.com {
    header -Server
    proxy / example:6000 {
        websocket
        transparent
    }
    tls example@example.com
}

# CONTTY STARTBLOCK MANUAL
https://example.com {
    header -Server
    proxy / example:6000 {
        websocket
        transparent
    }
    tls example@example.com
}
# CONTTY ENDBLOCK

# CONTTY STARTBLOCK AUTOMATIC {"hostname": "example.com", "service": "example", "port":800, "email": "example@example.org"}
https://example.com {
    header -Server
    proxy / example:800 {
        websocket
        transparent
    }
    tls example@example.com
}
# CONTTY ENDBLOCK
"""


class Caddyfile(object):

    def __init__(self):
        self.unmanaged_config = []
        self.automatic_blocks = []
        self.manual_blocks = []

    def parse_from_file(self, filepath):
        path = sys.path.abspath(filepath)
        with open(path, "r+") as f:
            lines = f.readlines()
        self.parse(lines)

    def add_automatic_block_config(self, config):
        self.automatic_blocks.append(config)

    def parse_automatic_block_config(self, config_string):
        config = json.loads(config_string)
        self.automatic_blocks.append(config)

    def add_manual_block(self, block_content):
        self.manual_blocks.append(block_content)

    def join_strings(self, *args):
        return " ".join(args)

    def parse_contty_block(self, line, index, lines):
        line = line.replace(CONTTY_PREFIX, "").strip()
        if not line.startswith(START_BLOCK_KEYWORD):
            raise AttributeError("Invalid line provided")

        line = line.replace(START_BLOCK_KEYWORD, "").strip()
        mode = line.split(" ")[0]
        lines_read = 1

        if mode == AUTOMATIC_BLOCK_MODE:
            config = line.replace(AUTOMATIC_BLOCK_MODE, "").strip()
            self.parse_automatic_block_config(config)

        line = ""
        block_content = []
        stop = self.join_strings(CONTTY_PREFIX, END_BLOCK_KEYWORD)
        while index < len(lines):
            line = lines[index + lines_read]
            lines_read += 1
            if line.startswith(stop):
                break
            else:
                block_content.append(line)

        if mode == MANUAL_BLOCK_MODE:
            self.add_manual_block(block_content)

        return lines_read

    def parse(self, lines):
        self.unmanaged_config = []

        index = 0
        while index < len(lines):
            line = lines[index].strip()
            if not line.startswith(CONTTY_PREFIX):
                if line or not self.unmanaged_config or not self.unmanaged_config[-1]:
                    self.unmanaged_config.append(line)
                index += 1
                continue

            index += self.parse_contty_block(line, index, lines)

    def build_automatic_block_header(self, data):
        prefix = self.join_strings(
            CONTTY_PREFIX,
            START_BLOCK_KEYWORD,
            AUTOMATIC_BLOCK_MODE
        )
        data = json.dumps(data)
        return "{prefix} {data}".format(prefix=prefix, data=data)

    def build_manual_block_header(self):
        return self.join_strings(CONTTY_PREFIX, START_BLOCK_KEYWORD, MANUAL_BLOCK_MODE)

    def build_block_footer(self):
        return self.join_strings(CONTTY_PREFIX, END_BLOCK_KEYWORD)

    def build_automatic_block(self, **kwargs):
        template = """
{block_header}
https://{hostname} {{
    header -Server
    proxy / {service}:{port} {{
        websocket
        transparent
    }}
    tls {email}
}}
{block_footer}
"""
        kwargs.update({
            "block_header": self.build_automatic_block_header(kwargs),
            "block_footer": self.build_block_footer(),
        })
        return template.format(**kwargs).split("\n")

    def get_lines(self):
        lines = []
        for entry in self.unmanaged_config:
            lines.append(entry)
        for block in self.manual_blocks:
            lines.append("")
            lines.append(self.build_manual_block_header())
            for line in block:
                lines.append(line)
            lines.append(self.build_block_footer())
            lines.append("")
        for config in self.automatic_blocks:
            for line in self.build_automatic_block(**config):
                lines.append(line)
        return lines

    def write_to_file(self, filepath):
        path = sys.path.abspath(filepath)
        lines = self.get_lines()
        with open(path, "w") as f:
            f.writelines(lines)
