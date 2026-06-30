import { computed, defineComponent, h, type VNodeChild } from 'vue'
import { useRoute } from 'vue-router'
import { resolveL3RouteContentConfig } from '@/services/menu/l3-content-registry'

type MetricCard = {
  label: string
  value: string
  note: string
  tone: string
}

type ActionRow = {
  title: string
  owner: string
  status: string
  priority: string
  route: string
}

type SectionConfig = {
  title: string
  subtitle: string
  metrics: MetricCard[]
  actions: ActionRow[]
  primaryRoute: string
  primaryAction: string
  sectionEyebrow?: string
  connectedWorkspaces?: Array<{ label: string; route: string }>
}

const defaultConnectedWorkspaces = [
  { label: 'Command Center', route: '/console/operations' },
  { label: 'Work Management', route: '/one/umms/workspace' },
  { label: 'Assets & Locations', route: '/assets/topology' },
  { label: 'Faults & Events', route: '/one/airport/alarms-events' },
  { label: 'Data & Intelligence', route: '/one/assets/context' },
  { label: 'Reports & Documents', route: '/reports' },
  { label: 'Governance & Security', route: '/console/operations' },
  { label: 'Integration & Partner Hub', route: '/uedge/setup' },
  { label: 'Industry Solutions', route: '/dashboard' },
  { label: 'Administration', route: '/system' },
]

const defaultMetrics: MetricCard[] = [
  { label: 'Asset Import Readiness', value: 'HOLD_BLOCKED', note: 'Confirm Import: Disabled', tone: '#dc2626' },
  { label: 'Total Asset Records', value: '5,187', note: 'Registered import batch under readonly projection', tone: '#0f766e' },
  { label: 'BLOCKER', value: '2', note: 'blocked_by_data_quality records prevent formal write', tone: '#b91c1c' },
  { label: 'MAJOR', value: '1', note: 'Asset quality issue requires owner review', tone: '#b45309' },
  { label: 'WARNING', value: '7', note: 'Warnings remain before evidence closure', tone: '#2563eb' },
]

const dashboardReadinessRows = [
  { label: 'Airport Map Readiness', value: 'Registered / Pending CAD conversion' },
  { label: 'Fault / Work Order Flow', value: 'Readonly projection active' },
  { label: 'Evidence Closure', value: 'Not ready due to asset quality blockers' },
  { label: 'T3 Ground Floor map registered', value: 'Registered floor-plan source retained for conversion' },
  { label: 'Asset overlay blocked by data quality', value: 'blocked_by_data_quality' },
  { label: 'Formal write disabled', value: 'No runtime activation' },
]

const dashboardDecisionLens = [
  { title: 'Import Gate', detail: 'HOLD_BLOCKED remains active until BLOCKER records are corrected and reviewed.' },
  { title: 'Map Overlay', detail: 'T3 Ground Floor map is registered, with asset overlay blocked by data quality.' },
  { title: 'Runtime Posture', detail: 'Readonly projection active; backend endpoint unavailable for formal write execution.' },
]

