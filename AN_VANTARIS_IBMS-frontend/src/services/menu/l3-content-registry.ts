import type { AppMenuL3Item } from './types'
import { fallbackMenuItems } from './static-menu'

export interface L3ContentContext {
  l1Label: string
  l2Id: string
  l2Label: string
  path: string
  item: AppMenuL3Item
}

export interface L3ContentConfig {
  title: string
  subtitle: string
  primaryAction: string
  metrics: Array<{ label: string; value: string; note: string }>
  rows: Array<{ item: string; focus: string; status: string }>
}

interface L2ContentProfile {
  domain: string
  subject: string
  operatingFocus: string
  evidenceFocus: string
  ownerFocus: string
}

const L2_CONTENT_PROFILES: Record<string, L2ContentProfile> = {
  'dashboard-executive': { domain: 'Executive Dashboard', subject: 'portfolio performance', operatingFocus: 'portfolio health, service risk, and customer delivery posture', evidenceFocus: 'executive-ready evidence summaries', ownerFocus: 'executive review' },
  'dashboard-operations': { domain: 'Operations Dashboard', subject: 'daily operations', operatingFocus: 'live operations, availability, faults, maintenance, and energy posture', evidenceFocus: 'daily operating evidence', ownerFocus: 'operations review' },
  'dashboard-my': { domain: 'My Dashboard', subject: 'personal work queue', operatingFocus: 'assigned tasks, approvals, reports, and evidence items', evidenceFocus: 'personal action traceability', ownerFocus: 'assigned user review' },
  'dashboard-scenario': { domain: 'Scenario Dashboard', subject: 'scenario package', operatingFocus: 'industry scenario readiness and acceptance flow', evidenceFocus: 'scenario evidence package', ownerFocus: 'scenario review' },
  'operations-command-center': { domain: 'Command Center', subject: 'operations command', operatingFocus: 'active operational state, escalations, and service impact', evidenceFocus: 'decision and event evidence', ownerFocus: 'operator review' },
  'incident-management': { domain: 'Command Center', subject: 'incident response', operatingFocus: 'incident detail, impacted assets, response actions, and communications', evidenceFocus: 'closure and incident evidence', ownerFocus: 'incident owner review' },
  'shift-management': { domain: 'Command Center', subject: 'shift handover', operatingFocus: 'handover notes, watchlists, operator assignments, and open items', evidenceFocus: 'shift evidence', ownerFocus: 'shift supervisor review' },
  'service-impact': { domain: 'Command Center', subject: 'service impact', operatingFocus: 'customer impact, affected systems, SLA exposure, and recovery priority', evidenceFocus: 'impact evidence', ownerFocus: 'service owner review' },
  'decision-log': { domain: 'Command Center', subject: 'decision traceability', operatingFocus: 'decision owner, approval chain, and export readiness', evidenceFocus: 'decision evidence', ownerFocus: 'decision owner review' },
  'site-portfolio': { domain: 'Assets & Locations', subject: 'site portfolio', operatingFocus: 'site health, risk, energy, compliance, and reports', evidenceFocus: 'site evidence and reports', ownerFocus: 'portfolio review' },
  'buildings-zones': { domain: 'Assets & Locations', subject: 'building and zone hierarchy', operatingFocus: 'building overview, floor plans, zone conditions, and occupancy', evidenceFocus: 'location mapping evidence', ownerFocus: 'facility review' },
  'space-mapping': { domain: 'Assets & Locations', subject: 'space mapping', operatingFocus: 'asset, system, tag, floor-plan binding, and mapping gaps', evidenceFocus: 'mapping evidence', ownerFocus: 'space data review' },
  'system-registry': { domain: 'Assets & Locations', subject: 'system registry', operatingFocus: 'system health, alarms, faults, evidence, and reports', evidenceFocus: 'system evidence', ownerFocus: 'system owner review' },
  'asset-registry': { domain: 'Assets & Locations', subject: 'asset registry', operatingFocus: 'asset detail, relationships, health, history, and evidence', evidenceFocus: 'asset evidence', ownerFocus: 'asset owner review' },
  equipment: { domain: 'Assets & Locations', subject: 'equipment', operatingFocus: 'equipment runtime status, maintenance history, fault history, vendor information, and evidence', evidenceFocus: 'equipment evidence', ownerFocus: 'equipment owner review' },
  'points-tags': { domain: 'Assets & Locations', subject: 'points and tags', operatingFocus: 'point list, tag mapping, live values, trends, and mapping gaps', evidenceFocus: 'point mapping evidence', ownerFocus: 'data engineer review' },
  'controllers-gateways': { domain: 'Assets & Locations', subject: 'controllers and gateways', operatingFocus: 'controller, gateway, connectivity, protocol, EDGE, and LINK mapping status', evidenceFocus: 'diagnostic evidence', ownerFocus: 'integration engineer review' },
  'asset-graph': { domain: 'Assets & Locations', subject: 'asset graph', operatingFocus: 'relationship graph, dependency view, impact path, and data quality', evidenceFocus: 'graph evidence links', ownerFocus: 'asset intelligence review' },
  'floor-plan-hmi': { domain: 'Assets & Locations', subject: 'floor plan HMI map', operatingFocus: 'site plan, floor plan, zone overlays, asset overlays, alarms, and energy overlays', evidenceFocus: 'floor-plan evidence', ownerFocus: 'workspace visualization review' },
  'digital-twin': { domain: 'Assets & Locations', subject: 'digital twin', operatingFocus: 'asset twin, system twin, space twin, fault impact path, and scenarios', evidenceFocus: 'twin evidence', ownerFocus: 'digital twin review' },
  'security-life-safety-assets': { domain: 'Assets & Locations', subject: 'security and life safety assets', operatingFocus: 'access events, doors, CCTV, fire systems, and life safety status', evidenceFocus: 'security evidence', ownerFocus: 'life safety review' },
  'data-center-assets': { domain: 'Assets & Locations', subject: 'data center assets', operatingFocus: 'data hall health, power chain, cooling chain, environment, capacity risk, and critical alarms', evidenceFocus: 'IDC reports', ownerFocus: 'data center review' },
  'work-orders': { domain: 'Work Management', subject: 'work orders', operatingFocus: 'open, assigned, emergency, preventive, corrective, detail, and closure evidence', evidenceFocus: 'work order evidence', ownerFocus: 'maintenance supervisor review' },
  'preventive-maintenance': { domain: 'Work Management', subject: 'preventive maintenance', operatingFocus: 'PM calendar, templates, schedule, checklist, completion, evidence, and reports', evidenceFocus: 'PM evidence', ownerFocus: 'PM planner review' },
  'corrective-maintenance': { domain: 'Work Management', subject: 'corrective maintenance', operatingFocus: 'fault-linked work orders, manual work orders, technician assignment, parts, and closure review', evidenceFocus: 'corrective closure evidence', ownerFocus: 'maintenance engineer review' },
  'engineer-workload': { domain: 'Work Management', subject: 'engineer workload', operatingFocus: 'calendar, assignment load, discipline, shift availability, escalation owner, and next due work', evidenceFocus: 'workload evidence', ownerFocus: 'resource planner review' },
  'sla-escalation': { domain: 'Work Management', subject: 'SLA and escalation', operatingFocus: 'SLA dashboard, breach risk, escalation queue, supervisor review, impact, and aging buckets', evidenceFocus: 'SLA evidence', ownerFocus: 'SLA owner review' },
  'maintenance-analytics': { domain: 'Work Management', subject: 'maintenance analytics', operatingFocus: 'MTTR, MTBF, repeated failures, technician load, reliability, predictive risk, and improvement plan', evidenceFocus: 'analytics evidence', ownerFocus: 'reliability review' },
  inventory: { domain: 'Work Management', subject: 'inventory', operatingFocus: 'spare parts, stock, material requests, critical spares, vendor supply, and inventory evidence', evidenceFocus: 'inventory evidence', ownerFocus: 'stores review' },
  vendors: { domain: 'Work Management', subject: 'vendors', operatingFocus: 'vendor list, contract coverage, service level, warranty, and vendor performance', evidenceFocus: 'vendor evidence', ownerFocus: 'vendor manager review' },
  'maintenance-configuration': { domain: 'Work Management', subject: 'maintenance configuration', operatingFocus: 'work order types, priority matrix, assignment rules, checklists, SLA rules, teams, and evidence rules', evidenceFocus: 'configuration evidence', ownerFocus: 'maintenance admin review' },
  'alarm-console': { domain: 'Faults & Events', subject: 'alarm console', operatingFocus: 'active alarms, critical alarms, acknowledgement, shelving, suppression, escalation, and notes', evidenceFocus: 'alarm evidence', ownerFocus: 'alarm operator review' },
  'event-timeline': { domain: 'Faults & Events', subject: 'event timeline', operatingFocus: 'event stream, filters, detail, related assets, related faults, related work orders, and timeline evidence', evidenceFocus: 'event evidence', ownerFocus: 'event analyst review' },
  'alarm-rules': { domain: 'Faults & Events', subject: 'alarm rules', operatingFocus: 'priority, escalation, notification, suppression, routing, evidence, and audit rules', evidenceFocus: 'rule evidence', ownerFocus: 'alarm rule owner review' },
  'alarm-analytics': { domain: 'Faults & Events', subject: 'alarm analytics', operatingFocus: 'alarm volume, flood, repeated alarms, nuisance alarms, top assets, top systems, and SLA impact', evidenceFocus: 'alarm analytics evidence', ownerFocus: 'alarm performance review' },
  'fault-console': { domain: 'Faults & Events', subject: 'fault console', operatingFocus: 'active faults, critical faults, detail, correlation, RCA, actions, and evidence', evidenceFocus: 'fault evidence', ownerFocus: 'fault owner review' },
  'detection-correlation': { domain: 'Faults & Events', subject: 'detection and correlation', operatingFocus: 'detection rules, correlation rules, clustering, related alarms, related assets, and confidence', evidenceFocus: 'correlation evidence', ownerFocus: 'diagnostic analyst review' },
  diagnostics: { domain: 'Faults & Events', subject: 'diagnostics', operatingFocus: 'diagnostic queue, system, asset, OT network, hardware, evidence, and history', evidenceFocus: 'diagnostic evidence', ownerFocus: 'diagnostics review' },
  remediation: { domain: 'Faults & Events', subject: 'remediation', operatingFocus: 'recommended actions, manual actions, work order creation, escalation, SLA tracking, and closure notes', evidenceFocus: 'closure evidence', ownerFocus: 'remediation owner review' },
  'fault-analytics': { domain: 'Faults & Events', subject: 'fault analytics', operatingFocus: 'fault trends, top fault types, repeat faults, MTTR, downtime impact, reliability, and improvement', evidenceFocus: 'fault analytics evidence', ownerFocus: 'reliability analyst review' },
  'event-evidence': { domain: 'Faults & Events', subject: 'event evidence', operatingFocus: 'evidence chain, UCDE trace, operator actions, export package, and audit trail', evidenceFocus: 'event evidence chain', ownerFocus: 'evidence owner review' },
  'energy-dashboard': { domain: 'Energy & Sustainability', subject: 'energy dashboard', operatingFocus: 'consumption, demand, intensity, meter health, exceptions, forecasts, and reports', evidenceFocus: 'energy evidence', ownerFocus: 'energy manager review' },
  metering: { domain: 'Energy & Sustainability', subject: 'metering', operatingFocus: 'meter list, mapping, readings, quality, trends, faults, and import export', evidenceFocus: 'meter evidence', ownerFocus: 'metering review' },
  'energy-faults': { domain: 'Energy & Sustainability', subject: 'energy faults', operatingFocus: 'high consumption, unoccupied use, weekend use, peak demand, meter offline, and flatline events', evidenceFocus: 'energy fault evidence', ownerFocus: 'energy fault review' },
  sustainability: { domain: 'Energy & Sustainability', subject: 'sustainability', operatingFocus: 'carbon, ESG, green mark support, utility baseline, reductions, and ESG reports', evidenceFocus: 'sustainability evidence', ownerFocus: 'sustainability review' },
  optimization: { domain: 'Energy & Sustainability', subject: 'optimization', operatingFocus: 'energy opportunities, setpoints, schedules, equipment efficiency, anomalies, savings, and action plans', evidenceFocus: 'optimization evidence', ownerFocus: 'optimization review' },
  'energy-compliance': { domain: 'Energy & Sustainability', subject: 'energy compliance', operatingFocus: 'energy compliance, ESG compliance, audit evidence, report export, submissions, and historical records', evidenceFocus: 'compliance evidence', ownerFocus: 'compliance review' },
  'data-center-energy': { domain: 'Energy & Sustainability', subject: 'data center energy', operatingFocus: 'UPS, PDU, switchgear, generator, power metering, alarms, and trends', evidenceFocus: 'power evidence', ownerFocus: 'data center energy review' },
  'data-model': { domain: 'Data & Intelligence', subject: 'data model', operatingFocus: 'canonical objects, site model, systems, equipment, points, events, work orders, evidence, dictionary, and schema', evidenceFocus: 'data model evidence', ownerFocus: 'data architect review' },
  'data-lake': { domain: 'Data & Intelligence', subject: 'data lake', operatingFocus: 'raw landing, event store, time series, document store, evidence store, retention, quality, export, and lineage', evidenceFocus: 'data lineage evidence', ownerFocus: 'data platform review' },
  'asset-graph-intelligence': { domain: 'Data & Intelligence', subject: 'asset graph intelligence', operatingFocus: 'relationship graph, dependencies, impact paths, mappings, fault impact, maintenance impact, and evidence links', evidenceFocus: 'graph intelligence evidence', ownerFocus: 'asset intelligence review' },
  'knowledge-base': { domain: 'Data & Intelligence', subject: 'knowledge base', operatingFocus: 'fault, maintenance, energy, manuals, SOP, RCA, troubleshooting, vendor knowledge, and evidence', evidenceFocus: 'knowledge evidence', ownerFocus: 'knowledge owner review' },
  'ai-model-hub': { domain: 'Data & Intelligence', subject: 'AI model hub', operatingFocus: 'model registry, versions, fault models, energy models, maintenance models, risk models, evaluation, approval, and evidence', evidenceFocus: 'model evidence', ownerFocus: 'AI governance review' },
  nexusai: { domain: 'Data & Intelligence', subject: 'NexusAI insights', operatingFocus: 'insight overview, fault, energy, maintenance, risk, branch audit, and AI evidence', evidenceFocus: 'AI evidence', ownerFocus: 'AI insight review' },
  recommendations: { domain: 'Data & Intelligence', subject: 'recommendations', operatingFocus: 'recommended actions, prioritized risks, operational, maintenance, energy suggestions, decision support, and confidence', evidenceFocus: 'confidence evidence', ownerFocus: 'recommendation review' },
  forecasting: { domain: 'Data & Intelligence', subject: 'forecasting', operatingFocus: 'fault, energy, maintenance, risk, capacity forecasts, and model evidence', evidenceFocus: 'forecast evidence', ownerFocus: 'forecast review' },
  'data-evidence-center': { domain: 'Data & Intelligence', subject: 'evidence center', operatingFocus: 'source, decision, fault, maintenance, energy, report, hash, and export evidence', evidenceFocus: 'UCDE evidence', ownerFocus: 'evidence owner review' },
  'data-governance': { domain: 'Data & Intelligence', subject: 'data governance', operatingFocus: 'ownership, classification, quality rules, access policy, retention, lineage, audit, and evidence', evidenceFocus: 'governance evidence', ownerFocus: 'data governance review' },
  'report-center': { domain: 'Reports & Documents', subject: 'report center', operatingFocus: 'operations, alarms, faults, maintenance, energy, compliance, and customer delivery reports', evidenceFocus: 'report evidence', ownerFocus: 'report owner review' },
  'export-center': { domain: 'Reports & Documents', subject: 'export center', operatingFocus: 'PDF, Excel, evidence bundles, handoff packages, schedules, history, and audit', evidenceFocus: 'export audit evidence', ownerFocus: 'export owner review' },
  'compliance-center': { domain: 'Reports & Documents', subject: 'compliance center', operatingFocus: 'IEC, ESG, green mark, customer acceptance, checklist, gaps, and compliance reports', evidenceFocus: 'compliance report evidence', ownerFocus: 'compliance owner review' },
  'document-library': { domain: 'Reports & Documents', subject: 'document library', operatingFocus: 'document register, drawings, manuals, methods, test reports, vendor documents, revision, and evidence', evidenceFocus: 'document evidence', ownerFocus: 'document controller review' },
  'drawing-bim-documents': { domain: 'Reports & Documents', subject: 'drawing and BIM documents', operatingFocus: 'as-built drawings, single line diagrams, controls, floor plans, BIM references, approval, and evidence', evidenceFocus: 'drawing evidence', ownerFocus: 'BIM document review' },
  'asset-document-binding': { domain: 'Reports & Documents', subject: 'asset document binding', operatingFocus: 'asset documents, system documents, manuals, warranties, spare parts, procedures, and evidence', evidenceFocus: 'document-to-asset evidence', ownerFocus: 'asset document review' },
  'handover-package-docs': { domain: 'Reports & Documents', subject: 'handover package', operatingFocus: 'handover index, FAT, SAT, commissioning, training, acceptance, export, and evidence', evidenceFocus: 'handover evidence', ownerFocus: 'handover owner review' },
  'document-governance': { domain: 'Reports & Documents', subject: 'document governance', operatingFocus: 'version control, approval workflow, access control, retention, change request, audit trail, and signature hash', evidenceFocus: 'document audit evidence', ownerFocus: 'document governance review' },
  'security-overview': { domain: 'Governance & Security', subject: 'security overview', operatingFocus: 'security dashboard, login risk, sessions, privileged users, events, violations, and evidence', evidenceFocus: 'security evidence', ownerFocus: 'security review' },
  'identity-access': { domain: 'Governance & Security', subject: 'identity and access', operatingFocus: 'users, roles, permissions, teams, MFA, session policy, access review, and audit', evidenceFocus: 'identity audit', ownerFocus: 'identity owner review' },
  'policy-governance': { domain: 'Governance & Security', subject: 'policy governance', operatingFocus: 'security, approval, data access, AI usage, evidence, retention, exceptions, and audit policies', evidenceFocus: 'policy evidence', ownerFocus: 'policy owner review' },
  'compliance-control': { domain: 'Governance & Security', subject: 'compliance control', operatingFocus: 'control mapping, ISO, cybersecurity checklist, OT baseline, data protection, readiness, and evidence', evidenceFocus: 'compliance evidence', ownerFocus: 'control owner review' },
  'governance-audit-trail': { domain: 'Governance & Security', subject: 'audit trail', operatingFocus: 'login, user action, configuration, data access, report export, AI decision, evidence, and tamper review', evidenceFocus: 'audit trail evidence', ownerFocus: 'audit owner review' },
  'risk-control-register': { domain: 'Governance & Security', subject: 'risk and control register', operatingFocus: 'risk register, control register, findings, mitigations, owners, schedule, and evidence', evidenceFocus: 'risk evidence', ownerFocus: 'risk owner review' },
  'cybersecurity-operations': { domain: 'Governance & Security', subject: 'cybersecurity operations', operatingFocus: 'asset vulnerability, network exposure, OT events, incident queue, threat intelligence, remediation, and evidence', evidenceFocus: 'cyber evidence', ownerFocus: 'cybersecurity review' },
  'users-roles': { domain: 'Administration', subject: 'users and roles', operatingFocus: 'users, roles, permissions, teams, role mapping, access review, and user audit', evidenceFocus: 'user audit evidence', ownerFocus: 'system admin review' },
  'system-settings': { domain: 'Administration', subject: 'system settings', operatingFocus: 'site, system, notification, evidence, report settings, feature flags, and configuration audit', evidenceFocus: 'configuration audit', ownerFocus: 'system settings review' },
  'license-edition': { domain: 'Administration', subject: 'license and edition', operatingFocus: 'edition, licensed modules, entitlements, usage limits, renewal, and license evidence', evidenceFocus: 'license evidence', ownerFocus: 'license admin review' },
  'backup-recovery': { domain: 'Administration', subject: 'backup and recovery', operatingFocus: 'backup plan, restore plan, recovery evidence, rollback, DR readiness, and reports', evidenceFocus: 'recovery evidence', ownerFocus: 'DR owner review' },
  'integration-foundation': { domain: 'Administration', subject: 'integration foundation', operatingFocus: 'connectors, EDGE, LINK, contracts, data quality, evidence, and integration checklist', evidenceFocus: 'integration evidence', ownerFocus: 'integration owner review' },
  'engineer-tools': { domain: 'Administration', subject: 'engineer tools', operatingFocus: 'deployment readiness, diagnostics, offline handoff, installer console, package management, server precheck, and evidence', evidenceFocus: 'diagnostics evidence', ownerFocus: 'engineer tools review' },
}

