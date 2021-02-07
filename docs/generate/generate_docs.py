"""scrapli_netconf.docs.generate"""
import pdoc
from pdoc import _render_template, tpl_lookup

context = pdoc.Context()
module = pdoc.Module("scrapli_netconf", context=context)
pdoc.link_inheritance(context)
tpl_lookup.directories.insert(0, "docs/generate")

doc_map = {
    "scrapli_netconf.driver.base_driver": {"path": "driver/base_driver", "content": None},
    "scrapli_netconf.driver.sync_driver": {"path": "driver/sync_driver", "content": None},
    "scrapli_netconf.driver.async_driver": {"path": "driver/async_driver", "content": None},
    "scrapli_netconf.channel.base_channel": {"path": "channel/base_channel", "content": None},
    "scrapli_netconf.channel.sync_channel": {"path": "channel/sync_channel", "content": None},
    "scrapli_netconf.channel.async_channel": {"path": "channel/async_channel", "content": None},
    "scrapli_netconf.transport.plugins.asyncssh.transport": {
        "path": "transport/plugins/asyncssh",
        "conent": None,
    },
    "scrapli_netconf.transport.plugins.paramiko.transport": {
        "path": "transport/plugins/paramiko",
        "conent": None,
    },
    "scrapli_netconf.transport.plugins.ssh2.transport": {
        "path": "transport/plugins/ssh2",
        "conent": None,
    },
    "scrapli_netconf.transport.plugins.system.transport": {
        "path": "transport/plugins/system",
        "conent": None,
    },
    "scrapli_netconf.exceptions": {"path": "exceptions", "content": None},
    "scrapli_netconf.constants": {"path": "constants", "content": None},
    "scrapli_netconf.helper": {"path": "helper", "content": None},
    "scrapli_netconf.response": {"path": "response", "content": None},
}


def recursive_mds(module):  # noqa
    """Recursively render mkdocs friendly markdown/html"""
    yield module.name, _render_template("/mkdocs_markdown.mako", module=module)
    for submod in module.submodules():
        yield from recursive_mds(submod)


def main():
    """Generate docs"""
    for module_name, html in recursive_mds(module=module):
        if module_name not in doc_map.keys():
            continue

        doc_map[module_name]["content"] = html

    for module_name, module_doc_data in doc_map.items():
        if not module_doc_data["content"]:
            print(f"broken module {module_name}")
            continue
        with open(f"docs/api_docs/{module_doc_data['path']}.md", "w") as f:
            f.write(module_doc_data["content"])


if __name__ == "__main__":
    main()