const sections: Record<string, SectionConfig> = {
  'portfolio-overview': {
    title: 'Portfolio Overview',
    subtitle: 'Executive view of site portfolio health, customer reporting, operational risk, and delivery readiness.',
    primaryRoute: '/reports',
    primaryAction: 'Open Portfolio Report',
    metrics: [
      { label: 'Sites', value: '12', note: 'Operational sites in the portfolio', tone: '#0f766e' },
      { label: 'Critical Sites', value: '2', note: 'Sites requiring executive attention', tone: '#dc2626' },
      { label: 'Open Risks', value: '9', note: 'Portfolio risks under review', tone: '#b45309' },
      { label: 'Customer Reports', value: '18', note: 'Reports ready for customer review', tone: '#2563eb' },
    ],
    actions: [
      { title: 'Review site portfolio', owner: 'Executive', status: 'Ready', priority: 'High', route: '/reports' },
      { title: 'Open customer delivery view', owner: 'Delivery Lead', status: 'Active', priority: 'High', route: '/customer-delivery' },
      { title: 'Export portfolio report', owner: 'Reports', status: 'Ready', priority: 'Medium', route: '/reports' },
    ],
  },
  'site-health': {
    title: 'Site Health',
    subtitle: 'Health posture across sites, impacted assets, operational evidence, and trend review.',
    primaryRoute: '/assets/topology',
    primaryAction: 'Open Site Health',
    metrics: [
      { label: 'Healthy Sites', value: '8', note: 'Sites operating within target range', tone: '#0f766e' },
      { label: 'Warning Sites', value: '3', note: 'Sites showing degraded indicators', tone: '#b45309' },
      { label: 'Critical Sites', value: '1', note: 'Site requiring immediate review', tone: '#dc2626' },
      { label: 'Health Trend', value: '+4%', note: 'Improvement across the current period', tone: '#2563eb' },
    ],
    actions: [
      { title: 'Review site health', owner: 'Operations', status: 'Active', priority: 'High', route: '/assets/topology' },
      { title: 'Open impacted assets', owner: 'Asset Manager', status: 'Review', priority: 'High', route: '/assets/topology' },
      { title: 'Check site evidence', owner: 'UCDE', status: 'Ready', priority: 'Medium', route: '/ucde/evidence' },
    ],
  },
  'critical-alarms': {
    title: 'Critical Alarms',
    subtitle: 'Critical alarm queue, repeated alarm patterns, acknowledgement posture, and evidence readiness.',
    primaryRoute: '/one/airport/alarms-events',
    primaryAction: 'Open Critical Alarms',
    metrics: [
      { label: 'Critical Alarms', value: '14', note: 'Critical alarms currently under review', tone: '#dc2626' },
      { label: 'Unacknowledged', value: '5', note: 'Critical alarms awaiting acknowledgement', tone: '#b45309' },
      { label: 'Repeated', value: '6', note: 'Repeated critical alarm patterns', tone: '#7c3aed' },
      { label: 'Evidence Linked', value: '11', note: 'Critical alarms with evidence chain', tone: '#2563eb' },
    ],
    actions: [
      { title: 'Review critical alarm queue', owner: 'Operator', status: 'Critical', priority: 'High', route: '/one/airport/alarms-events' },
      { title: 'Check repeated alarm root cause', owner: 'Engineer', status: 'Review', priority: 'High', route: '/one/airport/alarms-events' },
      { title: 'Export alarm evidence', owner: 'UCDE', status: 'Ready', priority: 'Medium', route: '/ucde/evidence' },
    ],
  },
  'open-faults': {
    title: 'Open Faults',
    subtitle: 'Open fault cases by impact, system, maintenance linkage, and evidence status.',
    primaryRoute: '/one/airport/alarms-events',
    primaryAction: 'Open Fault Queue',
    metrics: [
      { label: 'Open Faults', value: '26', note: 'Faults currently open', tone: '#dc2626' },
      { label: 'High Impact', value: '7', note: 'Faults affecting service continuity', tone: '#b45309' },
      { label: 'WO Linked', value: '18', note: 'Faults linked to maintenance work orders', tone: '#0f766e' },
      { label: 'Evidence Ready', value: '21', note: 'Faults with traceable evidence', tone: '#2563eb' },
    ],
    actions: [
      { title: 'Review open fault queue', owner: 'Operator', status: 'Open', priority: 'High', route: '/one/airport/alarms-events' },
      { title: 'Open fault-linked work orders', owner: 'Maintenance', status: 'Active', priority: 'High', route: '/one/umms/workspace' },
      { title: 'Check fault evidence records', owner: 'UCDE', status: 'Ready', priority: 'Medium', route: '/ucde/evidence' },
    ],
  },
  'open-work-orders': {
    title: 'Open Work Orders',
    subtitle: 'Executive maintenance queue view across priority, SLA exposure, assignment, and closure readiness.',
    primaryRoute: '/one/umms/workspace',
    primaryAction: 'Open UMMS',
    metrics: [
      { label: 'Open WOs', value: '42', note: 'Open work orders across the portfolio', tone: '#0f766e' },
      { label: 'Emergency WOs', value: '5', note: 'Emergency work orders needing attention', tone: '#dc2626' },
      { label: 'SLA Risk', value: '7', note: 'Work orders approaching SLA breach', tone: '#b45309' },
      { label: 'Closure Review', value: '8', note: 'Work orders awaiting closure evidence', tone: '#7c3aed' },
    ],
    actions: [
      { title: 'Review open work order queue', owner: 'Maintenance Lead', status: 'Active', priority: 'High', route: '/one/umms/workspace' },
      { title: 'Check emergency work orders', owner: 'Engineer', status: 'Emergency', priority: 'High', route: '/one/umms/workspace' },
      { title: 'Review closure evidence', owner: 'Supervisor', status: 'Review', priority: 'Medium', route: '/ucde/evidence' },
    ],
  },
  'energy-exceptions': {
    title: 'Energy Exceptions',
    subtitle: 'Energy anomalies, load exceptions, meter evidence, and sustainability reporting impact.',
    primaryRoute: '/uesg/sustainability',
    primaryAction: 'Open Energy View',
    metrics: [
      { label: 'Energy Exceptions', value: '13', note: 'Energy records outside operating band', tone: '#b45309' },
      { label: 'High Load Zones', value: '4', note: 'Zones with elevated load profile', tone: '#dc2626' },
      { label: 'Evidence Linked', value: '10', note: 'Exceptions linked to supporting evidence', tone: '#2563eb' },
      { label: 'Report Items', value: '6', note: 'Items ready for sustainability reporting', tone: '#0f766e' },
    ],
    actions: [
      { title: 'Review energy exception queue', owner: 'Energy Manager', status: 'Review', priority: 'High', route: '/uesg/sustainability' },
      { title: 'Open high-load asset context', owner: 'Asset Manager', status: 'Active', priority: 'Medium', route: '/assets/topology' },
      { title: 'Prepare energy exception report', owner: 'Reports', status: 'Ready', priority: 'Medium', route: '/reports' },
    ],
  },
  'esg-snapshot': {
    title: 'ESG Snapshot',
    subtitle: 'Sustainability and compliance snapshot across energy, emissions, evidence, and report readiness.',
    primaryRoute: '/uesg/sustainability',
    primaryAction: 'Open ESG Workspace',
    metrics: [
      { label: 'ESG Signals', value: '24', note: 'Tracked sustainability indicators', tone: '#0f766e' },
      { label: 'Exceptions', value: '5', note: 'Indicators requiring review', tone: '#b45309' },
      { label: 'Evidence Linked', value: '19', note: 'Indicators with evidence chain', tone: '#2563eb' },
      { label: 'Reports Ready', value: '4', note: 'ESG reports ready for review', tone: '#7c3aed' },
    ],
    actions: [
      { title: 'Review ESG snapshot', owner: 'ESG Lead', status: 'Ready', priority: 'Medium', route: '/uesg/sustainability' },
      { title: 'Check energy exceptions', owner: 'Energy Manager', status: 'Review', priority: 'High', route: '/uesg/sustainability' },
      { title: 'Open ESG evidence package', owner: 'UCDE', status: 'Ready', priority: 'Medium', route: '/ucde/evidence' },
    ],
  },
  'service-risk': {
    title: 'Service Risk',
    subtitle: 'Customer service risk view across operational impact, SLA exposure, critical assets, and delivery status.',
    primaryRoute: '/customer-delivery',
    primaryAction: 'Open Service Risk',
    metrics: [
      { label: 'Service Risks', value: '11', note: 'Open service risks under management', tone: '#dc2626' },
      { label: 'Customer Impact', value: '3', note: 'Risks visible to customer outcomes', tone: '#b45309' },
      { label: 'Mitigations', value: '8', note: 'Mitigation actions in progress', tone: '#0f766e' },
      { label: 'Evidence Ready', value: '9', note: 'Risks with traceable evidence', tone: '#2563eb' },
    ],
    actions: [
      { title: 'Review service risk board', owner: 'Delivery Lead', status: 'Active', priority: 'High', route: '/customer-delivery' },
      { title: 'Open impacted customer reports', owner: 'Reports', status: 'Ready', priority: 'High', route: '/reports' },
      { title: 'Check mitigation evidence', owner: 'UCDE', status: 'Ready', priority: 'Medium', route: '/ucde/evidence' },
    ],
  },
  'customer-delivery-view': {
    title: 'Customer Delivery View',
    subtitle: 'Customer-facing delivery progress across packages, reports, evidence, acceptance, and service readiness.',
    primaryRoute: '/customer-delivery',
    primaryAction: 'Open Customer Delivery',
    metrics: [
      { label: 'Delivery Packages', value: '7', note: 'Packages prepared for customer review', tone: '#0f766e' },
      { label: 'Acceptance Items', value: '12', note: 'Items tracked for acceptance', tone: '#2563eb' },
      { label: 'Open Risks', value: '4', note: 'Delivery risks requiring attention', tone: '#dc2626' },
      { label: 'Evidence Packs', value: '10', note: 'Evidence packs ready for handoff', tone: '#7c3aed' },
    ],
    actions: [
      { title: 'Review customer delivery board', owner: 'Delivery Lead', status: 'Active', priority: 'High', route: '/customer-delivery' },
      { title: 'Open acceptance evidence', owner: 'UCDE', status: 'Ready', priority: 'Medium', route: '/ucde/evidence' },
      { title: 'Prepare customer report pack', owner: 'Reports', status: 'Ready', priority: 'Medium', route: '/reports' },
    ],
  },
  'today-s-operations': {
    title: "Today's Operations",
    subtitle: 'Current operating day view across events, tasks, SLA exposure, and completed actions.',
    primaryRoute: '/console/operations',
    primaryAction: 'Open Today Board',
    metrics: [
      { label: 'Today Events', value: '86', note: 'Events captured in the current operating day', tone: '#0f766e' },
      { label: 'Active Tasks', value: '24', note: 'Tasks currently assigned or in progress', tone: '#2563eb' },
      { label: 'SLA Risk', value: '6', note: 'Items requiring SLA attention', tone: '#dc2626' },
      { label: 'Completed Actions', value: '39', note: 'Actions completed today', tone: '#7c3aed' },
    ],
    actions: [
      { title: 'Review today board', owner: 'Operator', status: 'Active', priority: 'High', route: '/console/operations' },
      { title: 'Open active tasks', owner: 'Supervisor', status: 'Open', priority: 'High', route: '/one/umms/workspace' },
      { title: 'Check shift handover', owner: 'Operations Lead', status: 'Ready', priority: 'Medium', route: '/reports' },
    ],
  },
  'live-situation': {
    title: 'Live Situation',
    subtitle: 'Live operational situation view across alarms, systems, faults, work orders, and active response.',
    primaryRoute: '/console/operations',
    primaryAction: 'Open Situation View',
    metrics: [
      { label: 'Live Events', value: '47', note: 'Events active in the live situation view', tone: '#0f766e' },
      { label: 'Critical Signals', value: '8', note: 'Signals requiring immediate review', tone: '#dc2626' },
      { label: 'Active Response', value: '15', note: 'Response actions in progress', tone: '#2563eb' },
      { label: 'Evidence Captured', value: '31', note: 'Evidence records captured for current situation', tone: '#7c3aed' },
    ],
    actions: [
      { title: 'Review live situation queue', owner: 'Operator', status: 'Live', priority: 'High', route: '/console/operations' },
      { title: 'Open active alarm detail', owner: 'Alarm Desk', status: 'Critical', priority: 'High', route: '/one/airport/alarms-events' },
      { title: 'Capture response evidence', owner: 'UCDE', status: 'Active', priority: 'Medium', route: '/ucde/evidence' },
    ],
  },
  'risk-summary': {
    title: 'Risk Summary',
    subtitle: 'Operational risk summary across system availability, faults, maintenance, compliance, and customer impact.',
    primaryRoute: '/reports',
    primaryAction: 'Open Risk Report',
    metrics: [
      { label: 'Open Risks', value: '17', note: 'Risks currently tracked by operations', tone: '#dc2626' },
      { label: 'High Priority', value: '5', note: 'Risks needing senior review', tone: '#b45309' },
      { label: 'Mitigated', value: '9', note: 'Risks with mitigation in place', tone: '#0f766e' },
      { label: 'Evidence Linked', value: '14', note: 'Risks with supporting evidence', tone: '#2563eb' },
    ],
    actions: [
      { title: 'Review operational risk summary', owner: 'Operations Lead', status: 'Review', priority: 'High', route: '/reports' },
      { title: 'Open high priority risk evidence', owner: 'UCDE', status: 'Ready', priority: 'High', route: '/ucde/evidence' },
      { title: 'Check risk-linked work orders', owner: 'Maintenance', status: 'Active', priority: 'Medium', route: '/one/umms/workspace' },
    ],
  },
  'system-availability': {
    title: 'System Availability',
    subtitle: 'Availability status across critical systems, degraded services, downtime exposure, and evidence records.',
    primaryRoute: '/assets/topology',
    primaryAction: 'Open Availability View',
    metrics: [
      { label: 'Available Systems', value: '41', note: 'Systems operating in available state', tone: '#0f766e' },
      { label: 'Degraded Systems', value: '4', note: 'Systems with degraded service', tone: '#b45309' },
      { label: 'Unavailable', value: '1', note: 'System requiring urgent review', tone: '#dc2626' },
      { label: 'Availability Evidence', value: '28', note: 'Evidence records linked to availability', tone: '#2563eb' },
    ],
    actions: [
      { title: 'Review system availability', owner: 'Operations', status: 'Active', priority: 'High', route: '/assets/topology' },
      { title: 'Open degraded system assets', owner: 'Asset Manager', status: 'Review', priority: 'High', route: '/assets/topology' },
      { title: 'Export availability evidence', owner: 'Reports', status: 'Ready', priority: 'Medium', route: '/reports' },
    ],
  },
  'fault-impact': {
    title: 'Fault Impact',
    subtitle: 'Fault impact view across affected assets, customer service exposure, work orders, and evidence trail.',
    primaryRoute: '/one/airport/alarms-events',
    primaryAction: 'Open Fault Impact',
    metrics: [
      { label: 'Impacting Faults', value: '19', note: 'Faults with operational impact', tone: '#dc2626' },
      { label: 'Assets Affected', value: '23', note: 'Assets linked to impacting faults', tone: '#b45309' },
      { label: 'WO Created', value: '12', note: 'Faults converted to work orders', tone: '#0f766e' },
      { label: 'Evidence Linked', value: '17', note: 'Fault impact records with evidence', tone: '#2563eb' },
    ],
    actions: [
      { title: 'Review fault impact board', owner: 'Operator', status: 'Active', priority: 'High', route: '/one/airport/alarms-events' },
      { title: 'Open impacted assets', owner: 'Asset Manager', status: 'Review', priority: 'High', route: '/assets/topology' },
      { title: 'Review fault work orders', owner: 'Maintenance', status: 'Active', priority: 'Medium', route: '/one/umms/workspace' },
    ],
  },
  'maintenance-status': {
    title: 'Maintenance Status',
    subtitle: 'Maintenance operations status across open work orders, preventive plans, assignments, and evidence closure.',
    primaryRoute: '/one/umms/workspace',
    primaryAction: 'Open Maintenance',
    metrics: [
      { label: 'Open WOs', value: '42', note: 'Open maintenance work orders', tone: '#0f766e' },
      { label: 'PM Due', value: '14', note: 'Preventive maintenance due soon', tone: '#2563eb' },
      { label: 'Overdue', value: '3', note: 'Maintenance items past due', tone: '#dc2626' },
      { label: 'Closure Review', value: '8', note: 'Items awaiting closure evidence', tone: '#7c3aed' },
    ],
    actions: [
      { title: 'Review maintenance status', owner: 'Maintenance Lead', status: 'Active', priority: 'High', route: '/one/umms/workspace' },
      { title: 'Open preventive maintenance schedule', owner: 'Planner', status: 'Scheduled', priority: 'Medium', route: '/one/umms/workspace' },
      { title: 'Check work order evidence', owner: 'UCDE', status: 'Ready', priority: 'Medium', route: '/ucde/evidence' },
    ],
  },
  'energy-status': {
    title: 'Energy Status',
    subtitle: 'Energy status across consumption signals, exception queues, sustainability reporting, and evidence coverage.',
    primaryRoute: '/uesg/sustainability',
    primaryAction: 'Open Energy Status',
    metrics: [
      { label: 'Energy Signals', value: '58', note: 'Energy signals under review', tone: '#0f766e' },
      { label: 'Exceptions', value: '13', note: 'Signals outside operating range', tone: '#b45309' },
      { label: 'High Impact', value: '4', note: 'Energy exceptions with high impact', tone: '#dc2626' },
      { label: 'Reports Ready', value: '6', note: 'Energy report items ready', tone: '#2563eb' },
    ],
    actions: [
      { title: 'Review energy status', owner: 'Energy Manager', status: 'Active', priority: 'Medium', route: '/uesg/sustainability' },
      { title: 'Open high-impact energy exceptions', owner: 'Operations', status: 'Review', priority: 'High', route: '/uesg/sustainability' },
      { title: 'Prepare sustainability evidence', owner: 'UCDE', status: 'Ready', priority: 'Medium', route: '/ucde/evidence' },
    ],
  },
  'compliance-status': {
    title: 'Compliance Status',
    subtitle: 'Compliance posture across operational controls, evidence, report readiness, and open review actions.',
    primaryRoute: '/reports',
    primaryAction: 'Open Compliance Reports',
    metrics: [
      { label: 'Controls Tracked', value: '36', note: 'Controls represented in dashboard coverage', tone: '#0f766e' },
      { label: 'Open Reviews', value: '7', note: 'Compliance items awaiting review', tone: '#b45309' },
      { label: 'Evidence Ready', value: '29', note: 'Controls with supporting evidence', tone: '#2563eb' },
      { label: 'Exceptions', value: '3', note: 'Compliance exceptions requiring action', tone: '#dc2626' },
    ],
    actions: [
      { title: 'Review compliance status', owner: 'Compliance Lead', status: 'Review', priority: 'High', route: '/reports' },
      { title: 'Open exception evidence', owner: 'UCDE', status: 'Ready', priority: 'High', route: '/ucde/evidence' },
      { title: 'Prepare compliance report', owner: 'Reports', status: 'Ready', priority: 'Medium', route: '/reports' },
    ],
  },
  'my-tasks': {
    title: 'My Tasks',
    subtitle: 'Priority work assigned to the current operator, including SLA risk, approvals, and evidence follow-up.',
    primaryRoute: '/one/umms/workspace',
    primaryAction: 'Open Work Queue',
    metrics: [
      { label: 'Assigned Tasks', value: '16', note: 'Tasks awaiting owner action', tone: '#0f766e' },
      { label: 'Due Today', value: '9', note: 'Items requiring same-day follow-up', tone: '#2563eb' },
      { label: 'SLA Risk', value: '4', note: 'Escalation required before breach', tone: '#dc2626' },
      { label: 'Evidence Pending', value: '7', note: 'Closure evidence needs review', tone: '#7c3aed' },
    ],
    actions: [
      { title: 'Review SLA risk work orders', owner: 'Supervisor', status: 'At risk', priority: 'High', route: '/one/umms/workspace' },
      { title: 'Approve maintenance closure evidence', owner: 'Engineer', status: 'Pending', priority: 'Medium', route: '/ucde/evidence' },
      { title: 'Check repeated CCTV fault task', owner: 'Operator', status: 'Open', priority: 'High', route: '/one/umms/workspace' },
    ],
  },
  'my-alarms': {
    title: 'My Alarms',
    subtitle: 'Alarm items requiring acknowledgement, prioritisation, escalation, or evidence linkage.',
    primaryRoute: '/one/airport/alarms-events',
    primaryAction: 'Open Alarm Console',
    metrics: [
      { label: 'Active Alarms', value: '31', note: 'Current alarms under review', tone: '#dc2626' },
      { label: 'Critical', value: '6', note: 'Critical operational impact', tone: '#b91c1c' },
      { label: 'Repeated', value: '12', note: 'Potential nuisance or recurring alarms', tone: '#b45309' },
      { label: 'Linked Evidence', value: '24', note: 'Alarm records with evidence trace', tone: '#2563eb' },
    ],
    actions: [
      { title: 'Acknowledge critical BHS alarm', owner: 'Operator', status: 'Critical', priority: 'High', route: '/one/airport/alarms-events' },
      { title: 'Review repeated access control events', owner: 'Security', status: 'Repeated', priority: 'Medium', route: '/one/airport/alarms-events' },
      { title: 'Attach alarm timeline evidence', owner: 'Supervisor', status: 'Evidence', priority: 'Medium', route: '/ucde/evidence' },
    ],
  },
  'my-work-orders': {
    title: 'My Work Orders',
    subtitle: 'Maintenance work orders by assignment, SLA age, asset impact, and closure status.',
    primaryRoute: '/one/umms/workspace',
    primaryAction: 'Open UMMS',
    metrics: [
      { label: 'Open WOs', value: '42', note: 'Open maintenance work orders', tone: '#0f766e' },
      { label: 'Assigned', value: '27', note: 'Assigned to engineer teams', tone: '#2563eb' },
      { label: 'Emergency', value: '5', note: 'Emergency work order queue', tone: '#dc2626' },
      { label: 'Closure Review', value: '8', note: 'Awaiting supervisor closure', tone: '#7c3aed' },
    ],
    actions: [
      { title: 'Dispatch emergency cooling work order', owner: 'Engineer', status: 'Emergency', priority: 'High', route: '/one/umms/workspace' },
      { title: 'Review overdue preventive maintenance', owner: 'Maintenance Lead', status: 'Overdue', priority: 'High', route: '/one/umms/workspace' },
      { title: 'Close evidence-backed corrective WO', owner: 'Supervisor', status: 'Review', priority: 'Medium', route: '/ucde/evidence' },
    ],
  },
  'my-approvals': {
    title: 'My Approvals',
    subtitle: 'Approvals for work order closure, reports, evidence bundles, and operational decisions.',
    primaryRoute: '/ucde/evidence',
    primaryAction: 'Open Evidence Review',
    metrics: [
      { label: 'Pending Approval', value: '11', note: 'Items waiting for approval', tone: '#b45309' },
      { label: 'High Priority', value: '3', note: 'High priority approval items', tone: '#dc2626' },
      { label: 'Report Review', value: '4', note: 'Reports awaiting customer-ready review', tone: '#2563eb' },
      { label: 'Evidence Review', value: '7', note: 'Evidence records awaiting acceptance', tone: '#7c3aed' },
    ],
    actions: [
      { title: 'Approve customer handoff report', owner: 'Admin', status: 'Review', priority: 'High', route: '/reports' },
      { title: 'Approve work order closure evidence', owner: 'Supervisor', status: 'Pending', priority: 'Medium', route: '/ucde/evidence' },
      { title: 'Review AI recommendation evidence', owner: 'Operations Manager', status: 'Pending', priority: 'Medium', route: '/one/nexus-ai/branch-audit' },
    ],
  },
  'my-reports': {
    title: 'My Reports',
    subtitle: 'Customer-ready reports, export packs, compliance summaries, and scheduled report queues.',
    primaryRoute: '/reports',
    primaryAction: 'Open Reports',
    metrics: [
      { label: 'Report Packs', value: '9', note: 'Customer-ready report packs', tone: '#7c3aed' },
      { label: 'Exports Today', value: '6', note: 'Exports prepared today', tone: '#2563eb' },
      { label: 'Compliance Drafts', value: '5', note: 'Compliance report drafts', tone: '#b45309' },
      { label: 'Evidence Bundles', value: '14', note: 'Evidence-linked export bundles', tone: '#0f766e' },
    ],
    actions: [
      { title: 'Open customer handoff package', owner: 'Reports', status: 'Ready', priority: 'Medium', route: '/reports' },
      { title: 'Prepare maintenance monthly report', owner: 'Maintenance', status: 'Draft', priority: 'Medium', route: '/reports' },
      { title: 'Export evidence bundle', owner: 'UCDE', status: 'Ready', priority: 'High', route: '/ucde/evidence' },
    ],
  },
  'my-evidence': {
    title: 'My Evidence',
    subtitle: 'Evidence records linked to alarms, work orders, reports, decisions, and customer acceptance.',
    primaryRoute: '/ucde/evidence',
    primaryAction: 'Open Evidence',
    metrics: [
      { label: 'Evidence Ready', value: '128', note: 'Records ready for review', tone: '#2563eb' },
      { label: 'Pending Linkage', value: '12', note: 'Records needing source linkage', tone: '#b45309' },
      { label: 'Decision Records', value: '18', note: 'Decision evidence records', tone: '#7c3aed' },
      { label: 'Export Ready', value: '22', note: 'Evidence ready for export', tone: '#0f766e' },
    ],
    actions: [
      { title: 'Review fault evidence chain', owner: 'UCDE', status: 'Ready', priority: 'High', route: '/ucde/evidence' },
      { title: 'Link maintenance closure evidence', owner: 'Engineer', status: 'Pending', priority: 'Medium', route: '/ucde/evidence' },
      { title: 'Prepare audit evidence package', owner: 'Admin', status: 'Ready', priority: 'Medium', route: '/reports' },
    ],
  },
  'recent-activity': {
    title: 'Recent Activity',
    subtitle: 'Recent operational events, alarm actions, work order updates, reports, and evidence activity.',
    primaryRoute: '/console/operations',
    primaryAction: 'Open Operations',
    metrics: [
      { label: 'Recent Events', value: '74', note: 'Activity in the latest operating window', tone: '#0f766e' },
      { label: 'Alarm Updates', value: '19', note: 'Alarm activity updates', tone: '#dc2626' },
      { label: 'WO Updates', value: '23', note: 'Work order activity updates', tone: '#2563eb' },
      { label: 'Evidence Updates', value: '12', note: 'Evidence and report updates', tone: '#7c3aed' },
    ],
    actions: [
      { title: 'Operator acknowledged critical alarm', owner: 'Operator', status: 'Completed', priority: 'High', route: '/one/airport/alarms-events' },
      { title: 'Engineer updated corrective work order', owner: 'Engineer', status: 'Updated', priority: 'Medium', route: '/one/umms/workspace' },
      { title: 'Report pack exported for review', owner: 'Reports', status: 'Completed', priority: 'Medium', route: '/reports' },
    ],
  },
  'umms-overview': {
    title: 'UMMS Overview',
    subtitle: 'Maintenance workspace scenario across work orders, preventive maintenance, SLA status, assignments, and evidence.',
    primaryRoute: '/one/umms/workspace',
    primaryAction: 'Open UMMS',
    metrics: [
      { label: 'Open WOs', value: '42', note: 'Open maintenance work orders', tone: '#0f766e' },
      { label: 'Emergency WOs', value: '5', note: 'Emergency work orders under review', tone: '#dc2626' },
      { label: 'PM Due', value: '14', note: 'Preventive maintenance due soon', tone: '#2563eb' },
      { label: 'Closure Review', value: '8', note: 'Work orders awaiting closure review', tone: '#7c3aed' },
    ],
    actions: [
      { title: 'Open UMMS', owner: 'Maintenance Lead', status: 'Active', priority: 'High', route: '/one/umms/workspace' },
      { title: 'Review PM schedule', owner: 'Planner', status: 'Scheduled', priority: 'Medium', route: '/one/umms/workspace' },
      { title: 'Check work order evidence', owner: 'UCDE', status: 'Ready', priority: 'Medium', route: '/ucde/evidence' },
    ],
  },
  'ufms-overview': {
    title: 'UFMS Overview',
    subtitle: 'Fault management scenario across open faults, alarm linkage, impact analysis, and work order conversion.',
    primaryRoute: '/one/airport/alarms-events',
    primaryAction: 'Open UFMS View',
    metrics: [
      { label: 'Open Faults', value: '26', note: 'Faults currently open', tone: '#dc2626' },
      { label: 'Impacting Faults', value: '19', note: 'Faults with operational impact', tone: '#b45309' },
      { label: 'WO Converted', value: '12', note: 'Faults converted to work orders', tone: '#0f766e' },
      { label: 'Evidence Linked', value: '17', note: 'Faults with evidence records', tone: '#2563eb' },
    ],
    actions: [
      { title: 'Review fault queue', owner: 'Operator', status: 'Open', priority: 'High', route: '/one/airport/alarms-events' },
      { title: 'Open fault impact view', owner: 'Supervisor', status: 'Review', priority: 'High', route: '/one/airport/alarms-events' },
      { title: 'Review fault-linked work orders', owner: 'Maintenance', status: 'Active', priority: 'Medium', route: '/one/umms/workspace' },
    ],
  },
  'uesg-overview': {
    title: 'UESG Overview',
    subtitle: 'Sustainability scenario across energy exceptions, ESG indicators, compliance evidence, and reports.',
    primaryRoute: '/uesg/sustainability',
    primaryAction: 'Open UESG',
    metrics: [
      { label: 'ESG Signals', value: '24', note: 'Tracked sustainability indicators', tone: '#0f766e' },
      { label: 'Energy Exceptions', value: '13', note: 'Energy exceptions under review', tone: '#b45309' },
      { label: 'Compliance Items', value: '36', note: 'Controls represented for review', tone: '#2563eb' },
      { label: 'Open Exceptions', value: '3', note: 'Exceptions requiring action', tone: '#dc2626' },
    ],
    actions: [
      { title: 'Open UESG sustainability view', owner: 'ESG Lead', status: 'Active', priority: 'Medium', route: '/uesg/sustainability' },
      { title: 'Review energy exception evidence', owner: 'Energy Manager', status: 'Review', priority: 'High', route: '/ucde/evidence' },
      { title: 'Prepare ESG report', owner: 'Reports', status: 'Ready', priority: 'Medium', route: '/reports' },
    ],
  },
  'airport-scenario': {
    title: 'Airport Scenario',
    subtitle: 'Airport operations scenario across terminal systems, BHS, CCTV, access control, alarms, and maintenance readiness.',
    primaryRoute: '/one/airport/alarms-events',
    primaryAction: 'Open Airport Scenario',
    metrics: [
      { label: 'Terminal Systems', value: '18', note: 'Airport terminal systems represented', tone: '#0f766e' },
      { label: 'BHS Alerts', value: '7', note: 'Baggage handling alerts under review', tone: '#dc2626' },
      { label: 'Security Events', value: '11', note: 'CCTV and access control events', tone: '#b45309' },
      { label: 'WO Linked', value: '9', note: 'Airport events linked to work orders', tone: '#2563eb' },
    ],
    actions: [
      { title: 'Review airport alarm queue', owner: 'Airport Operations', status: 'Active', priority: 'High', route: '/one/airport/alarms-events' },
      { title: 'Open BHS maintenance work orders', owner: 'Maintenance', status: 'Open', priority: 'High', route: '/one/umms/workspace' },
      { title: 'Check airport evidence package', owner: 'UCDE', status: 'Ready', priority: 'Medium', route: '/ucde/evidence' },
    ],
  },
  'data-center-scenario': {
    title: 'Data Center Scenario',
    subtitle: 'Data center operations scenario across power, cooling, UPS, alarms, maintenance, and service risk.',
    primaryRoute: '/assets/topology',
    primaryAction: 'Open Data Center Scenario',
    metrics: [
      { label: 'Critical Assets', value: '22', note: 'Power and cooling assets under coverage', tone: '#0f766e' },
      { label: 'UPS Warnings', value: '4', note: 'UPS indicators requiring review', tone: '#b45309' },
      { label: 'Cooling Risks', value: '5', note: 'Cooling risks under active review', tone: '#dc2626' },
      { label: 'Maintenance Linked', value: '13', note: 'Data center items linked to work orders', tone: '#2563eb' },
    ],
    actions: [
      { title: 'Review data center asset health', owner: 'Data Center Lead', status: 'Active', priority: 'High', route: '/assets/topology' },
      { title: 'Open UPS and cooling work orders', owner: 'Maintenance', status: 'Open', priority: 'High', route: '/one/umms/workspace' },
      { title: 'Prepare data center service report', owner: 'Reports', status: 'Ready', priority: 'Medium', route: '/reports' },
    ],
  },
  'customer-acceptance-flow': {
    title: 'Customer Acceptance Flow',
    subtitle: 'Customer acceptance scenario across delivery packages, evidence, reports, signoff items, and open risks.',
    primaryRoute: '/customer-delivery',
    primaryAction: 'Open Acceptance Flow',
    metrics: [
      { label: 'Acceptance Items', value: '12', note: 'Items tracked for customer acceptance', tone: '#2563eb' },
      { label: 'Evidence Packs', value: '10', note: 'Evidence packs ready for review', tone: '#0f766e' },
      { label: 'Report Packs', value: '7', note: 'Customer reports prepared', tone: '#7c3aed' },
      { label: 'Open Risks', value: '4', note: 'Risks blocking acceptance completion', tone: '#dc2626' },
    ],
    actions: [
      { title: 'Review customer acceptance flow', owner: 'Delivery Lead', status: 'Active', priority: 'High', route: '/customer-delivery' },
      { title: 'Open acceptance evidence bundle', owner: 'UCDE', status: 'Ready', priority: 'Medium', route: '/ucde/evidence' },
      { title: 'Prepare customer signoff report', owner: 'Reports', status: 'Ready', priority: 'High', route: '/reports' },
    ],
  },
}

