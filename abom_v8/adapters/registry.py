"""Small dependency-free registry for modular ABOM-V8 plug-ins."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class PluginDescriptor:
    plugin_id: str
    version: str
    supported_schema_versions: tuple[str, ...]
    capabilities: tuple[str, ...] = ()


class Plugin(Protocol):
    descriptor: PluginDescriptor


class PluginRegistry:
    """Register plug-ins by id and resolve only compatible schema versions."""

    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        descriptor = getattr(plugin, "descriptor", None)
        if not isinstance(descriptor, PluginDescriptor):
            raise TypeError("plugin must expose a PluginDescriptor as .descriptor")
        if not descriptor.plugin_id.strip() or not descriptor.version.strip():
            raise ValueError("plugin_id and version must be non-empty")
        if not descriptor.supported_schema_versions:
            raise ValueError("plugin must declare at least one supported schema version")
        if descriptor.plugin_id in self._plugins:
            raise ValueError(f"plugin already registered: {descriptor.plugin_id}")
        self._plugins[descriptor.plugin_id] = plugin

    def resolve(self, plugin_id: str, *, schema_version: str) -> Plugin:
        try:
            plugin = self._plugins[plugin_id]
        except KeyError as exc:
            raise KeyError(f"unknown plugin: {plugin_id}") from exc
        if schema_version not in plugin.descriptor.supported_schema_versions:
            raise ValueError(
                f"plugin {plugin_id!r} does not support schema {schema_version!r}"
            )
        return plugin

    def descriptors(self) -> tuple[PluginDescriptor, ...]:
        return tuple(plugin.descriptor for plugin in self._plugins.values())
