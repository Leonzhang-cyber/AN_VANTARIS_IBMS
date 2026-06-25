import { computed, defineComponent, h, type VNodeChild } from 'vue'
import { useRoute } from 'vue-router'

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
}

const defaultMetrics: MetricCard[] = [
  { label: 'Open Work Orders', value: '42', note: 'Active maintenance queue across critical systems', tone: '#0f766e' },
  { label: 'Critical Assets', value: '18', note: 'High impact assets requiring operational review', tone: '#b45309' },
  { label: 'SLA At Risk', value: '7', note: 'Items requiring supervisor attention before breach', tone: '#dc2626' },
  { label: 'Evidence Ready', value: '128', note: 'Traceable records ready for review or export', tone: '#2563eb' },
]

const sections: Record<string, SectionConfig> = {
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
    primaryAction: 'Open Evidence Center',
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
}

const fallbackSection: SectionConfig = {
  title: 'Dashboard Overview',
  subtitle: 'Unified operational overview across maintenance, assets, evidence, reports, energy, and customer delivery.',
  primaryRoute: '/one/umms/workspace',
  primaryAction: 'Open UMMS',
  metrics: defaultMetrics,
  actions: [
    { title: 'Review operations dashboard', owner: 'Operator', status: 'Open', priority: 'Medium', route: '/console/operations' },
    { title: 'Open customer report center', owner: 'Reports', status: 'Ready', priority: 'Medium', route: '/reports' },
    { title: 'Check evidence readiness', owner: 'UCDE', status: 'Ready', priority: 'Medium', route: '/ucde/evidence' },
  ],
}

const panelStyle = {
  background: '#ffffff',
  border: '1px solid #dbe7e4',
  borderRadius: '16px',
  boxShadow: '0 16px 38px rgba(15, 23, 42, 0.08)',
}

function openRoute(path: string): void {
  window.location.assign(path)
}

function card(children: VNodeChild[], extra: Record<string, string> = {}) {
  return h('article', { style: { ...panelStyle, padding: '18px', ...extra } }, children)
}

function normalizeL3(value: unknown): string {
  return typeof value === 'string' && value ? value : 'my-tasks'
}

export default defineComponent({
  name: 'DashboardPlaceholder',
  setup() {
    const route = useRoute()
    const activeSection = computed(() => sections[normalizeL3(route.query.l3)] ?? fallbackSection)

    return () => h('section', {
      style: {
        minHeight: '100vh',
        padding: '18px',
        background: 'linear-gradient(135deg, #f5fbf8 0%, #eef5ff 52%, #f9fafb 100%)',
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

      h('section', { style: { display: 'grid', gridTemplateColumns: '1.2fr .8fr', gap: '16px', marginBottom: '16px' } }, [
        card([
          h('div', { style: sectionHeaderStyle }, [
            h('div', [
              h('p', { style: eyebrowStyle }, 'Selected dashboard section'),
              h('h2', { style: headingStyle }, activeSection.value.title),
              h('p', { style: subtitleStyle }, activeSection.value.subtitle),
            ]),
            h('button', { type: 'button', onClick: () => openRoute(activeSection.value.primaryRoute), style: actionButtonStyle }, activeSection.value.primaryAction),
          ]),
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
          h('h2', { style: headingStyle }, 'Connected workspaces'),
          h('div', { style: { display: 'grid', gap: '10px' } }, [
            routeButton('UMMS Maintenance', '/one/umms/workspace'),
            routeButton('Assets & Topology', '/assets/topology'),
            routeButton('Evidence Center', '/ucde/evidence'),
            routeButton('Reports Center', '/reports'),
            routeButton('UESG Sustainability', '/uesg/sustainability'),
          ]),
        ]),
      ]),
    ])
  },
})

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

const subtitleStyle = {
  margin: 0,
  color: '#52615d',
  lineHeight: '1.6',
  fontSize: '13px',
  maxWidth: '760px',
}

const sectionHeaderStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  gap: '16px',
  alignItems: 'flex-start',
  marginBottom: '16px',
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

const actionButtonStyle = {
  border: '1px solid #0f766e33',
  background: '#ecfdf5',
  color: '#0f766e',
  borderRadius: '12px',
  padding: '10px 14px',
  cursor: 'pointer',
  fontWeight: '800',
  whiteSpace: 'nowrap',
}

const smallButtonStyle = {
  border: '1px solid #2563eb33',
  background: '#eff6ff',
  color: '#2563eb',
  borderRadius: '999px',
  padding: '6px 10px',
  cursor: 'pointer',
  fontWeight: '800',
  fontSize: '12px',
}