const defaultSection: SectionConfig = {
  title: 'VANTARIS ONE Operations Dashboard',
  subtitle: 'Production operations dashboard for asset import readiness, airport map registration, readonly fault and work order projection, and evidence closure gating.',
  primaryRoute: '/one/assets/context',
  primaryAction: 'Open Asset Context',
  sectionEyebrow: 'OPERATIONS READINESS',
  connectedWorkspaces: defaultConnectedWorkspaces,
  metrics: defaultMetrics,
  actions: [
    { title: 'Resolve asset import blockers', owner: 'Asset Data Owner', status: 'HOLD_BLOCKED', priority: 'BLOCKER', route: '/one/assets/context' },
    { title: 'Review T3 Ground Floor map registration', owner: 'Airport Operations', status: 'Registered', priority: 'MAJOR', route: '/one/airport/assets-topology' },
    { title: 'Hold confirm import control', owner: 'Governance', status: 'Confirm Import: Disabled', priority: 'BLOCKER', route: '/system/audit-logs' },
    { title: 'Verify readonly fault and work order projection', owner: 'Maintenance Lead', status: 'Readonly projection active', priority: 'WARNING', route: '/one/umms/workspace' },
    { title: 'Prepare evidence closure review', owner: 'Evidence Owner', status: 'Not ready', priority: 'WARNING', route: '/ucde/evidence' },
  ],
}

