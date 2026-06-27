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
  selectedLabel?: string
  sectionEyebrow?: string
  l3Tabs?: Array<{ key: string; label: string; active: boolean }>
  connectedWorkspaces?: string[]
  relatedWorkspaces?: string[]
  metrics: Array<{ label: string; value: string; note: string }>
  rows: Array<{ item: string; focus: string; status: string; owner?: string; priority?: string; open?: string }>
  dashboardWorkbench?: DashboardWorkbenchConfig
}

export interface DashboardWorkbenchConfig {
  breadcrumb: string
  intent: string
  owner: string
  nextStep: string
  workspaceState: string
  dataState: string
  persona: string
  commandFocus: string
  signalLabel: string
  signalValue: string
  riskLabel: string
  riskValue: string
  evidenceLabel: string
  evidenceValue: string
  tabs: string[]
  actions: string[]
  connectedWorkspaces: string[]
  signalCards: Array<{ label: string; value: string; note: string; severity: 'good' | 'watch' | 'risk'; icon: string }>
  visualType: DashboardVisualType
  contextRows: Array<{ label: string; value: string; note: string }>
  productionPanels: Array<{ dimension: DashboardProductionDimension; signal: string; detail: string; owner: string }>
  lanes: Array<{ dimension: string; title: string; detail: string; state: string }>
  focusCards: Array<{ title: string; value: string; detail: string; tone: 'good' | 'watch' | 'risk' }>
  heatmap: Array<{ label: string; value: number; tone: 'good' | 'watch' | 'risk' }>
  readinessLayers: Array<{ layer: string; health: string; risk: string; dataState: string; owner: string; nextAction: string; evidence: string; governanceNote: string }>
  acceptanceFooter: Array<{ label: string; value: string }>
}

interface WorkspaceOverviewSectionConfig {
  displayLabel: string
  title: string
  subtitle: string
  primaryAction: string
}

const DASHBOARD_DEFAULT_CONNECTED_WORKSPACES = [
  'Work Management',
  'Assets & Locations',
  'Faults & Events',
  'Reports & Documents',
  'Governance & Security',
  'Integration & Partner Hub',
]

const INDUSTRY_VIEW_CONNECTED_WORKSPACES = [
  'Industry Solutions',
  'Integration & Partner Hub',
  'Assets & Locations',
  'Reports & Documents',
  'Governance & Security',
  'Data & Intelligence',
]

type DashboardVisualType =
  | 'workspace-priority-board'
  | 'executive-risk-board'
  | 'live-operations-board'
  | 'portfolio-scorecard'
  | 'industry-profile-map'
  | 'value-realization-scorecard'
  | 'service-risk-board'
  | 'partner-health-map'
  | 'readiness-checklist-board'
  | 'seven-layer-readiness-board'
  | 'safe-fallback-board'

type DashboardProductionDimension = 'Pain Point' | 'Decision Signal' | 'Operational Context' | 'Action' | 'Evidence' | 'Governance'

interface L2ContentProfile {
  domain: string
  subject: string
  operatingFocus: string
  evidenceFocus: string
  ownerFocus: string
}

interface DashboardWorkbenchProfile {
  persona: string
  subject: string
  commandFocus: string
  signalLabel: string
  signalValue: string
  riskLabel: string
  riskValue: string
  evidenceLabel: string
  evidenceValue: string
  metricLabels: [string, string, string, string]
  dimensions: Array<{ dimension: string; title: string; detail: string; state: string }>
  focusCards: Array<{ title: string; value: string; detail: string; tone: 'good' | 'watch' | 'risk' }>
  heatmap: Array<{ label: string; value: number; tone: 'good' | 'watch' | 'risk' }>
}

