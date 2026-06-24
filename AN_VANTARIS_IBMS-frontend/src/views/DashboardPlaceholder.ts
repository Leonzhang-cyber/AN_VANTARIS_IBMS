import { defineComponent, h, type VNodeChild } from 'vue'

type MetricCard = {
  label: string
  value: string
  note: string
  tone: string
}

type WorkspaceCard = {
  title: string
  route: string
  status: string
  description: string
  metrics: string[]
}

type ScenarioRow = {
  flow: string
  entry: string
  outcome: string
  route: string
}

const metrics: MetricCard[] = [
  { label: 'Open Work Orders', value: '42', note: 'UMMS maintenance queue across terminal, BHS, CCTV, access control and mechanical systems', tone: '#0f766e' },
  { label: 'Critical Assets', value: '18', note: 'Assets with high operational impact or active service risk', tone: '#b45309' },
  { label: 'SLA At Risk', value: '7', note: 'Work orders requiring supervisor attention before breach', tone: '#dc2626' },
  { label: 'Evidence Ready', value: '128', note: 'Traceable records prepared across operations, maintenance and reports', tone: '#2563eb' },
  { label: 'Energy Exceptions', value: '11', note: 'Energy or sustainability metrics requiring review', tone: '#16a34a' },
  { label: 'Report Packs', value: '9', note: 'Customer handoff and operations reports available from Reports Center', tone: '#7c3aed' },
]

const workspaces: WorkspaceCard[] = [
  {
    title: 'UMMS Maintenance Workspace',
    route: '/one/umms/workspace',
    status: 'Customer-ready',
    description: 'Work orders, preventive maintenance, predictive risk, SLA aging, assignments, evidence and maintenance reports.',
    metrics: ['Fault-linked work orders', 'SLA & aging', 'Engineer assignments', 'Maintenance evidence'],
  },
  {
    title: 'Assets & Topology',
    route: '/assets/topology',
    status: 'Operational view',
    description: 'System, equipment and asset relationship views for site, space, system and maintenance context.',
    metrics: ['Asset registry', 'System topology', 'Runtime status', 'Maintenance history'],
  },
  {
    title: 'Reports & Compliance',
    route: '/reports',
    status: 'Report center',
    description: 'Operations, alarm, fault, maintenance, energy, compliance and customer handoff report entries.',
    metrics: ['Maintenance reports', 'Energy reports', 'Export center', 'Compliance evidence'],
  },
  {
    title: 'UESG Sustainability',
    route: '/uesg/sustainability',
    status: 'Sustainability view',
    description: 'Energy, carbon, data quality, utility baseline and sustainability reporting workspace.',
    metrics: ['Energy metrics', 'Carbon metrics', 'Green Mark support', 'Report readiness'],
  },
  {
    title: 'UCDE Evidence Center',
    route: '/ucde/evidence',
    status: 'Traceability view',
    description: 'Evidence detail, evidence hash, source references, audit trail and export linkage.',
    metrics: ['Evidence chain', 'Decision evidence', 'Fault evidence', 'Maintenance evidence'],
  },
  {
    title: 'NexusAI Insights',
    route: '/one/nexus-ai/branch-audit',
    status: 'Insight view',
    description: 'Operational insight, maintenance risk, energy insight, branch impact and decision support.',
    metrics: ['Risk insight', 'Maintenance suggestions', 'Confidence evidence', 'Branch audit'],
  },
]

const scenarioRows: ScenarioRow[] = [
  {
    flow: 'Fault to Work Order',
    entry: 'Critical alarm or equipment fault',
    outcome: 'UMMS work order with asset, system, SLA and evidence context',
    route: '/one/umms/workspace',
  },
  {
    flow: 'Asset to Evidence',
    entry: 'Asset or system selected from topology',
    outcome: 'Relationship graph, maintenance history and evidence trace',
    route: '/one/assets/context',
  },
  {
    flow: 'Operations to Report',
    entry: 'Customer review or management meeting',
    outcome: 'Operations, maintenance, energy and compliance report pack',
    route: '/reports',
  },
  {
    flow: 'Energy Exception to Action',
    entry: 'Energy or carbon anomaly',
    outcome: 'UESG review, sustainability evidence and improvement action',
    route: '/uesg/sustainability',
  },
]

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
  return h('article', { style: { ...panelStyle, padding: '20px', ...extra } }, children)
}