const panelStyle = {
  background: 'var(--one-color-card, #ffffff)',
  border: '1px solid var(--one-color-border, #d7e3ec)',
  borderRadius: 'var(--one-radius-lg, 14px)',
  boxShadow: 'var(--one-shadow-card, 0 8px 18px rgba(15, 23, 42, 0.035))',
}

function openRoute(path: string): void {
  window.location.assign(path)
}

function card(children: VNodeChild[], extra: Record<string, string> = {}) {
  return h('article', { style: { ...panelStyle, padding: '24px 32px 22px', ...extra } }, children)
}

function keyValueRows(rows: Array<{ label: string; value: string }>) {
  return h('div', { style: { display: 'grid', gap: '10px' } }, rows.map((row) => h('div', {
    style: {
      display: 'grid',
      gridTemplateColumns: 'minmax(180px, .75fr) minmax(0, 1fr)',
      gap: '12px',
      padding: '12px',
      border: '1px solid #dbe7e4',
      borderRadius: '10px',
      background: '#f8fbfa',
      alignItems: 'center',
    },
  }, [
    h('span', { style: { color: '#64748b', fontSize: '12px', fontWeight: '800' } }, row.label),
    h('strong', { style: { color: '#0f172a', fontSize: '13px' } }, row.value),
  ])))
}

