"""
Usage: {prog} [OPTION] FILE1 FILE2
Compare two XML files, ignoring element and attribute order.
Any extra options are passed to the `diff' command.
Copyright (c) 2017, Johannes H. Jensen.
License: BSD, see LICENSE for more details.

Original source: https://github.com/joh/xmldiffs
Thank you Johannes!
"""
import re
import subprocess
import xml.etree.ElementTree as ET
from tempfile import NamedTemporaryFile


def attr_str(k, v):
    return '{}="{}"'.format(k, v)


def node_str(n):
    attrs = sorted(n.attrib.items())
    astr = " ".join(attr_str(k, v) for k, v in attrs)
    s = n.tag
    if astr:
        s += " " + astr
    return s


def node_key(n):
    return node_str(n)


def indent(s, level):
    return "  " * level + s


def write_sorted(stream, node, level=0):
    children = list(node)
    text = (node.text or "").strip()
    tail = (node.tail or "").strip()

    if children or text:
        children.sort(key=node_key)

        node_start = indent("<" + node_str(node) + ">", level)
        stream.write(node_start)

        if text and len(children) == 0:
            line_length = len(node_start) + len(text) + 1 + len(node.tag) + 1
            if line_length < 120:
                stream.write(text)
                stream.write("</" + node.tag + ">\n")
            else:
                stream.write("\n")
                stream.write(indent(text + "\n", level))
                stream.write(indent("</" + node.tag + ">\n", level))

        else:
            stream.write("\n")
            if text:
                stream.write(indent(text + "\n", level))

            for child in children:
                write_sorted(stream, child, level + 1)

            stream.write(indent("</" + node.tag + ">\n", level))

    else:
        stream.write(indent("<" + node_str(node) + "/>\n", level))

    if tail:
        stream.write(indent(tail + "\n", level))


def xmldiffs(file1, file2):
    tree = ET.fromstring(file1)
    tmp1 = NamedTemporaryFile("w")
    write_sorted(tmp1, tree)
    tmp1.flush()

    tree = ET.fromstring(file2)
    tmp2 = NamedTemporaryFile("w")
    write_sorted(tmp2, tree)
    tmp2.flush()

    args = ["diff"]
    args += ["-u"]
    args += ["--label", file1, "--label", file2]
    args += [tmp1.name, tmp2.name]

    return subprocess.call(args)


def cisco_iosxe_replace_config_data(config):
    config = re.sub(
        pattern=r"! Last configuration change at \d{2}:\d{2}:\d{2} UTC \w{3} \w{3} \d{1,2} \d{4} .*",
        repl="TIMESTAMP",
        string=config,
        flags=re.M | re.I,
    )
    config = re.sub(
        pattern=r"([a-fA-F0-9]{2}:){5}[a-fA-F0-9]{2}",
        repl="MAC_ADDRESS",
        string=config,
        flags=re.M | re.I,
    )
    # iosxe does stupid stuff where there are a few single character trailing white spaces somehow?
    # that or i need to be doing this in the library like i do in scrapli core??
    config = "\n".join([line.rstrip() for line in config.splitlines()])
    config = replace_message_id(config)
    return config


def cisco_iosxr_replace_config_data(config):
    config = re.sub(
        pattern=r"<password>.*</password>",
        repl="PASSWORD",
        string=config,
        flags=re.M | re.I,
    )
    # iosxe does stupid stuff where there are a few single character trailing white spaces somehow?
    # that or i need to be doing this in the library like i do in scrapli core??
    config = "\n".join([line.rstrip() for line in config.splitlines()])
    config = replace_message_id(config)
    return config


def juniper_junos_replace_config_data(config):
    config = re.sub(
        pattern=r'junos:commit-seconds="\d+" junos:commit-localtime="\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} UTC"',
        repl='timestamp="TIMESTAMP"',
        string=config,
        flags=re.M | re.I,
    )
    config = re.sub(
        pattern=r'junos:changed-seconds="\d+" junos:changed-localtime="\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} UTC"',
        repl='timestamp="TIMESTAMP"',
        string=config,
        flags=re.M | re.I,
    )
    config = re.sub(
        pattern=r"<encrypted-password>.*</encrypted-password>",
        repl="PASSWORD",
        string=config,
        flags=re.M | re.I,
    )
    config = replace_message_id(config)
    return config


def replace_message_id(response_string):
    response_string = re.sub(
        pattern=r"message-id=\"\d+\"",
        repl='message-id="101"',
        string=response_string,
        flags=re.M | re.I,
    )
    return response_string
