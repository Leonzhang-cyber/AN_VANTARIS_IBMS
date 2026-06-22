import type { PluginMetadata } from './types.js';

export const DEFAULT_PLUGIN_METADATA: readonly PluginMetadata[] = [
  {
    id: 'plugin-bacnet-v1',
    name: 'BACnet Capability Descriptor',
    protocol: 'bacnet',
    version: '1.0.0',
    capabilities: ['read-property', 'subscribe-cov', 'health'],
    lifecycleState: 'configured',
    configSchemaRef: 'edge://plugin/bacnet/schema-v1',
    enabled: true,
    notes: 'metadata-only plugin scaffold',
  },
  {
    id: 'plugin-modbus-v1',
    name: 'Modbus Capability Descriptor',
    protocol: 'modbus',
    version: '1.0.0',
    capabilities: ['polling', 'command-placeholder', 'health'],
    lifecycleState: 'configured',
    configSchemaRef: 'edge://plugin/modbus/schema-v1',
    enabled: true,
    notes: 'metadata-only plugin scaffold',
  },
  {
    id: 'plugin-opcua-v1',
    name: 'OPCUA Capability Descriptor',
    protocol: 'opcua',
    version: '1.0.0',
    capabilities: ['polling', 'write-placeholder', 'health'],
    lifecycleState: 'configured',
    configSchemaRef: 'edge://plugin/opcua/schema-v1',
    enabled: true,
    notes: 'metadata-only plugin scaffold',
  },
  {
    id: 'plugin-mqtt-v1',
    name: 'MQTT Capability Descriptor',
    protocol: 'mqtt',
    version: '1.0.0',
    capabilities: ['subscribe', 'publish', 'event-ingest', 'health'],
    lifecycleState: 'configured',
    configSchemaRef: 'edge://plugin/mqtt/schema-v1',
    enabled: true,
    notes: 'metadata-only plugin scaffold',
  },
  {
    id: 'plugin-vendor-sdk-v1',
    name: 'Vendor SDK Placeholder',
    protocol: 'vendor-sdk',
    version: '1.0.0',
    capabilities: ['metadata', 'health'],
    lifecycleState: 'disabled',
    configSchemaRef: 'edge://plugin/vendor-sdk/schema-v1',
    enabled: false,
    notes: 'placeholder only, no external sdk binding',
  },
];

export class ProtocolPluginRegistry {
  private readonly plugins = new Map<string, PluginMetadata>();

  public constructor(initial: readonly PluginMetadata[] = DEFAULT_PLUGIN_METADATA) {
    for (const plugin of initial) {
      this.register(plugin);
    }
  }

  public register(metadata: PluginMetadata): void {
    this.plugins.set(metadata.id, { ...metadata });
  }

  public list(): readonly PluginMetadata[] {
    return Array.from(this.plugins.values());
  }

  public setLifecycleState(id: string, state: PluginMetadata['lifecycleState']): PluginMetadata {
    const plugin = this.require(id);
    plugin.lifecycleState = state;
    return plugin;
  }

  public setEnabled(id: string, enabled: boolean): PluginMetadata {
    const plugin = this.require(id);
    plugin.enabled = enabled;
    return plugin;
  }

  public snapshot(): { readonly generatedAt: string; readonly plugins: readonly PluginMetadata[] } {
    return {
      generatedAt: new Date().toISOString(),
      plugins: this.list(),
    };
  }

  private require(id: string): PluginMetadata {
    const plugin = this.plugins.get(id);
    if (!plugin) {
      throw new Error(`plugin not found: ${id}`);
    }
    return plugin;
  }
}