function profileFor(l2Id: string, l2Label: string, l1Label: string): L2ContentProfile {
  return L2_CONTENT_PROFILES[l2Id] ?? {
    domain: l1Label,
    subject: l2Label.toLowerCase(),
    operatingFocus: `${l2Label.toLowerCase()} operating status, review items, evidence, and customer handoff context`,
    evidenceFocus: `${l2Label.toLowerCase()} evidence`,
    ownerFocus: `${l2Label.toLowerCase()} owner review`,
  }
}

export function resolveL3ContentConfig(context: L3ContentContext): L3ContentConfig {
  const profile = profileFor(context.l2Id, context.l2Label, context.l1Label)
  const section = context.item.label
  const mappedModule = context.item.mappedExistingModule ?? context.l2Label
  const status = context.item.status?.replace(/-/g, ' ') ?? 'mapped'

  return {
    title: `${context.l2Label} / ${section}`,
    subtitle: `${section} is the selected ${profile.subject} section under ${profile.domain}. It focuses on ${profile.operatingFocus}.`,
    primaryAction: `Review ${section}`,
    metrics: [
      { label: 'Section', value: section, note: profile.subject },
      { label: 'Workspace', value: context.l2Label, note: profile.domain },
      { label: 'Module', value: mappedModule, note: context.path },
      { label: 'Status', value: status, note: profile.ownerFocus },
    ],
    rows: [
      { item: `Review ${section}`, focus: profile.operatingFocus, status: 'Selected' },
      { item: `Validate ${section} evidence`, focus: profile.evidenceFocus, status: 'Ready' },
      { item: `Prepare ${section} handoff`, focus: profile.ownerFocus, status: 'Guarded' },
    ],
  }
}