export default defineComponent({
  name: 'DashboardPlaceholder',
  setup() {
    return () => h('section', {
      style: {
        minHeight: '100vh',
        padding: '28px',
        background: 'linear-gradient(135deg, #f5fbf8 0%, #eef5ff 52%, #f9fafb 100%)',
        color: '#10201d',
      },
    }, [
      h('header', {
        style: {
          ...panelStyle,
          padding: '28px',
          display: 'flex',
          justifyContent: 'space-between',
          gap: '22px',
          alignItems: 'flex-start',
          marginBottom: '18px',
        },
      }, [
        h('div', [
          h('p', { style: { margin: '0 0 8px', color: '#0f766e', fontWeight: '800', letterSpacing: '.08em', textTransform: 'uppercase', fontSize: '12px' } }, 'VANTARIS ONE / International GA Dashboard'),
          h('h1', { style: { margin: '0 0 10px', fontSize: '34px', lineHeight: '1.12' } }, 'Customer Operations Command Overview'),
          h('p', { style: { margin: 0, maxWidth: '920px', color: '#52615d', fontSize: '15px', lineHeight: '1.7' } }, 'Unified customer-facing overview for operations, maintenance, assets, sustainability, evidence, reports and intelligent risk review.'),
        ]),
        h('div', { style: { display: 'flex', gap: '8px', flexWrap: 'wrap', justifyContent: 'flex-end' } }, [
          h('span', { style: badge('#0f766e', '#ecfdf5') }, 'Dashboard'),
          h('span', { style: badge('#2563eb', '#eff6ff') }, 'Customer-ready modules'),
          h('span', { style: badge('#7c3aed', '#f5f3ff') }, 'International GA view'),
        ]),
      ]),

      h('section', { style: { display: 'grid', gridTemplateColumns: 'repeat(6, minmax(0, 1fr))', gap: '14px', marginBottom: '18px' } },
        metrics.map((item) => card([
          h('span', { style: { display: 'block', color: '#64748b', fontSize: '12px', fontWeight: '700', marginBottom: '8px' } }, item.label),
          h('strong', { style: { display: 'block', fontSize: '28px', color: item.tone, marginBottom: '8px' } }, item.value),
          h('p', { style: { margin: 0, color: '#52615d', fontSize: '12px', lineHeight: '1.45' } }, item.note),
        ], { minHeight: '132px' })),
      ),

      h('section', { style: { display: 'grid', gridTemplateColumns: '1.2fr .8fr', gap: '18px', marginBottom: '18px' } }, [
        card([
          h('div', { style: sectionHeaderStyle }, [
            h('div', [
              h('p', { style: eyebrowStyle }, 'Customer-ready workspaces'),
              h('h2', { style: headingStyle }, 'Core module entry points'),
            ]),
          ]),
          h('div', { style: { display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: '14px' } },
            workspaces.map((item) => h('button', {
              type: 'button',
              onClick: () => openRoute(item.route),
              style: {
                textAlign: 'left',
                border: '1px solid #dbe7e4',
                borderRadius: '14px',
                background: '#f8fbfa',
                padding: '16px',
                cursor: 'pointer',
              },
            }, [
              h('span', { style: badge('#0f766e', '#ecfdf5') }, item.status),
              h('h3', { style: { margin: '12px 0 8px', fontSize: '17px' } }, item.title),
              h('p', { style: { margin: '0 0 12px', color: '#52615d', lineHeight: '1.55', fontSize: '13px' } }, item.description),
              h('div', { style: { display: 'flex', flexWrap: 'wrap', gap: '6px' } },
                item.metrics.map((m) => h('span', { style: miniPillStyle }, m)),
              ),
            ])),
          ),
        ]),

        card([
          h('p', { style: eyebrowStyle }, 'Readiness summary'),
          h('h2', { style: headingStyle }, 'International GA focus'),
          h('ul', { style: { margin: 0, paddingLeft: '18px', color: '#52615d', lineHeight: '1.85' } }, [
            h('li', 'UMMS maintenance workspace is the primary customer workflow view.'),
            h('li', 'L1/L2 remain in the sidebar; L3 content is handled inside pages.'),
            h('li', 'Reports, evidence and asset context are linked as customer review flows.'),
            h('li', 'Server and deployment pages should stay out of customer-facing presentation unless requested.'),
          ]),
          h('div', { style: { marginTop: '16px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' } }, [
            h('button', { type: 'button', onClick: () => openRoute('/one/umms/workspace'), style: actionButtonStyle }, 'Open UMMS'),
            h('button', { type: 'button', onClick: () => openRoute('/reports'), style: actionButtonStyle }, 'Open Reports'),
          ]),
        ]),
      ]),

      card([
        h('div', { style: sectionHeaderStyle }, [
          h('div', [
            h('p', { style: eyebrowStyle }, 'Scenario flows'),
            h('h2', { style: headingStyle }, 'Customer production review paths'),
          ]),
        ]),
        h('div', { style: { overflowX: 'auto' } }, [
          h('table', { style: { width: '100%', borderCollapse: 'collapse', minWidth: '900px' } }, [
            h('thead', [
              h('tr', [
                h('th', { style: thStyle }, 'Flow'),
                h('th', { style: thStyle }, 'Entry'),
                h('th', { style: thStyle }, 'Outcome'),
                h('th', { style: thStyle }, 'Action'),
              ]),
            ]),
            h('tbody', scenarioRows.map((row) => h('tr', [
              h('td', { style: tdStyle }, row.flow),
              h('td', { style: tdStyle }, row.entry),
              h('td', { style: tdStyle }, row.outcome),
              h('td', { style: tdStyle }, [
                h('button', { type: 'button', onClick: () => openRoute(row.route), style: smallButtonStyle }, 'Open'),
              ]),
            ]))),
          ]),
        ]),
      ]),
    ])
  },
})

