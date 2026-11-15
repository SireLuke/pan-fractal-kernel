from dataclasses import dataclass

import pytest

from abom_v8.adapters.registry import PluginDescriptor, PluginRegistry


@dataclass
class ExamplePlugin:
    descriptor: PluginDescriptor


def test_register_and_resolve_schema_compatible_plugin():
    plugin = ExamplePlugin(PluginDescriptor("test.curve", "0.1.0", ("0.1",), ("transport.curve",)))
    registry = PluginRegistry()
    registry.register(plugin)
    assert registry.resolve("test.curve", schema_version="0.1") is plugin
    assert registry.descriptors() == (plugin.descriptor,)


def test_rejects_duplicate_or_incompatible_plugin():
    plugin = ExamplePlugin(PluginDescriptor("test.curve", "0.1.0", ("0.1",)))
    registry = PluginRegistry()
    registry.register(plugin)
    with pytest.raises(ValueError, match="already registered"):
        registry.register(plugin)
    with pytest.raises(ValueError, match="does not support"):
        registry.resolve("test.curve", schema_version="0.2")