export function resolveL3RouteContentConfig(menuId: unknown, l3Id: unknown): L3ContentConfig | undefined {
  const context = resolveL3RouteContentContext(menuId, l3Id)
  return context ? resolveL3ContentConfig(context) : undefined
}

export function resolveL3RouteContentContext(menuId: unknown, l3Id: unknown): L3ContentContext | undefined {
  if (typeof menuId !== 'string' || !menuId) {
    return undefined
  }

  const selectedL3Id = typeof l3Id === 'string' ? l3Id : ''
  const normalizedSelectedL3Id = selectedL3Id.replace(/-\d+$/, '')

  for (const l1 of fallbackMenuItems) {
    const l2 = (l1.children ?? []).find((child) => child.id === menuId)
    if (!l2) {
      continue
    }

    const l3Items = l2.l3Items ?? []
    const exact = l3Items.find((item) => item.id === selectedL3Id)
    const normalized = l3Items.find((item) => item.id.replace(/-\d+$/, '') === normalizedSelectedL3Id)
    const item = exact ?? normalized ?? l3Items[0]
    if (!item) {
      return undefined
    }

    return {
      l1Label: l1.label,
      l2Id: l2.id,
      l2Label: l2.label,
      path: l2.path,
      item,
    }
  }

  return undefined
}