function decisionLensPanel() {
  return card([
    h('p', { style: eyebrowStyle }, 'Decision Lens'),
    h('h2', { style: headingStyle }, 'Decision Lens'),
    h('div', { style: { display: 'grid', gap: '12px' } }, dashboardDecisionLens.map((item) => h('div', {
      style: {
        border: '1px solid #f1d3bd',
        padding: '12px 14px',
        background: '#fffaf6',
        borderRadius: '12px',
      },
    }, [
      h('strong', { style: { display: 'block', marginBottom: '4px', color: '#0f172a' } }, item.title),
      h('p', { style: { margin: 0, color: '#52615d', fontSize: '13px', lineHeight: '1.5' } }, item.detail),
    ]))),
  ])
}

function normalizeL3(value: unknown): string {
  if (typeof value !== 'string' || !value) {
    return 'my-tasks'
  }

  if (sections[value]) {
    return value
  }

  const menuGeneratedId = value.replace(/-\d+$/, '')
  return menuGeneratedId
}

export default defineComponent({
  name: 'DashboardPlaceholder',
  setup() {
    const route = useRoute()
    const registrySection = computed<SectionConfig | undefined>(() => {
      const config = resolveL3RouteContentConfig(route.query.menu, route.query.l3)
      return config
        ? {
            title: config.title,
            subtitle: config.subtitle,
            primaryRoute: '/dashboard',
            primaryAction: config.primaryAction,
            sectionEyebrow: config.sectionEyebrow,
            connectedWorkspaces: (config.connectedWorkspaces ?? config.relatedWorkspaces)?.map((label) => ({
              label,
              route: routeForConnectedWorkspace(label),
            })),
            metrics: config.metrics.map((metric, index) => ({
              ...metric,
              tone: ['#0f766e', '#2563eb', '#7c3aed', '#b45309'][index % 4],
            })),
            actions: config.rows.map((row) => ({
              title: row.item,
              owner: row.focus,
              status: row.status,
              priority: row.status === 'Selected' ? 'High' : 'Medium',
              route: '/dashboard',
            })),
          }
        : undefined
    })
    const activeSection = computed(() => {
      if (route.path === '/dashboard' && !route.query.l3 && !route.query.menu) {
        return defaultSection
      }

      return sections[normalizeL3(route.query.l3)] ?? registrySection.value ?? defaultSection
    })
    const isOperationsDashboard = computed(() => activeSection.value.title === defaultSection.title)

    return () => h('section', {
      style: {
        minHeight: '100vh',
        padding: '0 0 28px',
        background: '#eef6fa',
        color: '#10201d',
      },
    }, [
      h('section', { style: { display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: '14px', marginBottom: '16px' } },
        activeSection.value.metrics.map((item) => card([
          h('span', { style: { display: 'block', color: '#64748b', fontSize: '12px', fontWeight: '700', marginBottom: '8px' } }, item.label),
          h('strong', { style: { display: 'block', fontSize: '28px', color: item.tone, marginBottom: '8px' } }, item.value),
          h('p', { style: { margin: 0, color: '#52615d', fontSize: '12px', lineHeight: '1.45' } }, item.note),
        ], { minHeight: '116px' })),
      ),

      h('section', { style: { display: 'grid', gap: '16px', marginBottom: '16px' } }, [
        card([
          h('h3', { style: { ...headingStyle, fontSize: '16px', marginBottom: '10px' } }, 'Action Queue'),
          h('div', { style: { overflowX: 'auto' } }, [
            h('table', { style: { width: '100%', borderCollapse: 'collapse', minWidth: '760px' } }, [
              h('thead', [
                h('tr', [
                  h('th', { style: thStyle }, 'Action'),
                  h('th', { style: thStyle }, 'Owner'),
                  h('th', { style: thStyle }, 'Status'),
                  h('th', { style: thStyle }, 'Priority'),
                  h('th', { style: thStyle }, 'Open'),
                ]),
              ]),
              h('tbody', activeSection.value.actions.map((row) => h('tr', [
                h('td', { style: tdStyle }, row.title),
                h('td', { style: tdStyle }, row.owner),
                h('td', { style: tdStyle }, row.status),
                h('td', { style: tdStyle }, row.priority),
                h('td', { style: tdStyle }, [
                  h('button', { type: 'button', onClick: () => openRoute(row.route), style: smallButtonStyle }, 'Open'),
                ]),
              ]))),
            ]),
          ]),
        ]),

        card([
          h('p', { style: eyebrowStyle }, 'Operational routes'),
          h('h2', { style: headingStyle }, 'Connected Workspaces'),
          h('div', { style: { display: 'grid', gap: '10px' } },
            (activeSection.value.connectedWorkspaces ?? defaultConnectedWorkspaces).map((workspace) => routeButton(workspace.label, workspace.route)),
          ),
        ]),
      ]),

      ...(isOperationsDashboard.value ? [
        h('section', { style: { display: 'grid', gap: '16px' } }, [
          card([
            h('p', { style: eyebrowStyle }, 'Readiness Gate'),
            h('h2', { style: headingStyle }, 'Asset Import and Airport Map Readiness'),
            keyValueRows(dashboardReadinessRows),
          ]),
          decisionLensPanel(),
        ]),
      ] : []),
    ])
  },
})