const DASHBOARD_WORKBENCH_PROFILES: Record<string, DashboardWorkbenchProfile> = {
  'workspace-overview': {
    persona: 'Role-based workspace',
    subject: 'role-based priority entry',
    commandFocus: 'showing who the user is, what to inspect first, which actions need attention, what evidence is missing, which workspaces connect to the role, and whether the user is allowed to proceed',
    signalLabel: 'Workspace Health',
    signalValue: '92%',
    riskLabel: 'Assigned Actions',
    riskValue: '7',
    evidenceLabel: 'Evidence Readiness',
    evidenceValue: '18 / 21',
    metricLabels: ['Workspace Health', 'Assigned Actions', 'Evidence Readiness', 'Readiness Gate'],
    dimensions: [
      { dimension: 'Detect', title: 'Role risk signal', detail: 'Open risk signals filtered by role, site, and responsibility.', state: 'Live' },
      { dimension: 'Diagnose', title: 'Workspace context', detail: 'Related sites, systems, tasks, and evidence are grouped for review.', state: 'Mapped' },
      { dimension: 'Decide', title: 'Priority actions', detail: 'Assigned actions are ordered by customer impact and operating urgency.', state: 'Ready' },
      { dimension: 'Dispatch', title: 'Owner handoff', detail: 'Action owners and next review windows are visible before escalation.', state: 'Guarded' },
      { dimension: 'Document', title: 'Evidence pack', detail: 'Evidence links are prepared for supervisor and customer review.', state: 'Ready' },
      { dimension: 'Deliver', title: 'Readiness quality', detail: 'Workspace readiness is tracked before handoff or reporting.', state: 'Watch' },
    ],
    focusCards: [
      { title: 'Role queue', value: '24', detail: 'assigned items grouped by operator, engineer, supervisor, and customer view', tone: 'watch' },
      { title: 'Open handoffs', value: '6', detail: 'handoffs needing evidence or owner confirmation', tone: 'risk' },
      { title: 'Ready sections', value: '11', detail: 'sections ready for review without route or API changes', tone: 'good' },
    ],
    heatmap: [
      { label: 'Operations', value: 82, tone: 'good' },
      { label: 'Maintenance', value: 68, tone: 'watch' },
      { label: 'Evidence', value: 76, tone: 'good' },
      { label: 'Governance', value: 61, tone: 'watch' },
    ],
  },
  'dashboard-executive': {
    persona: 'Executive / supervisor',
    subject: 'executive portfolio control view',
    commandFocus: 'summarizing portfolio performance, customer exposure, critical actions, and evidence readiness for leadership review',
    signalLabel: 'Portfolio posture',
    signalValue: '88%',
    riskLabel: 'Critical exposure',
    riskValue: '5',
    evidenceLabel: 'Board packs',
    evidenceValue: '12',
    metricLabels: ['Portfolio signal', 'Critical actions', 'Customer impact', 'Executive pack'],
    dimensions: [
      { dimension: 'Detect', title: 'Executive risk signal', detail: 'Portfolio risks are ranked by service impact, SLA exposure, and customer visibility.', state: 'Live' },
      { dimension: 'Diagnose', title: 'Performance context', detail: 'Site, service, energy, and maintenance trends are consolidated for leadership review.', state: 'Mapped' },
      { dimension: 'Decide', title: 'Critical service actions', detail: 'High-impact actions are separated from routine operational noise.', state: 'Ready' },
      { dimension: 'Dispatch', title: 'Owner accountability', detail: 'Accountable owners and executive escalation paths are visible.', state: 'Guarded' },
      { dimension: 'Document', title: 'Executive evidence pack', detail: 'Evidence summaries are shaped for board, customer, and governance review.', state: 'Ready' },
      { dimension: 'Deliver', title: 'Portfolio readiness', detail: 'Readiness quality shows whether the portfolio can be reported externally.', state: 'Watch' },
    ],
    focusCards: [
      { title: 'Sites at risk', value: '3', detail: 'portfolio sites with service, compliance, or energy exposure', tone: 'risk' },
      { title: 'Customer-visible items', value: '9', detail: 'items requiring customer-ready language and evidence', tone: 'watch' },
      { title: 'Ready briefings', value: '4', detail: 'executive packs ready for supervisor review', tone: 'good' },
    ],
    heatmap: [
      { label: 'Service', value: 73, tone: 'watch' },
      { label: 'Customer', value: 64, tone: 'watch' },
      { label: 'Energy', value: 81, tone: 'good' },
      { label: 'Compliance', value: 58, tone: 'risk' },
    ],
  },
  'dashboard-operations': {
    persona: 'Operations manager',
    subject: 'daily operations snapshot',
    commandFocus: 'coordinating live situation awareness, recovery actions, availability governance, and daily evidence',
    signalLabel: 'Live availability',
    signalValue: '96%',
    riskLabel: 'Action queue',
    riskValue: '14',
    evidenceLabel: 'Timeline links',
    evidenceValue: '31',
    metricLabels: ['Live signal', 'Recovery actions', 'Availability guard', 'Daily evidence'],
    dimensions: [
      { dimension: 'Detect', title: 'Operations risk signal', detail: 'Live risks are separated by alarm, fault, maintenance, and energy source.', state: 'Live' },
      { dimension: 'Diagnose', title: 'Situation context', detail: 'Affected services, assets, and active work are shown together.', state: 'Mapped' },
      { dimension: 'Decide', title: 'Recovery actions', detail: 'Recovery candidates are ranked by operational impact and urgency.', state: 'Ready' },
      { dimension: 'Dispatch', title: 'Shift execution', detail: 'Operator and engineer handoffs are visible for shift execution.', state: 'Active' },
      { dimension: 'Document', title: 'Evidence timeline', detail: 'Daily operating evidence is linked to incidents, tasks, and reports.', state: 'Ready' },
      { dimension: 'Deliver', title: 'Daily readiness', detail: 'Readiness quality confirms the shift can close or escalate cleanly.', state: 'Watch' },
    ],
    focusCards: [
      { title: 'Live events', value: '42', detail: 'events grouped into actionable operating signals', tone: 'watch' },
      { title: 'Recovery candidates', value: '8', detail: 'items ready for supervisor review or dispatch', tone: 'risk' },
      { title: 'Stable systems', value: '91%', detail: 'systems without active service degradation', tone: 'good' },
    ],
    heatmap: [
      { label: 'Availability', value: 91, tone: 'good' },
      { label: 'Faults', value: 57, tone: 'risk' },
      { label: 'Workload', value: 70, tone: 'watch' },
      { label: 'Evidence', value: 84, tone: 'good' },
    ],
  },
  'portfolio-operations': {
    persona: 'Portfolio operator',
    subject: 'multi-site portfolio operations',
    commandFocus: 'comparing cross-site risk, SLA exposure, partner performance, and evidence readiness',
    signalLabel: 'Portfolio health',
    signalValue: '84%',
    riskLabel: 'SLA exposure',
    riskValue: '6',
    evidenceLabel: 'Site packs',
    evidenceValue: '21',
    metricLabels: ['Cross-site signal', 'SLA exposure', 'Partner risk', 'Readiness pack'],
    dimensions: [
      { dimension: 'Detect', title: 'Portfolio risk signal', detail: 'Cross-site risks are ranked by operating exposure and service effect.', state: 'Live' },
      { dimension: 'Diagnose', title: 'Site context map', detail: 'Sites, partners, systems, and service tiers are compared in one view.', state: 'Mapped' },
      { dimension: 'Decide', title: 'SLA exposure actions', detail: 'Actions focus on sites with breach, partner, or customer exposure.', state: 'Ready' },
      { dimension: 'Dispatch', title: 'Partner governance', detail: 'Partner owner and support windows are visible before escalation.', state: 'Guarded' },
      { dimension: 'Document', title: 'Portfolio evidence pack', detail: 'Site evidence is grouped for customer and executive reporting.', state: 'Ready' },
      { dimension: 'Deliver', title: 'Portfolio quality gate', detail: 'Readiness quality shows whether all sites are reportable.', state: 'Watch' },
    ],
    focusCards: [
      { title: 'Sites monitored', value: '18', detail: 'active sites in the portfolio operating window', tone: 'good' },
      { title: 'Partner exposure', value: '4', detail: 'partner-owned systems requiring governance review', tone: 'watch' },
      { title: 'Readiness gaps', value: '5', detail: 'site packs missing evidence or owner sign-off', tone: 'risk' },
    ],
    heatmap: [
      { label: 'North', value: 83, tone: 'good' },
      { label: 'South', value: 62, tone: 'watch' },
      { label: 'East', value: 55, tone: 'risk' },
      { label: 'West', value: 74, tone: 'watch' },
    ],
  },
  'industry-view': {
    persona: 'Solution architect',
    subject: 'active industry profile summary',
    commandFocus: 'validating the active industry profile, KPI coverage, scenario risk model, connector readiness, and evidence pack without replacing the full Industry Solutions workspace',
    signalLabel: 'Scenario fit',
    signalValue: '89%',
    riskLabel: 'Model gaps',
    riskValue: '3',
    evidenceLabel: 'Scenario packs',
    evidenceValue: '9',
    metricLabels: ['Industry signal', 'Scenario actions', 'Risk model', 'Readiness pack'],
    dimensions: [
      { dimension: 'Detect', title: 'Profile risk signal', detail: 'The active industry profile highlights scenario risks without acting as the full Industry Solutions page.', state: 'Live' },
      { dimension: 'Diagnose', title: 'Profile context', detail: 'Scenario, KPI, SLA, connector, and report assumptions are summarized for decision review.', state: 'Mapped' },
      { dimension: 'Decide', title: 'KPI readiness actions', detail: 'KPI gaps are surfaced as review entries before users open the full industry package.', state: 'Ready' },
      { dimension: 'Dispatch', title: 'Profile governance', detail: 'Scenario profile owners and approval requirements are visible.', state: 'Guarded' },
      { dimension: 'Document', title: 'Industry evidence pack', detail: 'Industry evidence is ready for sales, architecture, and customer review.', state: 'Ready' },
      { dimension: 'Deliver', title: 'Scenario readiness', detail: 'Readiness quality confirms whether the industry view is GA-presentable.', state: 'Watch' },
    ],
    focusCards: [
      { title: 'Active packages', value: '7', detail: 'industry packages available for current customer context', tone: 'good' },
      { title: 'KPI gaps', value: '3', detail: 'KPIs requiring configuration or evidence alignment', tone: 'watch' },
      { title: 'Connector fit', value: '92%', detail: 'industry connector coverage for selected scenario', tone: 'good' },
    ],
    heatmap: [
      { label: 'Building', value: 88, tone: 'good' },
      { label: 'Airport', value: 76, tone: 'good' },
      { label: 'Data Center', value: 69, tone: 'watch' },
      { label: 'Industrial', value: 61, tone: 'watch' },
    ],
  },
  'customer-success': {
    persona: 'Customer success manager',
    subject: 'customer delivery success',
    commandFocus: 'tracking customer health, acceptance workflow, open risks, milestone evidence, and success readiness',
    signalLabel: 'Customer health',
    signalValue: '86%',
    riskLabel: 'Open risks',
    riskValue: '8',
    evidenceLabel: 'Acceptance packs',
    evidenceValue: '15',
    metricLabels: ['Health signal', 'Acceptance action', 'Risk governance', 'Success pack'],
    dimensions: [
      { dimension: 'Detect', title: 'Customer health signal', detail: 'Customer-visible risk is separated from internal operational backlog.', state: 'Live' },
      { dimension: 'Diagnose', title: 'Milestone context', detail: 'Delivery milestones, acceptance criteria, and evidence needs are aligned.', state: 'Mapped' },
      { dimension: 'Decide', title: 'Acceptance actions', detail: 'Actions focus on handoff blockers and customer success criteria.', state: 'Ready' },
      { dimension: 'Dispatch', title: 'Customer governance', detail: 'Owners, approvals, and customer touchpoints are ready for review.', state: 'Guarded' },
      { dimension: 'Document', title: 'Customer evidence pack', detail: 'Evidence is shaped for customer handoff and sign-off.', state: 'Ready' },
      { dimension: 'Deliver', title: 'Success readiness', detail: 'Readiness quality confirms whether customer preview can proceed.', state: 'Watch' },
    ],
    focusCards: [
      { title: 'Milestones ready', value: '10', detail: 'milestones with sufficient acceptance evidence', tone: 'good' },
      { title: 'Customer blockers', value: '4', detail: 'open blockers requiring owner or evidence closure', tone: 'risk' },
      { title: 'Handoff quality', value: '82%', detail: 'handoff completeness across delivery artifacts', tone: 'watch' },
    ],
    heatmap: [
      { label: 'Acceptance', value: 80, tone: 'good' },
      { label: 'Evidence', value: 72, tone: 'watch' },
      { label: 'Open risk', value: 54, tone: 'risk' },
      { label: 'Success', value: 86, tone: 'good' },
    ],
  },
  'service-risk': {
    persona: 'Service owner',
    subject: 'service risk management',
    commandFocus: 'prioritizing customer impact, SLA mitigation, risk ownership, service evidence, and recovery readiness',
    signalLabel: 'Service posture',
    signalValue: '79%',
    riskLabel: 'High risk',
    riskValue: '6',
    evidenceLabel: 'Risk evidence',
    evidenceValue: '17',
    metricLabels: ['Service signal', 'Mitigation action', 'Risk owner', 'Recovery gate'],
    dimensions: [
      { dimension: 'Detect', title: 'Service risk signal', detail: 'Service risk is ranked by customer impact, SLA exposure, and recovery urgency.', state: 'Live' },
      { dimension: 'Diagnose', title: 'Impact context', detail: 'Customer, asset, system, and partner relationships are visible together.', state: 'Mapped' },
      { dimension: 'Decide', title: 'Mitigation actions', detail: 'Mitigation actions are grouped by effect and time-to-recover.', state: 'Ready' },
      { dimension: 'Dispatch', title: 'Risk ownership', detail: 'Risk owners and escalation policies are visible before action.', state: 'Guarded' },
      { dimension: 'Document', title: 'Service evidence', detail: 'Service risk evidence is prepared for audit and customer explanation.', state: 'Ready' },
      { dimension: 'Deliver', title: 'Recovery readiness', detail: 'Readiness quality confirms if risk can be closed or escalated.', state: 'Watch' },
    ],
    focusCards: [
      { title: 'SLA risks', value: '6', detail: 'service risks with measurable SLA exposure', tone: 'risk' },
      { title: 'Mitigation ready', value: '11', detail: 'actions ready for owner review or dispatch', tone: 'good' },
      { title: 'Evidence gaps', value: '3', detail: 'risks missing customer-ready evidence', tone: 'watch' },
    ],
    heatmap: [
      { label: 'SLA', value: 49, tone: 'risk' },
      { label: 'Customer', value: 66, tone: 'watch' },
      { label: 'Owner', value: 77, tone: 'good' },
      { label: 'Recovery', value: 71, tone: 'watch' },
    ],
  },
  'partner-system-status': {
    persona: 'Integration manager',
    subject: 'partner system status',
    commandFocus: 'monitoring connected systems, data freshness, partner SLA governance, integration evidence, and readiness quality',
    signalLabel: 'Partner health',
    signalValue: '91%',
    riskLabel: 'Freshness issues',
    riskValue: '5',
    evidenceLabel: 'Partner packs',
    evidenceValue: '13',
    metricLabels: ['Partner signal', 'Freshness action', 'SLA governance', 'Integration pack'],
    dimensions: [
      { dimension: 'Detect', title: 'Partner system signal', detail: 'Partner risks are surfaced by connectivity, data freshness, and SLA exposure.', state: 'Live' },
      { dimension: 'Diagnose', title: 'Connected context', detail: 'Systems, connectors, owners, and data contracts are mapped together.', state: 'Mapped' },
      { dimension: 'Decide', title: 'Freshness actions', detail: 'Actions focus on stale data, queue delay, and failed handoff.', state: 'Ready' },
      { dimension: 'Dispatch', title: 'Partner governance', detail: 'Partner owners, access policies, and SLA review paths are visible.', state: 'Guarded' },
      { dimension: 'Document', title: 'Partner evidence pack', detail: 'Integration evidence is prepared for partner and customer review.', state: 'Ready' },
      { dimension: 'Deliver', title: 'Integration readiness', detail: 'Readiness quality confirms whether partner data can support operations.', state: 'Watch' },
    ],
    focusCards: [
      { title: 'Connected systems', value: '26', detail: 'active partner and source systems under observation', tone: 'good' },
      { title: 'Data delays', value: '5', detail: 'systems with freshness or queue delay exposure', tone: 'watch' },
      { title: 'SLA exceptions', value: '2', detail: 'partner status items requiring governance escalation', tone: 'risk' },
    ],
    heatmap: [
      { label: 'Freshness', value: 74, tone: 'watch' },
      { label: 'Connectivity', value: 91, tone: 'good' },
      { label: 'SLA', value: 65, tone: 'watch' },
      { label: 'Evidence', value: 83, tone: 'good' },
    ],
  },
  'delivery-readiness': {
    persona: 'Delivery lead',
    subject: 'release and delivery readiness',
    commandFocus: 'checking release risk, package context, handoff workflow, deployment governance, delivery evidence, and readiness gates',
    signalLabel: 'Release readiness',
    signalValue: '87%',
    riskLabel: 'Gate issues',
    riskValue: '4',
    evidenceLabel: 'Delivery packs',
    evidenceValue: '10',
    metricLabels: ['Release signal', 'Handoff action', 'Gate governance', 'Delivery pack'],
    dimensions: [
      { dimension: 'Detect', title: 'Release risk signal', detail: 'Release blockers are ranked by customer impact and package readiness.', state: 'Live' },
      { dimension: 'Diagnose', title: 'Package context', detail: 'Build, evidence, handoff, and acceptance context are visible together.', state: 'Mapped' },
      { dimension: 'Decide', title: 'Handoff actions', detail: 'Handoff actions focus on readiness gaps and approval requirements.', state: 'Ready' },
      { dimension: 'Dispatch', title: 'Deployment governance', detail: 'Approval status and execution boundaries are visible before release.', state: 'Guarded' },
      { dimension: 'Document', title: 'Delivery evidence', detail: 'Delivery evidence is packaged for customer and supervisor review.', state: 'Ready' },
      { dimension: 'Deliver', title: 'Readiness gate', detail: 'Readiness quality confirms whether delivery can proceed.', state: 'Watch' },
    ],
    focusCards: [
      { title: 'Ready packages', value: '8', detail: 'packages with evidence and handoff criteria satisfied', tone: 'good' },
      { title: 'Approval gaps', value: '4', detail: 'items requiring governance or delivery owner review', tone: 'risk' },
      { title: 'Customer handoffs', value: '6', detail: 'handoffs ready for preview or acceptance planning', tone: 'watch' },
    ],
    heatmap: [
      { label: 'Package', value: 87, tone: 'good' },
      { label: 'Approval', value: 59, tone: 'risk' },
      { label: 'Evidence', value: 81, tone: 'good' },
      { label: 'Handoff', value: 73, tone: 'watch' },
    ],
  },
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

function dashboardProfileFor(l2Id: string): DashboardWorkbenchProfile | undefined {
  return DASHBOARD_WORKBENCH_PROFILES[l2Id]
}

const DASHBOARD_CONTENT_TABS = [
  'Enterprise Overview',
  'Operations Overview',
  'Service Impact View',
  'Spatial Risk View',
  'Partner Health View',
  'Delivery Readiness',
  '7-layer Readiness',
]

const WORKSPACE_OVERVIEW_TABS = ['Priority Signal', 'Role Context', 'Action Queue', 'Readiness Gate', 'Evidence Pack', 'Governance Audit']

const WORKSPACE_OVERVIEW_CONNECTED_WORKSPACES = [
  'Work Management',
  'Assets & Locations',
  'Faults & Events',
  'Reports & Documents',
  'Energy & Sustainability',
  'Governance & Security',
]

const WORKSPACE_OVERVIEW_SECTIONS: Record<string, WorkspaceOverviewSectionConfig> = {
  'Workspace Risk Signal': {
    displayLabel: 'Priority Signal',
    title: 'Role Priority Signal',
    subtitle: "Prioritizes today's workspace by service risk, assigned actions, evidence gaps, and governance readiness.",
    primaryAction: 'Open Priority Workbench',
  },
  'Role Workspace Context': {
    displayLabel: 'Role Context',
    title: 'Role Context',
    subtitle: "Shows the user's operating scope, access boundary, assigned workspaces, and role-specific priorities.",
    primaryAction: 'Open Recommended Workspace',
  },
  'Assigned Workspace Actions': {
    displayLabel: 'Action Queue',
    title: 'Action Queue',
    subtitle: 'Orders assigned actions by customer impact, SLA exposure, and operational urgency.',
    primaryAction: 'Open Action Queue',
  },
  'Workspace Health Readiness': {
    displayLabel: 'Readiness Gate',
    title: 'Readiness Gate',
    subtitle: 'Validates whether the workspace is ready for operational use, customer review, and controlled handoff.',
    primaryAction: 'Open Recommended Workspace',
  },
  'Workspace Evidence Pack': {
    displayLabel: 'Evidence Pack',
    title: 'Evidence Pack',
    subtitle: 'Collects workspace evidence for supervisor review, customer acceptance, export, and audit traceability.',
    primaryAction: 'Export Evidence Pack',
  },
  'Workspace Governance Audit': {
    displayLabel: 'Governance Audit',
    title: 'Governance Audit',
    subtitle: 'Confirms owner, permission, approval, SLA, audit, export, and review controls for this workspace.',
    primaryAction: 'Open Governance Audit',
  },
}

function workspaceOverviewDisplayTabs(activeSection: string): Array<{ key: string; label: string; active: boolean }> {
  return Object.entries(WORKSPACE_OVERVIEW_SECTIONS).map(([key, section]) => ({
    key,
    label: section.displayLabel,
    active: key === activeSection,
  }))
}

function dashboardDisplayTabs(context: L3ContentContext, section: string): Array<{ key: string; label: string; active: boolean }> {
  if (context.l2Id === 'workspace-overview') {
    return workspaceOverviewDisplayTabs(section)
  }

  return DASHBOARD_CONTENT_TABS.map((label) => ({
    key: label,
    label,
    active: label === section,
  }))
}

const DASHBOARD_VISUAL_TYPES: Record<string, DashboardVisualType> = {
  'workspace-overview': 'workspace-priority-board',
  'dashboard-executive': 'executive-risk-board',
  'dashboard-operations': 'live-operations-board',
  'portfolio-operations': 'portfolio-scorecard',
  'industry-view': 'industry-profile-map',
  'customer-success': 'value-realization-scorecard',
  'service-risk': 'service-risk-board',
  'partner-system-status': 'partner-health-map',
  'delivery-readiness': 'readiness-checklist-board',
}

const DASHBOARD_ACTIONS: Record<string, string[]> = {
  'workspace-overview': ['Open Priority Workbench', 'Open Recommended Workspace', 'Open Action Queue', 'Export Evidence Pack', 'Open Governance Audit'],
  'dashboard-executive': ['Approve escalation', 'Request evidence', 'Open service risk', 'Export executive pack'],
  'dashboard-operations': ['Open command center', 'Create work order', 'Escalate', 'Open dispatch queue'],
  'portfolio-operations': ['Compare sites', 'Open site detail', 'Export portfolio report', 'Prepare executive portfolio pack'],
  'industry-view': ['Open industry solution', 'Review profile readiness', 'Export industry evidence', 'Open required connectors'],
  'customer-success': ['Export value report', 'Prepare renewal pack', 'Open delivery center', 'Export executive value pack'],
  'service-risk': ['Open command center', 'Mitigate risk', 'Export risk evidence', 'Open asset 360'],
  'partner-system-status': ['Open integration health', 'Run connectivity check', 'Escalate partner', 'Export partner evidence'],
  'delivery-readiness': ['Open handover package', 'Export evidence bundle', 'Request rework', 'Prepare acceptance'],
}

const DASHBOARD_CONTEXT_ROWS: Record<string, Array<{ label: string; value: string; note: string }>> = {
  'workspace-overview': [
    { label: 'Assigned Site', value: 'Singapore Portfolio Site A', note: 'Role Workspace View' },
    { label: 'Assigned Space', value: 'Level 3 public zone', note: 'Assigned Workspaces' },
    { label: 'Assigned System', value: 'Airside HVAC system', note: 'Workspace Health' },
    { label: 'Assigned Asset', value: 'AHU-B2-14', note: 'Recommended Workspaces' },
    { label: 'Related Point', value: 'TEMP_SUPPLY_AHU_B2_14', note: 'Role Access Status' },
    { label: 'Related Tag', value: 'comfort.priority.watch', note: 'Pending Approvals' },
    { label: 'Source System', value: 'VANTARIS ONE Workspace Registry', note: 'Recent Actions' },
    { label: 'Related Work Order', value: 'WO-24891', note: 'Missing Evidence' },
    { label: 'Evidence Object', value: 'EV-WS-0921', note: 'Workspace Summary' },
    { label: 'Export Object', value: 'EXP-WS-SUMMARY', note: 'Customer Acceptance ready' },
    { label: 'Latest Evidence Update', value: '2026-06-26 09:40', note: 'Evidence Pack freshness' },
    { label: 'Partner System', value: 'Partner CMMS feed', note: 'Telemetry inherited from IBMS' },
  ],
  'dashboard-executive': [
    { label: 'Affected Space', value: 'Executive portfolio', note: 'Customer-facing Risk' },
    { label: 'Affected Zone', value: 'East campus zone', note: 'SLA Exposure' },
    { label: 'Affected System', value: 'Chilled water plant', note: 'Business Continuity Risk' },
    { label: 'Affected Asset', value: 'CHWP-03', note: 'Decision Required' },
    { label: 'Related Point', value: 'CHWP03_STATUS', note: 'Critical Risk' },
    { label: 'Related Tag', value: 'sla.customer.visible', note: 'Customer Impact' },
    { label: 'Source System', value: 'Executive Decision Log', note: 'Portfolio Health' },
    { label: 'Related Event', value: 'EVT-77102', note: 'Latest Evidence Update' },
    { label: 'Evidence Object', value: 'EV-EXEC-4408', note: 'Executive Evidence Pack' },
    { label: 'Export Object', value: 'EXP-EXEC-PACK', note: 'Customer Acceptance ready' },
    { label: 'Partner System', value: 'Customer reporting portal', note: 'Executive pack destination' },
  ],
  'dashboard-operations': [
    { label: 'Affected Space', value: 'Level 3 public zone', note: 'Live Situation' },
    { label: 'Affected Zone', value: 'Retail atrium', note: 'Operational Load' },
    { label: 'Affected System', value: 'BMS airside network', note: 'System Availability' },
    { label: 'Affected Asset', value: 'VAV-L3-27', note: 'Fault Impact' },
    { label: 'Related Point', value: 'VAV27_DAMPER_POS', note: 'Telemetry Delayed' },
    { label: 'Related Tag', value: 'ops.dispatch.required', note: 'Field Team Capacity' },
    { label: 'Source System', value: 'Alarm and fault intake', note: 'Live Events' },
    { label: 'Related Fault', value: 'FLT-10433', note: 'Unassigned Faults' },
    { label: 'Related Work Order', value: 'WO-25018', note: 'Open Dispatches' },
    { label: 'Evidence Object', value: 'EV-OPS-1184', note: 'Operations Evidence Timeline' },
    { label: 'Export Object', value: 'EXP-DAILY-OPS', note: 'Daily readiness report' },
  ],
  'portfolio-operations': [
    { label: 'Affected Space', value: 'Multi-site portfolio', note: 'Portfolio Health' },
    { label: 'Affected Zone', value: 'South region', note: 'Worst Performing Site' },
    { label: 'Affected System', value: 'Common HVAC fault group', note: 'Cross-site Common Faults' },
    { label: 'Affected Asset', value: 'AHU fleet group', note: 'Energy Benchmark' },
    { label: 'Related Point', value: 'AHU_SUPPLY_TEMP_AVG', note: 'Site Benchmark' },
    { label: 'Related Tag', value: 'portfolio.sla.exposure', note: 'Highest SLA Exposure' },
    { label: 'Source System', value: 'Portfolio Operations Registry', note: 'Cross-site Risk' },
    { label: 'Evidence Object', value: 'EV-PORT-2217', note: 'Portfolio Evidence' },
    { label: 'Export Object', value: 'EXP-PORTFOLIO-PACK', note: 'Executive Portfolio Pack' },
    { label: 'Partner System', value: 'Regional service partner', note: 'Partner Exposure' },
  ],
  'industry-view': [
    { label: 'Affected Space', value: 'Industry solution workspace', note: 'Current Industry Profile' },
    { label: 'Affected Zone', value: 'Commercial Building package', note: 'Supported industry examples' },
    { label: 'Affected System', value: 'Required connector set', note: 'Industry Connector Status' },
    { label: 'Affected Asset', value: 'Package template asset', note: 'Industry KPI Coverage' },
    { label: 'Related Point', value: 'industry.kpi.coverage', note: 'Industry Risk Model' },
    { label: 'Related Tag', value: 'industry.profile.active', note: 'Active Industry Profile' },
    { label: 'Source System', value: 'Industry Package Manager', note: 'Enabled Industry Package' },
    { label: 'Evidence Object', value: 'EV-IND-3201', note: 'Industry Evidence Readiness' },
    { label: 'Export Object', value: 'EXP-INDUSTRY-EVIDENCE', note: 'Industry Evidence Pack' },
    { label: 'Partner System', value: 'Connector marketplace', note: 'Required Connectors' },
  ],
  'customer-success': [
    { label: 'Affected Space', value: 'Customer delivery workspace', note: 'Customer Health' },
    { label: 'Affected Zone', value: 'Acceptance phase', note: 'Delivery Milestones' },
    { label: 'Affected System', value: 'Value realization tracker', note: 'Downtime Avoided' },
    { label: 'Affected Asset', value: 'Customer value pack', note: 'Energy Savings' },
    { label: 'Related Point', value: 'roi.energy.saving', note: 'SLA Improvement' },
    { label: 'Related Tag', value: 'renewal.readiness.watch', note: 'Renewal Readiness' },
    { label: 'Source System', value: 'Customer Success Registry', note: 'Acceptance Flow' },
    { label: 'Evidence Object', value: 'EV-CUST-7780', note: 'Customer Evidence' },
    { label: 'Export Object', value: 'EXP-VALUE-PACK', note: 'Executive Value Pack' },
    { label: 'Partner System', value: 'Customer portal', note: 'Expansion Opportunity' },
  ],
  'service-risk': [
    { label: 'Affected Space', value: 'Tenant comfort zone', note: 'Affected Space' },
    { label: 'Affected Zone', value: 'Tower B level 12', note: 'Affected Zone' },
    { label: 'Affected System', value: 'Airside HVAC system', note: 'Affected System' },
    { label: 'Affected Asset', value: 'AHU-B12-02', note: 'Affected Asset' },
    { label: 'Related Point', value: 'AHU_B12_SUPPLY_TEMP', note: 'Related Point / Tag' },
    { label: 'Related Tag', value: 'service.customer.impact', note: 'Customer Impact' },
    { label: 'Source System', value: 'Service Risk Board', note: 'Service Risk Board' },
    { label: 'Related Fault', value: 'FLT-11821', note: 'Related Fault' },
    { label: 'Related Work Order', value: 'WO-25844', note: 'Open Work Order' },
    { label: 'Evidence Object', value: 'EV-RISK-8820', note: 'Risk Evidence' },
    { label: 'Export Object', value: 'EXP-RISK-EVIDENCE', note: 'Latest Evidence' },
  ],
  'partner-system-status': [
    { label: 'Affected Space', value: 'Integration operations', note: 'Connected Systems' },
    { label: 'Affected Zone', value: 'Partner data lane', note: 'Oldest Data Source' },
    { label: 'Affected System', value: 'API event exchange', note: 'API Failure Rate' },
    { label: 'Affected Asset', value: 'Connector-OPCUA-07', note: 'Failed Connector' },
    { label: 'Related Point', value: 'api.failure.rate', note: 'Data Freshness' },
    { label: 'Related Tag', value: 'credential.expiry.risk', note: 'Credential Expiry Risk' },
    { label: 'Source System', value: 'Data Contract Registry', note: 'Data Contract Status' },
    { label: 'Evidence Object', value: 'EV-PARTNER-6004', note: 'Integration Evidence' },
    { label: 'Export Object', value: 'EXP-PARTNER-EVIDENCE', note: 'Partner Evidence' },
    { label: 'Partner System', value: 'Partner CMMS API', note: 'Partner Owner / Technical Owner' },
  ],
  'delivery-readiness': [
    { label: 'Affected Space', value: 'Customer handover workspace', note: 'Readiness Summary' },
    { label: 'Affected Zone', value: 'Acceptance package', note: 'Handoff Checklist' },
    { label: 'Affected System', value: 'Release evidence chain', note: 'Package Status' },
    { label: 'Affected Asset', value: 'Deployment evidence pack', note: 'Deployment Evidence' },
    { label: 'Related Point', value: 'readiness.evidence.coverage', note: 'Missing Evidence' },
    { label: 'Related Tag', value: 'signoff.pending', note: 'Pending Sign-off' },
    { label: 'Source System', value: 'Delivery Readiness Gate', note: 'Release Risk' },
    { label: 'Evidence Object', value: 'EV-DELIVERY-5019', note: 'Delivery Evidence' },
    { label: 'Export Object', value: 'EXP-ACCEPTANCE-PACK', note: 'Export Package Status' },
    { label: 'Partner System', value: 'Customer acceptance portal', note: 'Customer Acceptance Owner' },
  ],
}

function dashboardSignalCards(l2Id: string, profile: DashboardWorkbenchProfile): DashboardWorkbenchConfig['signalCards'] {
  const common: DashboardWorkbenchConfig['signalCards'] = [
    { label: 'Critical Alerts', value: profile.riskValue, note: profile.riskLabel, severity: profile.riskValue === '2' || profile.riskValue === '3' ? 'watch' : 'risk', icon: 'alert' },
    { label: 'SLA Risk', value: l2Id === 'service-risk' ? 'High' : 'Watch', note: 'SLA pressure entry', severity: l2Id === 'service-risk' ? 'risk' : 'watch', icon: 'sla' },
    { label: 'Open Work Orders', value: l2Id === 'dashboard-operations' ? '18' : '9', note: 'Work pressure entry', severity: 'watch', icon: 'work' },
    { label: 'Evidence Readiness', value: profile.signalValue, note: profile.evidenceLabel, severity: 'good', icon: 'evidence' },
    { label: 'Average Asset Health', value: l2Id === 'service-risk' ? '71%' : '86%', note: 'IBMS site/system/asset/point/tag inheritance', severity: l2Id === 'service-risk' ? 'watch' : 'good', icon: 'asset' },
  ]

  const specific: Record<string, DashboardWorkbenchConfig['signalCards']> = {
    'workspace-overview': [
      { label: 'Workspace Health', value: '92%', note: 'Role scope ready', severity: 'good', icon: 'health' },
      { label: 'Assigned Actions', value: '7', note: '3 due today', severity: 'watch', icon: 'action' },
      { label: 'Evidence Readiness', value: '18 / 21', note: '3 missing', severity: 'watch', icon: 'evidence' },
      { label: 'Readiness Gate', value: 'Mapped', note: 'Access and workflow aligned', severity: 'good', icon: 'gate' },
      { label: 'Pending Approvals', value: '4', note: 'Supervisor review required', severity: 'watch', icon: 'approval' },
      { label: 'Role Access Status', value: 'Allowed', note: 'Permission guard passed', severity: 'good', icon: 'access' },
      { label: 'SLA Due Soon', value: '3', note: 'Operations Engineer attention', severity: 'risk', icon: 'sla' },
      { label: 'Closure Evidence Missing', value: '2', note: 'Maintenance Engineer follow-up', severity: 'watch', icon: 'closure' },
    ],
    'dashboard-executive': [
      { label: 'Customer Impact', value: '9', note: 'Customer-facing Risk', severity: 'risk', icon: 'customer' },
      { label: 'Decision Required', value: '5', note: 'Executive Decision Log', severity: 'risk', icon: 'decision' },
      { label: 'Portfolio Health', value: '88%', note: 'Business Continuity Risk', severity: 'good', icon: 'portfolio' },
    ],
    'dashboard-operations': [
      { label: 'Live Events', value: '42', note: 'Current risk', severity: 'watch', icon: 'event' },
      { label: 'Unassigned Faults', value: '8', note: 'Recommended action required', severity: 'risk', icon: 'fault' },
      { label: 'Telemetry Delayed', value: '6', note: 'Data state pressure', severity: 'watch', icon: 'telemetry' },
    ],
    'portfolio-operations': [
      { label: 'Cross-site Risk', value: '11', note: 'Worst Performing Site', severity: 'watch', icon: 'site' },
      { label: 'Energy Benchmark', value: '82%', note: 'Best Performing Site comparison', severity: 'good', icon: 'energy' },
      { label: 'Expansion Opportunity', value: '4', note: 'Sales / Presales signal', severity: 'good', icon: 'value' },
    ],
    'industry-view': [
      { label: 'Active Industry Profile', value: '7', note: 'Commercial Building / Airport / Data Center ready', severity: 'good', icon: 'industry' },
      { label: 'Industry KPI Coverage', value: '89%', note: 'Industry Risk Model coverage', severity: 'good', icon: 'kpi' },
      { label: 'Industry Connector Status', value: 'Watch', note: 'Required Connectors', severity: 'watch', icon: 'connector' },
    ],
    'customer-success': [
      { label: 'Value Realization', value: '$420k', note: 'Commercial value / ROI', severity: 'good', icon: 'value' },
      { label: 'Renewal Readiness', value: '82%', note: 'Renewal and expansion workspace', severity: 'good', icon: 'renewal' },
      { label: 'Acceptance Flow', value: 'Watch', note: 'Evidence Completeness', severity: 'watch', icon: 'acceptance' },
    ],
    'service-risk': [
      { label: 'Impacted Services', value: '6', note: 'Who or what is impacted', severity: 'risk', icon: 'service' },
      { label: 'Mitigation Status', value: 'Active', note: 'Mitigation Owner assigned', severity: 'watch', icon: 'mitigation' },
      { label: 'Risk Evidence', value: '17', note: 'Latest Evidence', severity: 'good', icon: 'risk' },
    ],
    'partner-system-status': [
      { label: 'Connected Systems', value: '26', note: 'Partner and integration health', severity: 'good', icon: 'partner' },
      { label: 'Data Freshness', value: '74%', note: 'Oldest Data Source', severity: 'watch', icon: 'freshness' },
      { label: 'API Failure Rate', value: '1.8%', note: 'Connector Health', severity: 'watch', icon: 'api' },
    ],
    'delivery-readiness': [
      { label: 'Package Status', value: '87%', note: 'Readiness Summary', severity: 'good', icon: 'package' },
      { label: 'Sign-off Status', value: 'Pending', note: 'Customer Acceptance Owner', severity: 'watch', icon: 'signoff' },
      { label: 'Release Risk', value: '4', note: 'Open Handover Risks', severity: 'risk', icon: 'release' },
    ],
  }

  return [...(specific[l2Id] ?? []), ...common].slice(0, 8)
}

function dashboardProductionPanels(section: string, profile: DashboardWorkbenchProfile): DashboardWorkbenchConfig['productionPanels'] {
  if (section in WORKSPACE_OVERVIEW_SECTIONS) {
    return [
      { dimension: 'Pain Point', signal: 'Role-based starting point', detail: 'Users entering a cross-industry operations platform need a clear role-based starting point instead of searching across many L1 domains.', owner: profile.persona },
      { dimension: 'Decision Signal', signal: 'Workspace Health / Assigned Actions / Evidence Readiness', detail: 'Workspace health, assigned actions, due items, evidence gaps, and readiness gate status show what requires attention first.', owner: 'Executive / Supervisor' },
      { dimension: 'Operational Context', signal: 'Assigned Site / Space / System / Asset', detail: 'Role, accessible workspace, assigned site, affected space, related system, asset, point/tag, work order, and evidence object.', owner: 'Operations Engineer' },
      { dimension: 'Action', signal: 'Priority action path', detail: 'Open recommended workspace, review priority actions, prepare evidence handoff, validate readiness gate, or open governance audit.', owner: 'Operations Engineer' },
      { dimension: 'Evidence', signal: 'Evidence Pack / Export Object', detail: 'Workspace activity record, evidence pack, export object, latest evidence update, and handoff package.', owner: 'Customer / Delivery lead' },
      { dimension: 'Governance', signal: 'Permission and approval boundary', detail: 'Owner role, permission guard, SLA rule, approval rule, audit event, export permission, and review cycle.', owner: 'Architect / Governance owner' },
    ]
  }

  return [
    { dimension: 'Pain Point', signal: `${section} operating pressure`, detail: `The page reveals where ${profile.subject} creates customer, operations, or delivery friction.`, owner: profile.persona },
    { dimension: 'Decision Signal', signal: profile.signalLabel, detail: `${profile.signalValue} is treated as the first risk decision layer for the selected Dashboard workspace.`, owner: 'Executive / Supervisor' },
    { dimension: 'Operational Context', signal: 'IBMS inheritance context', detail: 'Affected Space, Affected Zone, Affected System, Affected Asset, Related Point, Related Tag, Source System, Related Fault, Related Event, and Related Work Order are preserved.', owner: 'Operations Engineer' },
    { dimension: 'Action', signal: 'Next action path', detail: 'Actions route the user toward command, work, integration, evidence, governance, or acceptance workspaces without creating new routes.', owner: 'Operations Engineer' },
    { dimension: 'Evidence', signal: 'Evidence Object / Export Object', detail: 'Evidence-driven delivery remains visible for report export, customer review, accountability, and acceptance.', owner: 'Customer / Delivery lead' },
    { dimension: 'Governance', signal: 'Permission and SLA guard', detail: 'Owner role, permission guard, SLA rule, approval rule, review cycle, audit event, and workspace state are explicit.', owner: 'Architect / Governance owner' },
  ]
}

function dashboardReadinessLayers(profile: DashboardWorkbenchProfile): DashboardWorkbenchConfig['readinessLayers'] {
  return [
    { layer: 'Layer 1 Experience / Console', health: profile.signalValue, risk: profile.riskLabel, dataState: 'Live console', owner: 'Customer / Operations Engineer', nextAction: 'Review active workspace', evidence: 'Console Evidence Object', governanceNote: 'Role visibility and workspace state checked' },
    { layer: 'Layer 2 Application Domain', health: '84%', risk: 'Domain gap watch', dataState: 'Mapped domain', owner: 'Product owner', nextAction: 'Confirm domain coverage', evidence: 'Application Domain Evidence', governanceNote: 'Domain ownership recorded' },
    { layer: 'Layer 3 Workflow & Evidence', health: '81%', risk: 'Evidence gap watch', dataState: 'Evidence linked', owner: 'Delivery lead', nextAction: 'Prepare evidence pack', evidence: 'Workflow Evidence Object', governanceNote: 'Audit Event required for export' },
    { layer: 'Layer 4 Intelligence & Semantic', health: '78%', risk: 'Semantic alignment watch', dataState: 'Semantic model mapped', owner: 'Architect', nextAction: 'Review model coverage', evidence: 'Semantic Evidence Object', governanceNote: 'AI Operations Platform governance applies' },
    { layer: 'Layer 5 Integration / Partner', health: '74%', risk: 'Partner data freshness', dataState: 'Partner feed watch', owner: 'Developer / Integration Engineer', nextAction: 'Check connector health', evidence: 'Integration Evidence Object', governanceNote: 'Partner SLA and credential review required' },
    { layer: 'Layer 6 Edge / Runtime', health: '86%', risk: 'Runtime observation only', dataState: 'Read-only telemetry', owner: 'Operations Engineer', nextAction: 'Validate EDGE / LINK signal', evidence: 'Runtime Evidence Object', governanceNote: 'No direct runtime action from Dashboard' },
    { layer: 'Layer 7 Governance / Deployment', health: '82%', risk: 'Approval readiness watch', dataState: 'Governance record ready', owner: 'Executive / Supervisor', nextAction: 'Review approval gate', evidence: 'Deployment Governance Evidence', governanceNote: 'Approval Rule and review cycle enforced' },
  ]
}

function dashboardAcceptanceFooter(l2Id: string, section: string, profile: DashboardWorkbenchProfile): DashboardWorkbenchConfig['acceptanceFooter'] {
  if (l2Id === 'workspace-overview') {
    return [
      { label: 'customerAcceptanceUse', value: 'This workspace can be used for daily supervisor review, customer evidence review, role-based handoff, acceptance readiness verification, and audit-backed export.' },
      { label: 'evidenceObject', value: 'Evidence Object EV-WS-0921 for workspace activity, assigned actions, missing evidence, and latest evidence update' },
      { label: 'exportObject', value: 'Export Object EXP-WS-SUMMARY for customer-facing workspace summary and evidence pack' },
      { label: 'auditEvent', value: 'Audit Event captured for role access, approval boundary, evidence export, and handoff review' },
      { label: 'ownerRole', value: 'Role-based workspace owner: Customer, Operations Engineer, Maintenance Engineer, Executive / Supervisor, Architect, Sales / Presales' },
      { label: 'permissionGuard', value: 'Allowed to proceed when role scope, access boundary, and export permission are aligned' },
      { label: 'slaRule', value: 'SLA due soon and customer-facing service risk are visible before action' },
      { label: 'approvalRule', value: 'Supervisor approval required for escalation, governance audit, and acceptance export' },
      { label: 'reviewCycle', value: 'Daily supervisor review / customer evidence review / weekly readiness verification' },
      { label: 'relatedWorkspaces', value: 'Work Management, Assets & Locations, Faults & Events, Reports & Documents, Energy & Sustainability, Governance & Security' },
      { label: 'dataState', value: 'Data State: live role scope with read-only IBMS inherited site, system, asset, point, tag, work order, and evidence context' },
      { label: 'workspaceState', value: 'Workspace State: GA role-based priority entry, ready for handoff and customer acceptance review' },
    ]
  }

  return [
    { label: 'customerAcceptanceUse', value: `${section} supports Customer Acceptance review, accountability, export, and escalation.` },
    { label: 'evidenceObject', value: `Evidence Object for ${profile.subject}` },
    { label: 'exportObject', value: `Export Object for ${section}` },
    { label: 'auditEvent', value: `Audit Event captured for ${l2Id}` },
    { label: 'ownerRole', value: profile.persona },
    { label: 'permissionGuard', value: 'Dashboard read-only role and workspace permission guard' },
    { label: 'slaRule', value: 'SLA Rule visible where customer or service pressure exists' },
    { label: 'approvalRule', value: 'Approval Rule required for escalation, export, or acceptance package release' },
    { label: 'reviewCycle', value: 'Daily operations review / weekly customer governance review' },
    { label: 'relatedWorkspaces', value: DASHBOARD_DEFAULT_CONNECTED_WORKSPACES.join(', ') },
    { label: 'dataState', value: 'Data State: live, mapped, or watch depending on signal freshness' },
    { label: 'workspaceState', value: 'Workspace State: GA read-only console content, no route or API change' },
  ]
}

function buildDashboardWorkbench(
  context: L3ContentContext,
  section: string,
  profile: DashboardWorkbenchProfile,
  status: string,
): DashboardWorkbenchConfig {
  const workspaceSection = context.l2Id === 'workspace-overview' ? WORKSPACE_OVERVIEW_SECTIONS[section] : undefined

  return {
    breadcrumb: `DASHBOARD / ${context.l2Label.toUpperCase()}`,
    intent: 'Cross-industry operational health overview, first risk decision layer, service impact, SLA pressure, partner health, evidence readiness, and commercial value entry.',
    owner: profile.persona,
    nextStep: workspaceSection?.primaryAction ?? (DASHBOARD_ACTIONS[context.l2Id] ?? ['Open command center'])[0],
    workspaceState: status,
    dataState: context.l2Id === 'partner-system-status' ? 'Data State: partner freshness watch' : 'Data State: live read-only operating signal',
    persona: profile.persona,
    commandFocus: profile.commandFocus,
    signalLabel: profile.signalLabel,
    signalValue: profile.signalValue,
    riskLabel: profile.riskLabel,
    riskValue: profile.riskValue,
    evidenceLabel: profile.evidenceLabel,
    evidenceValue: profile.evidenceValue,
    tabs: context.l2Id === 'workspace-overview' ? WORKSPACE_OVERVIEW_TABS : DASHBOARD_CONTENT_TABS,
    actions: DASHBOARD_ACTIONS[context.l2Id] ?? ['Open command center', 'Export evidence pack'],
    connectedWorkspaces: context.l2Id === 'workspace-overview'
      ? WORKSPACE_OVERVIEW_CONNECTED_WORKSPACES
      : context.l2Id === 'industry-view'
        ? INDUSTRY_VIEW_CONNECTED_WORKSPACES
        : DASHBOARD_DEFAULT_CONNECTED_WORKSPACES,
    signalCards: dashboardSignalCards(context.l2Id, profile),
    visualType: DASHBOARD_VISUAL_TYPES[context.l2Id] ?? 'safe-fallback-board',
    contextRows: DASHBOARD_CONTEXT_ROWS[context.l2Id] ?? DASHBOARD_CONTEXT_ROWS['workspace-overview'],
    productionPanels: dashboardProductionPanels(section, profile),
    lanes: profile.dimensions,
    focusCards: profile.focusCards,
    heatmap: profile.heatmap,
    readinessLayers: dashboardReadinessLayers(profile),
    acceptanceFooter: dashboardAcceptanceFooter(context.l2Id, section, profile),
  }
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
  const dashboardProfile = dashboardProfileFor(context.l2Id)
  const section = context.item.label
  const workspaceSection = context.l2Id === 'workspace-overview' ? WORKSPACE_OVERVIEW_SECTIONS[section] : undefined
  const displaySection = workspaceSection?.displayLabel ?? section
  const isIndustryView = context.l2Id === 'industry-view'
  const mappedModule = context.item.mappedExistingModule ?? context.l2Label
  const status = context.item.status?.replace(/-/g, ' ') ?? 'mapped'

  if (context.l1Label === 'Assets & Locations' && context.l2Id === 'floor-plan-hmi') {
    return {
      title: 'Airport Operational HMI Map',
      subtitle: 'Map-based view of zones, spaces, assets, tags, faults, work orders and evidence for Terminal 3 operations.',
      primaryAction: 'Review readonly projection',
      selectedLabel: section,
      sectionEyebrow: 'Registered base layer',
      l3Tabs: [
        'Equipment Location Risk',
        'Site / Building Context',
        'Zone Overlay Review',
        'Asset Alarm Linkage',
        'Overlay Evidence Review',
        'HMI Map Readiness Gate',
        'Floor Plan Equipment Location',
        'HMI Equipment Locator',
        'Zone-to-Asset Mapping',
        'System-to-Asset Map',
        'Point / Tag Overlay',
        'Fault Location Overlay',
        'Work Order Location Route',
        'Technician Navigation Context',
      ].map((label) => ({
        key: label,
        label,
        active: label === context.item.label,
      })),
      connectedWorkspaces: ['Assets & Locations', 'Faults & Events', 'Work Management', 'Reports & Documents', 'Governance & Security'],
      relatedWorkspaces: ['Assets & Locations', 'Faults & Events', 'Work Management', 'Reports & Documents', 'Governance & Security'],
      metrics: [
        { label: 'Asset Import Readiness', value: 'HOLD_BLOCKED', note: 'Blocked by asset data quality' },
        { label: 'Overlay Status', value: 'blocked_by_data_quality', note: 'Readonly projection' },
        { label: 'Formal Registry Write', value: 'false', note: 'No runtime activation' },
        { label: 'Evidence Closure', value: 'not_ready_due_to_asset_quality_blockers', note: 'Evidence readiness' },
      ],
      rows: [
        { item: 'Zone Summary', focus: 'Zone-level asset grouping for Terminal 3 Ground Floor', status: 'Readonly projection' },
        { item: 'Location Summary', focus: 'Location-level grouping pending customer-approved map conversion', status: 'Pending review' },
        { item: 'Asset Overlay Summary', focus: 'Production-safe asset record projection without formal registry write', status: 'Blocked by asset data quality' },
        { item: 'System Overlay Summary', focus: 'System-to-asset grouping across PA, ACS, CCTV, TEL, IPTV, RAS, and MCS', status: 'Readonly projection' },
        { item: 'Fault Overlay', focus: 'Fault location projection linked to controlled sample events', status: 'Pending asset import clearance' },
        { item: 'Work Order Route', focus: 'Route hints for assigned work orders without formal work order write', status: 'Route hint only' },
        { item: 'Evidence Readiness', focus: 'Closure evidence requirements and audit readiness', status: 'Evidence readiness' },
        { item: 'Import Audit Summary', focus: 'Asset import quality gate summary and confirm disabled state', status: 'HOLD_BLOCKED' },
      ],
    }
  }

  if (context.l1Label === 'Dashboard' && dashboardProfile) {
    return {
      title: isIndustryView ? 'Active Industry Profile' : workspaceSection?.title ?? `${context.l2Label} / ${displaySection}`,
      subtitle: isIndustryView
        ? 'Validates the active industry profile, KPI coverage, scenario risk model, connector readiness, and evidence pack for the selected operating scenario.'
        : workspaceSection?.subtitle ?? `${displaySection} provides a decision-ready view for ${dashboardProfile.subject}, linking risk signals, operational context, recommended action, evidence readiness, and governance controls.`,
      primaryAction: isIndustryView ? 'Review Active Industry Profile' : workspaceSection?.primaryAction ?? `Open ${displaySection} workbench`,
      selectedLabel: isIndustryView ? 'Active Industry Profile' : displaySection,
      sectionEyebrow: context.l2Id === 'workspace-overview' ? 'ROLE PRIORITY ENTRY' : isIndustryView ? 'INDUSTRY DECISION CONTEXT' : 'DASHBOARD DECISION WORKSPACE',
      l3Tabs: dashboardDisplayTabs(context, section),
      connectedWorkspaces: context.l2Id === 'workspace-overview'
        ? WORKSPACE_OVERVIEW_CONNECTED_WORKSPACES
        : isIndustryView
          ? INDUSTRY_VIEW_CONNECTED_WORKSPACES
          : DASHBOARD_DEFAULT_CONNECTED_WORKSPACES,
      relatedWorkspaces: context.l2Id === 'workspace-overview'
        ? WORKSPACE_OVERVIEW_CONNECTED_WORKSPACES
        : isIndustryView
          ? INDUSTRY_VIEW_CONNECTED_WORKSPACES
          : DASHBOARD_DEFAULT_CONNECTED_WORKSPACES,
      metrics: context.l2Id === 'workspace-overview'
        ? [
            { label: 'Workspace Health', value: '92%', note: 'Role scope ready' },
            { label: 'Assigned Actions', value: '7', note: '3 due today' },
            { label: 'Evidence Readiness', value: '18 / 21', note: '3 missing' },
            { label: 'Readiness Gate', value: 'Mapped', note: 'Access and workflow aligned' },
          ]
        : [
            { label: dashboardProfile.metricLabels[0], value: dashboardProfile.signalValue, note: dashboardProfile.signalLabel },
            { label: dashboardProfile.metricLabels[1], value: dashboardProfile.riskValue, note: dashboardProfile.riskLabel },
            { label: dashboardProfile.metricLabels[2], value: dashboardProfile.evidenceValue, note: dashboardProfile.evidenceLabel },
            { label: dashboardProfile.metricLabels[3], value: status, note: dashboardProfile.persona },
          ],
      rows: context.l2Id === 'workspace-overview'
        ? [
            { item: 'Review top assigned service risks', focus: 'Service status, customer impact, SLA due soon, and priority signal', status: 'Open', owner: 'Operations Engineer', priority: 'High', open: 'Open Priority Workbench' },
            { item: 'Confirm action queue ownership', focus: 'Assigned actions, due today, escalation owner, and recommended workspace', status: 'Ready', owner: 'Executive / Supervisor', priority: 'High', open: 'Open Action Queue' },
            { item: 'Prepare evidence handoff package', focus: 'Evidence readiness, missing evidence, customer-facing export, and acceptance package', status: 'Guarded', owner: 'Customer Success Manager', priority: 'Medium', open: 'Export Evidence Pack' },
            { item: 'Validate readiness gate', focus: 'Role access status, workflow alignment, permission guard, and 7-layer readiness', status: 'Mapped', owner: 'Architect', priority: 'Medium', open: 'Open Recommended Workspace' },
            { item: 'Open recommended workspace', focus: 'Work Management, Assets & Locations, Faults & Events, Reports & Documents, Energy & Sustainability, Governance & Security', status: 'Allowed', owner: 'Role-based user', priority: 'Normal', open: 'Open Recommended Workspace' },
            { item: 'Review access and approval boundary', focus: 'Owner role, approval rule, SLA rule, audit event, export permission, and review cycle', status: 'Review', owner: 'Governance owner', priority: 'High', open: 'Open Governance Audit' },
          ]
        : [
            { item: `${displaySection} signal review`, focus: dashboardProfile.commandFocus, status: 'Live' },
            { item: `${displaySection} action alignment`, focus: dashboardProfile.dimensions[2]?.detail ?? profile.operatingFocus, status: 'Ready' },
            { item: `${displaySection} evidence handoff`, focus: dashboardProfile.dimensions[4]?.detail ?? profile.evidenceFocus, status: 'Guarded' },
          ],
      dashboardWorkbench: {
        ...buildDashboardWorkbench(context, section, dashboardProfile, status),
      },
    }
  }

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