function badge(color: string, background: string) {
  return {
    display: 'inline-flex',
    alignItems: 'center',
    borderRadius: '999px',
    padding: '6px 10px',
    border: `1px solid ${color}22`,
    color,
    background,
    fontSize: '12px',
    fontWeight: '800',
  }
}

const eyebrowStyle = {
  margin: '0 0 8px',
  color: '#0f766e',
  fontWeight: '800',
  letterSpacing: '.08em',
  textTransform: 'uppercase',
  fontSize: '12px',
}

const headingStyle = {
  margin: '0 0 16px',
  fontSize: '20px',
}

const sectionHeaderStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  gap: '12px',
}

const miniPillStyle = {
  border: '1px solid #dbe7e4',
  borderRadius: '999px',
  padding: '5px 8px',
  fontSize: '11px',
  color: '#475569',
  background: '#fff',
}

const actionButtonStyle = {
  border: '1px solid #0f766e',
  background: '#0f766e',
  color: '#fff',
  borderRadius: '10px',
  padding: '10px 12px',
  fontWeight: '800',
  cursor: 'pointer',
}

const smallButtonStyle = {
  border: '1px solid #2563eb',
  background: '#eff6ff',
  color: '#1d4ed8',
  borderRadius: '8px',
  padding: '7px 12px',
  fontWeight: '800',
  cursor: 'pointer',
}

const thStyle = {
  textAlign: 'left',
  borderBottom: '1px solid #dbe7e4',
  padding: '12px',
  color: '#64748b',
  fontSize: '12px',
  textTransform: 'uppercase',
}

const tdStyle = {
  borderBottom: '1px solid #edf2f7',
  padding: '12px',
  color: '#334155',
  verticalAlign: 'top',
}
