import type { ConnectorDefinition, ConnectorProtocol } from './connector-types.js';
import { BacnetIpReadonlyProtocolPlugin } from './plugins/bacnet-ip-readonly-protocol-plugin.js';
import { FileImportProtocolPlugin } from './plugins/file-import-protocol-plugin.js';
import { HttpPollingProtocolPlugin } from './plugins/http-polling-protocol-plugin.js';
import { ModbusTcpReadonlyProtocolPlugin } from './plugins/modbus-tcp-readonly-protocol-plugin.js';
import { OpcUaReadonlyProtocolPlugin } from './plugins/opc-ua-readonly-protocol-plugin.js';
import { SnmpReadonlyProtocolPlugin } from './plugins/snmp-readonly-protocol-plugin.js';
import { SimulatorProtocolPlugin } from './plugins/simulator-protocol-plugin.js';
import type { ProtocolPlugin } from './protocol-plugin-types.js';

function nowIso(): string {
  return new Date().toISOString();
}

export interface ProtocolPluginCompatibilityResult {
  readonly connectorId: string;
  readonly pluginId: string;
  readonly compatible: boolean;
  readonly reasons: readonly string[];
}

export class ProtocolPluginRuntimeRegistry {
  private readonly plugins = new Map<string, ProtocolPlugin>();

  public registerProtocolPlugin(plugin: ProtocolPlugin): ProtocolPlugin {
    this.plugins.set(plugin.pluginId, plugin);
    return plugin;
  }

  public listProtocolPlugins(): readonly ProtocolPlugin[] {
    return Array.from(this.plugins.values()).sort((a, b) => a.pluginId.localeCompare(b.pluginId));
  }

  public getProtocolPlugin(pluginId: string): ProtocolPlugin | null {
    return this.plugins.get(pluginId) ?? null;
  }

  public validateProtocolPluginCompatibility(
    connector: ConnectorDefinition,
    plugin: ProtocolPlugin,
  ): ProtocolPluginCompatibilityResult {
    const reasons: string[] = [];
    if (!plugin.supportedProtocols.includes(connector.protocol as ConnectorProtocol)) {
      reasons.push(`plugin does not support connector protocol: ${connector.protocol}`);
    }
    if (!plugin.capability.supportsPolling) {
      reasons.push('plugin does not support polling');
    }
    return {
      connectorId: connector.connectorId,
      pluginId: plugin.pluginId,
      compatible: reasons.length == 0,
      reasons,
    };
  }

  public exportProtocolPluginRegistrySnapshot(): {
    readonly generatedAt: string;
    readonly pluginCount: number;
    readonly protocolCount: number;
    readonly protocols: readonly string[];
    readonly plugins: ReadonlyArray<{
      readonly pluginId: string;
      readonly name: string;
      readonly version: string;
      readonly supportedProtocols: readonly string[];
      readonly capability: ProtocolPlugin['capability'];
    }>;
  } {
    const plugins = this.listProtocolPlugins();
    const protocols = Array.from(new Set(plugins.flatMap((plugin) => plugin.supportedProtocols))).sort();
    return {
      generatedAt: nowIso(),
      pluginCount: plugins.length,
      protocolCount: protocols.length,
      protocols,
      plugins: plugins.map((plugin) => ({
        pluginId: plugin.pluginId,
        name: plugin.name,
        version: plugin.version,
        supportedProtocols: [...plugin.supportedProtocols],
        capability: plugin.capability,
      })),
    };
  }
}

export function createC3FoundationProtocolPluginRegistry(): ProtocolPluginRuntimeRegistry {
  const registry = new ProtocolPluginRuntimeRegistry();
  registry.registerProtocolPlugin(new SimulatorProtocolPlugin());
  registry.registerProtocolPlugin(new FileImportProtocolPlugin());
  registry.registerProtocolPlugin(new HttpPollingProtocolPlugin());
  registry.registerProtocolPlugin(new BacnetIpReadonlyProtocolPlugin());
  registry.registerProtocolPlugin(new OpcUaReadonlyProtocolPlugin());
  registry.registerProtocolPlugin(new ModbusTcpReadonlyProtocolPlugin());
  registry.registerProtocolPlugin(new SnmpReadonlyProtocolPlugin());
  return registry;
}