function routeForConnectedWorkspace(label: string): string {
  const routes: Record<string, string> = {
    'Command Center': '/console/operations',
    'Work Management': '/one/umms/workspace',
    'Assets & Locations': '/assets/topology',
    'Faults & Events': '/one/airport/alarms-events',
    'Reports & Documents': '/reports',
    'Governance & Security': '/console/operations',
    'Integration & Partner Hub': '/uedge/setup',
    'Industry Solutions': '/dashboard',
    'Data & Intelligence': '/one/assets/context',
    Administration: '/system',
  }

  return routes[label] ?? '/dashboard'
}

function routeButton(label: string, route: string) {
  return h('button', {
    type: 'button',
    onClick: () => openRoute(route),
    style: {
      textAlign: 'left',
      border: '1px solid #dbe7e4',
      borderRadius: '12px',
      background: '#f8fbfa',
      padding: '12px',
      cursor: 'pointer',
      color: '#0f172a',
      fontWeight: '700',
    },
  }, label)
}

const eyebrowStyle = {
  margin: '0 0 8px',
  color: '#0f766e',
  fontWeight: '800',
  letterSpacing: '.08em',
  textTransform: 'uppercase',
  fontSize: '11px',
}

const headingStyle = {
  margin: '0 0 8px',
  fontSize: '22px',
}

const thStyle = {
  textAlign: 'left',
  padding: '12px',
  background: '#f8fbfa',
  color: '#64748b',
  borderBottom: '1px solid #dbe7e4',
  fontSize: '12px',
}

const tdStyle = {
  padding: '12px',
  borderBottom: '1px solid #edf2f1',
  color: '#334155',
  fontSize: '13px',
}

const smallButtonStyle = {
  border: '1px solid #2563eb33',
  background: '#eff6ff',
  color: '#2563eb',
  borderRadius: 'var(--one-radius-md, 10px)',
  padding: '6px 10px',
  cursor: 'pointer',
  fontWeight: '800',
  fontSize: '12px',
}
