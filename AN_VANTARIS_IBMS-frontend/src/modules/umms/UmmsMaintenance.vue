<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ApiError } from '@/services/api/errors'
import { getUmmsGaR2Workspace, type UmmsGaR2Workspace, type UmmsGaR2WorkOrder } from '@/services/api/umms'
import { resolveL3RouteContentConfig } from '@/services/menu/l3-content-registry'

type CustomerSection = {
  title: string
  subtitle: string
  primaryAction: string
  targetTab: string
  metrics: Array<{ label: string; value: string; note: string }>
  rows: Array<{ item: string; focus: string; status: string }>
}

type DeepSectionConfig = {
  insight: string
  riskLevel: string
  affectedService: string
  recommendedOwner: string
  painPoints: string[]
  recommendations: string[]
  decisionRows: Array<{
    item: string
    assetOrSystem: string
    owner: string
    priority: string
    riskOrSla: string
    nextAction: string
  }>
  evidence: Array<{ label: string; status: string; note: string }>
}

const route = useRoute()
const customerUnavailableMessage = 'Live service is temporarily unavailable. Showing the latest available operational view.'

const tabs = [
  'Overview',
  'Work Orders',
  'Preventive',
  'Predictive',
  'Assignments',
  'SLA & Aging',
  'Execution',
  'Parts / Vendor',
  'Evidence',
  'Closure',
  'Reports',
]

const loading = ref(false)
const apiError = ref('')
const activeTab = ref('Overview')
const workspace = ref<UmmsGaR2Workspace | null>(null)
const reportToast = ref('')

const customerSections: Record<string, CustomerSection> = {
  'open-work-orders': {
    title: 'Open Work Orders',
    subtitle: 'Open maintenance queue across assets, systems, SLA risk, engineer assignment, and evidence status.',
    primaryAction: 'Review open work orders',
    targetTab: 'Work Orders',
    metrics: [
      { label: 'Open WOs', value: '42', note: 'Open maintenance work orders' },
      { label: 'High Priority', value: '11', note: 'Critical and high priority queue' },
      { label: 'SLA Risk', value: '7', note: 'Work orders approaching breach' },
      { label: 'Evidence Pending', value: '8', note: 'Closure evidence under review' },
    ],
    rows: [
      { item: 'Review open work order queue', focus: 'Status, asset and SLA due', status: 'Active' },
      { item: 'Open high priority work orders', focus: 'Critical service impact', status: 'High' },
      { item: 'Check closure evidence', focus: 'UCDE evidence linkage', status: 'Review' },
    ],
  },
  'assigned-work-orders': {
    title: 'Assigned Work Orders',
    subtitle: 'Engineer assignment view across workload, discipline, shift availability, escalation owner, and active tasks.',
    primaryAction: 'Review assignments',
    targetTab: 'Assignments',
    metrics: [
      { label: 'Assigned WOs', value: '27', note: 'Work orders assigned to teams' },
      { label: 'Engineers', value: '9', note: 'Engineers with active workload' },
      { label: 'Shift Coverage', value: '3', note: 'Shifts represented in workload view' },
      { label: 'Escalations', value: '4', note: 'Assignments requiring escalation owner' },
    ],
    rows: [
      { item: 'Review engineer workload', focus: 'Assigned work orders and skills', status: 'Active' },
      { item: 'Open shift availability', focus: 'Coverage and escalation owner', status: 'Ready' },
      { item: 'Prepare assignment evidence', focus: 'Workload and shift evidence', status: 'Ready' },
    ],
  },
  'emergency-work-orders': {
    title: 'Emergency Work Orders',
    subtitle: 'Emergency maintenance queue for critical assets, service impact, engineer response, and evidence trail.',
    primaryAction: 'Review emergency queue',
    targetTab: 'Work Orders',
    metrics: [
      { label: 'Emergency WOs', value: '5', note: 'Emergency work orders under review' },
      { label: 'Critical Assets', value: '4', note: 'Assets with service impact' },
      { label: 'SLA At Risk', value: '5', note: 'Emergency SLA exposure' },
      { label: 'Evidence Linked', value: '5', note: 'Emergency records with evidence' },
    ],
    rows: [
      { item: 'Review emergency queue', focus: 'Criticality and SLA due', status: 'High' },
      { item: 'Open impacted assets', focus: 'Asset and service context', status: 'Active' },
      { item: 'Prepare emergency evidence', focus: 'Evidence trail and closure state', status: 'Ready' },
    ],
  },
  'fault-linked-work-orders': {
    title: 'Fault-linked Work Orders',
    subtitle: 'Work orders created from alarms and faults with source event, impacted asset, and evidence linkage.',
    primaryAction: 'Review fault-linked WOs',
    targetTab: 'Evidence',
    metrics: [
      { label: 'Fault-linked WOs', value: '18', note: 'Work orders tied to faults' },
      { label: 'Critical Faults', value: '6', note: 'Faults with critical impact' },
      { label: 'Asset Links', value: '18', note: 'Work orders linked to assets' },
      { label: 'Evidence Ready', value: '15', note: 'Evidence-linked records' },
    ],
    rows: [
      { item: 'Review fault-linked queue', focus: 'Fault source and work order state', status: 'Active' },
      { item: 'Open source fault evidence', focus: 'Alarm / fault trace', status: 'Ready' },
      { item: 'Prepare closure record', focus: 'Work order evidence chain', status: 'Review' },
    ],
  },
  'preventive-work-orders': {
    title: 'Preventive Work Orders',
    subtitle: 'Preventive maintenance work orders by plan, frequency, due date, compliance, and checklist readiness.',
    primaryAction: 'Review preventive WOs',
    targetTab: 'Preventive',
    metrics: [
      { label: 'Preventive WOs', value: '14', note: 'Preventive work orders due soon' },
      { label: 'Due Today', value: '7', note: 'Preventive work scheduled today' },
      { label: 'Compliance Risk', value: '3', note: 'PM items needing review' },
      { label: 'Checklist Ready', value: '11', note: 'PM checklists ready' },
    ],
    rows: [
      { item: 'Review preventive queue', focus: 'Schedule and compliance state', status: 'Ready' },
      { item: 'Open PM checklist', focus: 'Checklist readiness', status: 'Active' },
      { item: 'Prepare PM evidence', focus: 'Preventive evidence package', status: 'Ready' },
    ],
  },
  'corrective-work-orders': {
    title: 'Corrective Work Orders',
    subtitle: 'Corrective maintenance view across issue source, technician action, parts readiness, and closure review.',
    primaryAction: 'Review corrective WOs',
    targetTab: 'Work Orders',
    metrics: [
      { label: 'Corrective WOs', value: '16', note: 'Corrective work orders open' },
      { label: 'Parts Watch', value: '5', note: 'Items requiring materials readiness' },
      { label: 'Engineer Updates', value: '12', note: 'Engineer updates recorded' },
      { label: 'Closure Review', value: '6', note: 'Corrective records awaiting review' },
    ],
    rows: [
      { item: 'Review corrective queue', focus: 'Source event and action status', status: 'Active' },
      { item: 'Open parts readiness', focus: 'Materials and vendor notes', status: 'Review' },
      { item: 'Prepare corrective closure', focus: 'Evidence and closure records', status: 'Ready' },
    ],
  },
  'work-order-detail': {
    title: 'Work Order Detail',
    subtitle: 'Focused work order context with asset, system, location, source fault, engineer, SLA, and evidence.',
    primaryAction: 'Review work order detail',
    targetTab: 'Work Orders',
    metrics: [
      { label: 'Context Fields', value: '12', note: 'Core customer-visible fields' },
      { label: 'Evidence Items', value: '5', note: 'Evidence linked to selected WO' },
      { label: 'SLA Fields', value: '4', note: 'SLA and aging indicators' },
      { label: 'Action Rows', value: '3', note: 'Next review actions' },
    ],
    rows: [
      { item: 'Review work order detail', focus: 'Asset, system and source fault', status: 'Ready' },
      { item: 'Open engineer update', focus: 'Engineer action and status', status: 'Active' },
      { item: 'Check closure evidence', focus: 'Evidence and approval record', status: 'Review' },
    ],
  },
  'closure-evidence': {
    title: 'Closure Evidence',
    subtitle: 'Closure evidence view for completed work, approval records, attachments, and audit traceability.',
    primaryAction: 'Review closure evidence',
    targetTab: 'Evidence',
    metrics: [
      { label: 'Closure Packages', value: '8', note: 'Closure packages under review' },
      { label: 'Attachments', value: '21', note: 'Attachments linked to closure records' },
      { label: 'Approval Records', value: '8', note: 'Closure approvals represented' },
      { label: 'Audit Ready', value: '6', note: 'Closure packages ready for audit' },
    ],
    rows: [
      { item: 'Review closure evidence', focus: 'Work order closure trail', status: 'Review' },
      { item: 'Open attachments', focus: 'Photos, notes and records', status: 'Ready' },
      { item: 'Prepare closure export', focus: 'Customer-ready evidence package', status: 'Ready' },
    ],
  },
  'pm-calendar': {
    title: 'PM Calendar',
    subtitle: 'Preventive maintenance calendar across due dates, frequency, compliance state, and checklist readiness.',
    primaryAction: 'Review PM calendar',
    targetTab: 'Preventive',
    metrics: [
      { label: 'PM Tasks', value: '24', note: 'Scheduled preventive tasks' },
      { label: 'Due Today', value: '7', note: 'PM tasks due today' },
      { label: 'Due This Week', value: '14', note: 'PM tasks due this week' },
      { label: 'Compliance Watch', value: '3', note: 'PM items requiring review' },
    ],
    rows: [
      { item: 'Review PM calendar', focus: 'Due dates and frequency', status: 'Ready' },
      { item: 'Open due-today PM', focus: 'Today schedule and owners', status: 'Active' },
      { item: 'Prepare PM report', focus: 'Compliance and evidence', status: 'Ready' },
    ],
  },
  'pm-templates': {
    title: 'PM Templates',
    subtitle: 'Preventive maintenance templates with checklist readiness, asset group coverage, and evidence rules.',
    primaryAction: 'Review PM templates',
    targetTab: 'Preventive',
    metrics: [
      { label: 'Templates', value: '18', note: 'PM templates available' },
      { label: 'Checklist Ready', value: '15', note: 'Templates with checklist coverage' },
      { label: 'Asset Groups', value: '9', note: 'Asset groups covered' },
      { label: 'Evidence Rules', value: '12', note: 'Templates with evidence rules' },
    ],
    rows: [
      { item: 'Review PM templates', focus: 'Checklist and asset coverage', status: 'Ready' },
      { item: 'Open checklist readiness', focus: 'Template completeness', status: 'Review' },
      { item: 'Prepare template evidence', focus: 'Evidence rules and audit trail', status: 'Ready' },
    ],
  },
  'pm-schedule': {
    title: 'PM Schedule',
    subtitle: 'Preventive maintenance schedule by next due date, asset group, compliance status, and owner readiness.',
    primaryAction: 'Review PM schedule',
    targetTab: 'Preventive',
    metrics: [
      { label: 'Scheduled PM', value: '24', note: 'PM items on schedule' },
      { label: 'Next Due', value: '7', note: 'Items due in the next operating day' },
      { label: 'Owner Assigned', value: '21', note: 'PM items with owner assignment' },
      { label: 'Evidence Ready', value: '18', note: 'PM evidence records ready' },
    ],
    rows: [
      { item: 'Review PM schedule', focus: 'Due date and assignment', status: 'Ready' },
      { item: 'Open owner gaps', focus: 'Unassigned PM items', status: 'Review' },
      { item: 'Prepare schedule evidence', focus: 'PM schedule evidence package', status: 'Ready' },
    ],
  },
  'engineer-calendar': {
    title: 'Engineer Calendar',
    subtitle: 'Engineer workload calendar with assignments, skills, shift availability, and escalation ownership.',
    primaryAction: 'Review engineer calendar',
    targetTab: 'Assignments',
    metrics: [
      { label: 'Engineers', value: '9', note: 'Engineers represented' },
      { label: 'Assigned WOs', value: '27', note: 'Assigned work orders' },
      { label: 'Shift Conflicts', value: '2', note: 'Calendar conflicts requiring review' },
      { label: 'Escalations', value: '4', note: 'Items requiring escalation owner' },
    ],
    rows: [
      { item: 'Review engineer calendar', focus: 'Shift and workload coverage', status: 'Ready' },
      { item: 'Open assignment load', focus: 'Engineer capacity and skills', status: 'Active' },
      { item: 'Prepare workload evidence', focus: 'Assignment evidence record', status: 'Ready' },
    ],
  },
  'assignment-load': {
    title: 'Assignment Load',
    subtitle: 'Assignment load view for engineer capacity, assigned work orders, skill coverage, and SLA exposure.',
    primaryAction: 'Review assignment load',
    targetTab: 'Assignments',
    metrics: [
      { label: 'Assigned WOs', value: '27', note: 'Assigned work order load' },
      { label: 'High Load Engineers', value: '3', note: 'Engineers with elevated workload' },
      { label: 'Skill Gaps', value: '2', note: 'Assignments needing skill review' },
      { label: 'SLA Exposure', value: '6', note: 'Assigned items at SLA risk' },
    ],
    rows: [
      { item: 'Review load balance', focus: 'Engineer capacity and SLA risk', status: 'Review' },
      { item: 'Open skill coverage', focus: 'Discipline and availability', status: 'Active' },
      { item: 'Prepare assignment report', focus: 'Workload evidence', status: 'Ready' },
    ],
  },
  'assignment-dispatch': {
    title: 'Assignment & Dispatch',
    subtitle: 'Dispatch readiness across assigned work orders, technician availability, SLA exposure, and escalation ownership.',
    primaryAction: 'Review dispatch readiness',
    targetTab: 'Assignments',
    metrics: [
      { label: 'Assigned WOs', value: '27', note: 'Work orders assigned to teams' },
      { label: 'Dispatch Watch', value: '6', note: 'Items with SLA or access exposure' },
      { label: 'Escalation Owners', value: '4', note: 'Escalation owners represented' },
      { label: 'Shift Coverage', value: '3', note: 'Shifts represented in workload view' },
    ],
    rows: [
      { item: 'Review assignment and dispatch', focus: 'Owner, shift, discipline, and SLA exposure', status: 'Active' },
      { item: 'Confirm escalation owner', focus: 'Supervisor or duty owner for high-risk work', status: 'Review' },
      { item: 'Prepare dispatch evidence', focus: 'Assignment and workload evidence', status: 'Ready' },
    ],
  },
  'sla-dashboard': {
    title: 'SLA Dashboard',
    subtitle: 'SLA dashboard for due soon, overdue work orders, aging buckets, MTTR, response, and escalation.',
    primaryAction: 'Review SLA dashboard',
    targetTab: 'SLA & Aging',
    metrics: [
      { label: 'SLA At Risk', value: '7', note: 'Items approaching breach' },
      { label: 'Overdue', value: '3', note: 'Work orders past SLA due' },
      { label: 'Due Today', value: '9', note: 'Items due today' },
      { label: 'Avg MTTR', value: '3.8h', note: 'Rolling maintenance MTTR' },
    ],
    rows: [
      { item: 'Review SLA dashboard', focus: 'Due soon and overdue items', status: 'Active' },
      { item: 'Open escalation queue', focus: 'Supervisor review items', status: 'High' },
      { item: 'Prepare SLA report', focus: 'SLA evidence and response time', status: 'Ready' },
    ],
  },
  'breach-risk': {
    title: 'Breach Risk',
    subtitle: 'Breach risk queue for work orders nearing SLA breach, escalation owners, and customer impact.',
    primaryAction: 'Review breach risk',
    targetTab: 'SLA & Aging',
    metrics: [
      { label: 'Breach Risk', value: '7', note: 'Items nearing SLA breach' },
      { label: 'Critical Risk', value: '2', note: 'Critical breach risk items' },
      { label: 'Escalation Owners', value: '5', note: 'Assigned escalation owners' },
      { label: 'Evidence Pending', value: '4', note: 'Risk items needing evidence' },
    ],
    rows: [
      { item: 'Review breach risk queue', focus: 'SLA due and owner readiness', status: 'High' },
      { item: 'Open customer impact items', focus: 'Service risk and mitigation', status: 'Review' },
      { item: 'Prepare breach evidence', focus: 'SLA and action evidence', status: 'Ready' },
    ],
  },
  'escalation-queue': {
    title: 'Escalation Queue',
    subtitle: 'Escalation queue for high-risk work orders, owners, customer impact, and closure evidence.',
    primaryAction: 'Review escalation queue',
    targetTab: 'SLA & Aging',
    metrics: [
      { label: 'Escalations', value: '8', note: 'Escalation items open' },
      { label: 'High Priority', value: '5', note: 'High priority escalation items' },
      { label: 'Owner Assigned', value: '7', note: 'Items with escalation owner' },
      { label: 'Evidence Ready', value: '5', note: 'Escalations with evidence' },
    ],
    rows: [
      { item: 'Review escalation queue', focus: 'Priority and owner state', status: 'Active' },
      { item: 'Open high-priority escalation', focus: 'Customer impact and SLA', status: 'High' },
      { item: 'Prepare escalation evidence', focus: 'Action and approval trail', status: 'Ready' },
    ],
  },
  mttr: {
    title: 'MTTR',
    subtitle: 'Mean time to repair view across work order closure, system category, team response, and evidence.',
    primaryAction: 'Review MTTR',
    targetTab: 'SLA & Aging',
    metrics: [
      { label: 'Average MTTR', value: '3.8h', note: 'Rolling maintenance MTTR' },
      { label: 'Critical MTTR', value: '2.4h', note: 'Critical queue repair average' },
      { label: 'Improving Systems', value: '6', note: 'Systems trending better' },
      { label: 'Review Items', value: '3', note: 'MTTR outliers for review' },
    ],
    rows: [
      { item: 'Review MTTR trend', focus: 'System and priority performance', status: 'Ready' },
      { item: 'Open MTTR outliers', focus: 'Repair delays and root cause', status: 'Review' },
      { item: 'Prepare MTTR report', focus: 'Customer maintenance performance', status: 'Ready' },
    ],
  },
  mtbf: {
    title: 'MTBF',
    subtitle: 'Mean time between failures view for repeated failures, reliability, asset health, and improvement actions.',
    primaryAction: 'Review MTBF',
    targetTab: 'Predictive',
    metrics: [
      { label: 'MTBF Watchlist', value: '9', note: 'Assets needing reliability review' },
      { label: 'Repeated Failures', value: '6', note: 'Assets with repeated failures' },
      { label: 'Reliability Actions', value: '5', note: 'Improvement actions in progress' },
      { label: 'Evidence Ready', value: '8', note: 'Reliability records with evidence' },
    ],
    rows: [
      { item: 'Review MTBF watchlist', focus: 'Repeated failures and reliability', status: 'Review' },
      { item: 'Open reliability actions', focus: 'Improvement plan status', status: 'Active' },
      { item: 'Prepare reliability evidence', focus: 'Asset reliability report', status: 'Ready' },
    ],
  },
  'repeated-failures': {
    title: 'Repeated Failures',
    subtitle: 'Repeated failure view for high-repeat assets, fault linkage, maintenance actions, and evidence.',
    primaryAction: 'Review repeated failures',
    targetTab: 'Predictive',
    metrics: [
      { label: 'Repeated Failures', value: '6', note: 'Repeated failure cases open' },
      { label: 'High Repeat Assets', value: '4', note: 'Assets with repeated patterns' },
      { label: 'WO Linked', value: '6', note: 'Repeated failures linked to work orders' },
      { label: 'Evidence Ready', value: '5', note: 'Repeated failure evidence records' },
    ],
    rows: [
      { item: 'Review repeated failure queue', focus: 'Asset and fault pattern', status: 'Review' },
      { item: 'Open reliability work orders', focus: 'Corrective and preventive actions', status: 'Active' },
      { item: 'Prepare repeated failure evidence', focus: 'RCA and maintenance evidence', status: 'Ready' },
    ],
  },
  'predictive-risk': {
    title: 'Predictive Risk',
    subtitle: 'Predictive maintenance risk view across asset health, failure risk, anomaly summary, and recommended action.',
    primaryAction: 'Review predictive risk',
    targetTab: 'Predictive',
    metrics: [
      { label: 'Predictive Alerts', value: '5', note: 'Predictive alerts under review' },
      { label: 'High Severity', value: '2', note: 'High-severity predictive risks' },
      { label: 'Actions Recommended', value: '5', note: 'Recommended maintenance actions' },
      { label: 'Evidence Linked', value: '4', note: 'Predictive evidence records' },
    ],
    rows: [
      { item: 'Review predictive risk', focus: 'Asset health and anomaly summary', status: 'Active' },
      { item: 'Open recommended actions', focus: 'Maintenance plan alignment', status: 'Review' },
      { item: 'Prepare predictive evidence', focus: 'Risk evidence and confidence', status: 'Ready' },
    ],
  },
  'parts-vendor-notes': {
    title: 'Parts / Vendor Notes',
    subtitle: 'Parts, vendor, warranty, contract, and evidence coordination for corrective and SLA-sensitive work orders.',
    primaryAction: 'Review parts and vendor coordination',
    targetTab: 'Parts / Vendor',
    metrics: [
      { label: 'Parts Watch', value: '5', note: 'Corrective items requiring materials readiness' },
      { label: 'Vendor Exposure', value: '4', note: 'Items with vendor coordination' },
      { label: 'Warranty Review', value: '3', note: 'Warranty or contract context required' },
      { label: 'Vendor Evidence', value: '5', note: 'Vendor records needing evidence review' },
    ],
    rows: [
      { item: 'Review parts readiness', focus: 'Spare parts, requested material, and reserved items', status: 'Review' },
      { item: 'Check vendor responsibility', focus: 'Vendor, warranty, contract, and SLA commitment', status: 'Review' },
      { item: 'Prepare vendor evidence', focus: 'Vendor response and closure evidence', status: 'Ready' },
    ],
  },
  'technician-assignment': {
    title: 'Technician Assignment',
    subtitle: 'Technician execution view across task status, checklist readiness, linked asset, linked event, and required evidence.',
    primaryAction: 'Review technician execution',
    targetTab: 'Execution',
    metrics: [
      { label: 'Execution Tasks', value: '0', note: 'Rendered when task data is available' },
      { label: 'Checklist Status', value: 'Review', note: 'Checklist readiness by maintenance task' },
      { label: 'Evidence Required', value: 'Yes', note: 'Evidence field is tracked per task' },
      { label: 'Linked Events', value: 'Active', note: 'Tasks can retain source event context' },
    ],
    rows: [
      { item: 'Review technician execution', focus: 'Task, owner, status, checklist, and evidence', status: 'Review' },
      { item: 'Confirm linked asset and event', focus: 'Asset and source event context', status: 'Ready' },
      { item: 'Prepare execution evidence', focus: 'Technician notes and checklist evidence', status: 'Ready' },
    ],
  },
  'action-tracking': {
    title: 'Action Tracking',
    subtitle: 'Tracks corrective action progress across technician execution, evidence readiness, owner review, and closure state.',
    primaryAction: 'Review action tracking',
    targetTab: 'Execution',
    metrics: [
      { label: 'Active Actions', value: '12', note: 'Engineer updates recorded' },
      { label: 'Checklist Watch', value: '3', note: 'Tasks needing checklist review' },
      { label: 'Evidence Pending', value: '8', note: 'Actions awaiting closure evidence' },
      { label: 'Closure Review', value: '6', note: 'Actions awaiting supervisor review' },
    ],
    rows: [
      { item: 'Review action progress', focus: 'Technician status, checklist, and evidence', status: 'Active' },
      { item: 'Check action blockers', focus: 'SLA, parts, vendor, and access constraints', status: 'Review' },
      { item: 'Prepare closure review', focus: 'Evidence chain and supervisor acceptance', status: 'Ready' },
    ],
  },
  'closure-review': {
    title: 'Closure Review',
    subtitle: 'Closure readiness across technician notes, before / after evidence, parts, vendor evidence, supervisor review, and customer sign-off.',
    primaryAction: 'Review closure readiness',
    targetTab: 'Closure',
    metrics: [
      { label: 'Closure Evidence', value: '8', note: 'Closure packages under review' },
      { label: 'Supervisor Review', value: '6', note: 'Records awaiting supervisor review' },
      { label: 'Customer Sign-off', value: 'Gated', note: 'Gated by closure evidence readiness' },
      { label: 'Report Linkage', value: 'Ready', note: 'Linked report field is retained per work order' },
    ],
    rows: [
      { item: 'Review closure evidence', focus: 'Technician notes, before / after records, and attachments', status: 'Review' },
      { item: 'Confirm supervisor review', focus: 'High-impact and repeated faults need owner acceptance', status: 'Guarded' },
      { item: 'Gate customer sign-off', focus: 'Customer sign-off is gated by closure evidence readiness', status: 'Review' },
    ],
  },
  'customer-sign-off': {
    title: 'Customer Sign-off',
    subtitle: 'Customer sign-off status is reviewed after closure evidence, supervisor review, vendor evidence, and report linkage are ready.',
    primaryAction: 'Review customer sign-off',
    targetTab: 'Closure',
    metrics: [
      { label: 'Sign-off Pending', value: 'Review', note: 'Gated by closure evidence readiness' },
      { label: 'Evidence Chain', value: 'Required', note: 'Fault, technician, parts, and vendor evidence' },
      { label: 'Supervisor Review', value: 'Required', note: 'Owner acceptance before customer sign-off' },
      { label: 'Customer Report', value: 'Linked', note: 'Linked report field retained where available' },
    ],
    rows: [
      { item: 'Review customer sign-off gate', focus: 'Closure evidence readiness and supervisor review', status: 'Review' },
      { item: 'Check evidence chain', focus: 'Fault source, technician notes, parts, vendor, and report linkage', status: 'Review' },
      { item: 'Prepare customer-ready closure', focus: 'Customer-readable closure summary and sign-off gate', status: 'Guarded' },
    ],
  },
}

const defaultCustomerSection = customerSections['open-work-orders']

const workflowSteps = [
  { label: 'Alarm / Fault Intake', note: 'Source Event' },
  { label: 'Asset & Location Context', note: 'Asset Quality Gate' },
  { label: 'Work Order Created', note: 'Fault-linked Work Order' },
  { label: 'Assignment & Dispatch', note: 'Owner and Shift' },
  { label: 'SLA Monitoring', note: 'Escalation Watch' },
  { label: 'Technician Execution', note: 'Checklist and Notes' },
  { label: 'Parts / Vendor', note: 'Contract and Evidence' },
  { label: 'Evidence & Sign-off', note: 'Closure Evidence' },
]

const defaultDeepSection: DeepSectionConfig = {
  insight: 'Maintenance workload is being reviewed by asset criticality, service exposure, field readiness, and evidence completeness.',
  riskLevel: 'Medium',
  affectedService: 'Customer facility operations',
  recommendedOwner: 'Maintenance Supervisor',
  painPoints: [
    'Open items can look similar unless fault source, asset criticality, and evidence gaps are reviewed together.',
    'Access windows and permit readiness can delay technically simple work orders.',
    'Closure quality depends on linking engineer notes, before/after records, and supervisor acceptance.',
  ],
  recommendations: [
    'Prioritize items that combine high service impact with short SLA remaining.',
    'Attach source fault evidence before closure review.',
    'Use supervisor review when repeated faults or access constraints could affect customer operations.',
  ],
  decisionRows: [
    { item: 'Maintenance triage', assetOrSystem: 'Critical facility assets', owner: 'Maintenance Supervisor', priority: 'High', riskOrSla: 'SLA watch', nextAction: 'Confirm owner, access window, and evidence readiness' },
    { item: 'Evidence readiness check', assetOrSystem: 'Work order closure records', owner: 'UCDE Owner', priority: 'Medium', riskOrSla: 'Closure risk', nextAction: 'Verify before/after notes and report linkage' },
    { item: 'Customer handoff review', assetOrSystem: 'Maintenance report package', owner: 'Service Manager', priority: 'Medium', riskOrSla: 'Handoff quality', nextAction: 'Prepare customer-readable action summary' },
  ],
  evidence: [
    { label: 'Work order evidence', status: 'Review required', note: 'Engineer update, photos or checklist must support closure.' },
    { label: 'Customer report linkage', status: 'Available', note: 'Selected items can be exported into the maintenance report pack.' },
    { label: 'Supervisor acceptance', status: 'Guarded', note: 'High-impact or repeated faults require supervisor review before closure.' },
  ],
}

const ummsDeepSections: Record<string, DeepSectionConfig> = {
  'open-work-orders': {
    insight: 'Priority is driven by passenger-facing service impact, repeated source faults, SLA remaining, and whether closure evidence is already attached.',
    riskLevel: 'High',
    affectedService: 'Terminal comfort, baggage support, and tenant-facing service continuity',
    recommendedOwner: 'Duty Maintenance Supervisor',
    painPoints: [
      'Several high-priority work orders share source alarms with the same AHU and lift subsystems, so duplicate dispatch can hide the real asset issue.',
      'SLA breach risk is mainly caused by access window limits and missing fault evidence, not only technician availability.',
      'Closure cannot be trusted if engineer notes are not linked to the originating alarm, asset history, and before/after evidence.',
    ],
    recommendations: [
      'Merge duplicate work orders raised from the same source fault before dispatching a second team.',
      'Escalate short-SLA items that affect terminal comfort or passenger movement to the duty supervisor.',
      'Attach alarm snapshot, field note, and asset history evidence before moving any item to closure review.',
    ],
    decisionRows: [
      { item: 'AHU repeated high-temperature call', assetOrSystem: 'AHU-T2-04 / HVAC', owner: 'HVAC Team A', priority: 'Critical', riskOrSla: '2h remaining', nextAction: 'Dispatch with filter history and trend evidence attached' },
      { item: 'Lift landing door intermittent fault', assetOrSystem: 'Lift-L3-02 / Vertical Transport', owner: 'Vendor Lift Response', priority: 'High', riskOrSla: 'Passenger service risk', nextAction: 'Open vendor ticket and assign supervisor watch' },
      { item: 'Baggage belt motor overload', assetOrSystem: 'BHS-Belt-17 / Baggage Handling', owner: 'BHS Duty Engineer', priority: 'High', riskOrSla: 'Peak departure risk', nextAction: 'Verify overload reset history before closure' },
    ],
    evidence: [
      { label: 'Fault source evidence', status: 'Partial', note: 'Alarm snapshots exist for HVAC and BHS; lift vendor evidence is still pending.' },
      { label: 'Closure evidence', status: 'At risk', note: 'Two high-priority WOs need before/after photos and checklist signoff.' },
      { label: 'Customer report export', status: 'Ready after review', note: 'Open queue can feed daily maintenance exception report once evidence gaps are closed.' },
    ],
  },
  'emergency-work-orders': {
    insight: 'Emergency work orders must separate safety isolation, passenger/service exposure, immediate containment, and recovery target.',
    riskLevel: 'Critical',
    affectedService: 'Passenger safety, life-safety response, and critical building services',
    recommendedOwner: 'Duty Manager + Safety Supervisor',
    painPoints: [
      'Emergency priority is not enough; the team must know whether isolation is required before field access.',
      'Passenger-facing disruption can escalate faster than the asset repair itself when lift, fire, or baggage paths are affected.',
      'Recovery targets often fail when supervisor escalation and access control are not confirmed at dispatch time.',
    ],
    recommendations: [
      'Confirm safety isolation and access permit before technician arrival.',
      'Escalate passenger-impacting emergency work orders to Duty Manager immediately.',
      'Record containment action and recovery target in evidence before status downgrade.',
    ],
    decisionRows: [
      { item: 'Fire damper actuator fault', assetOrSystem: 'FLS-DMP-T1 / Life Safety', owner: 'Life Safety Team', priority: 'Critical', riskOrSla: 'Immediate isolation review', nextAction: 'Verify fire panel status and open supervisor bridge' },
      { item: 'Main chilled water pump trip', assetOrSystem: 'CHWP-01 / Cooling Plant', owner: 'HVAC Duty Lead', priority: 'Critical', riskOrSla: 'Terminal comfort loss', nextAction: 'Start standby pump and capture recovery evidence' },
      { item: 'Baggage screening lane outage', assetOrSystem: 'BHS-SCR-03 / Baggage Security', owner: 'BHS + Security', priority: 'Critical', riskOrSla: 'Departure queue risk', nextAction: 'Route passengers to alternate lane and log handoff' },
    ],
    evidence: [
      { label: 'Safety evidence', status: 'Required', note: 'Isolation state and supervisor acknowledgement must be attached.' },
      { label: 'Recovery evidence', status: 'In progress', note: 'Recovery target must include time, owner, and customer-facing service note.' },
      { label: 'Customer handoff', status: 'Required', note: 'Emergency closure needs customer-readable incident summary.' },
    ],
  },
  'fault-linked-work-orders': {
    insight: 'Fault-linked work orders need correlation across source alarm, repeated fault count, asset history, and suspected root cause before closure.',
    riskLevel: 'High',
    affectedService: 'Fault response quality and repeat maintenance reduction',
    recommendedOwner: 'Reliability Engineer',
    painPoints: [
      'Repeated alarms can create separate work orders while the real issue is one degrading asset or bad point mapping.',
      'Technicians may fix symptoms without checking asset history and related faults.',
      'Closure evidence is weak when the original alarm, correlated assets, and repair action are not linked.',
    ],
    recommendations: [
      'Group work orders by source alarm and correlated asset before dispatch.',
      'Review repeated fault count and asset age before selecting corrective action.',
      'Require source alarm evidence and repair evidence before closure approval.',
    ],
    decisionRows: [
      { item: 'Temperature sensor drift creates AHU calls', assetOrSystem: 'AHU-T2-04 / Sensor loop', owner: 'BMS Engineer', priority: 'High', riskOrSla: 'Repeat count 6', nextAction: 'Calibrate sensor and link trend evidence' },
      { item: 'Escalator vibration alarm repeats', assetOrSystem: 'ESC-T1-07 / Passenger movement', owner: 'Vendor Escalator Team', priority: 'High', riskOrSla: 'Repeat count 4', nextAction: 'Check bearing history and vendor inspection record' },
      { item: 'Pump differential pressure alarm', assetOrSystem: 'CHW-P-02 / Cooling plant', owner: 'HVAC Reliability', priority: 'Medium', riskOrSla: 'Trend worsening', nextAction: 'Compare with PM records and filter maintenance history' },
    ],
    evidence: [
      { label: 'Alarm-to-WO trace', status: 'Ready', note: 'Source alarm and work order linkage can support RCA.' },
      { label: 'Asset history', status: 'Review required', note: 'Repeated items need maintenance history before closure.' },
      { label: 'RCA report linkage', status: 'Available', note: 'Fault-linked records can feed reliability improvement report.' },
    ],
  },
  'pm-calendar': {
    insight: 'PM priority is shaped by critical system coverage, skipped PM, access windows, resource conflicts, and compliance exposure.',
    riskLevel: 'Medium',
    affectedService: 'Planned maintenance compliance and service continuity',
    recommendedOwner: 'PM Planner',
    painPoints: [
      'Skipped PM on critical systems can become emergency maintenance during peak operating hours.',
      'Access windows for airside, baggage, and tenant areas compete with technician availability.',
      'Checklist gaps make completed PM hard to defend during audit or customer review.',
    ],
    recommendations: [
      'Move critical PM into low-traffic access windows and lock owner assignment early.',
      'Escalate overdue PM affecting life-safety, cooling, or baggage systems.',
      'Confirm checklist readiness and vendor dependency before scheduled work.',
    ],
    decisionRows: [
      { item: 'Weekly AHU filter PM', assetOrSystem: 'Terminal 2 HVAC', owner: 'HVAC PM Team', priority: 'High', riskOrSla: 'Due today', nextAction: 'Schedule after passenger peak and attach checklist' },
      { item: 'Baggage conveyor inspection', assetOrSystem: 'BHS Line 3', owner: 'BHS Planner', priority: 'High', riskOrSla: 'Overdue 1 day', nextAction: 'Book access window with operations control' },
      { item: 'Generator load-test readiness', assetOrSystem: 'Emergency Power', owner: 'Electrical Team', priority: 'Medium', riskOrSla: 'Compliance watch', nextAction: 'Confirm vendor standby and test record template' },
    ],
    evidence: [
      { label: 'PM checklist', status: 'Required', note: 'Checklist must be ready before planned work starts.' },
      { label: 'Access window evidence', status: 'Partial', note: 'BHS and electrical PM require confirmed access window.' },
      { label: 'Compliance report', status: 'Ready after completion', note: 'PM completion can feed monthly compliance report.' },
    ],
  },
  'breach-risk': {
    insight: 'Breach risk is driven by access delay, missing owner escalation, customer-facing impact, and incomplete mitigation evidence.',
    riskLevel: 'High',
    affectedService: 'SLA commitments and customer trust',
    recommendedOwner: 'SLA Manager',
    painPoints: [
      'Aging timers do not explain breach cause unless owner, access delay, and mitigation action are visible together.',
      'Customer-impacting work can remain with a field engineer when it needs supervisor intervention.',
      'SLA mitigation is hard to prove without evidence of interim service restoration.',
    ],
    recommendations: [
      'Escalate all high-impact items with less than four hours remaining.',
      'Record access-delay reason and interim mitigation before SLA breach.',
      'Assign customer communication owner for passenger or tenant-facing service risk.',
    ],
    decisionRows: [
      { item: 'Cooling complaint at premium lounge', assetOrSystem: 'FCU-Lounge-05 / HVAC', owner: 'HVAC Supervisor', priority: 'High', riskOrSla: '1.5h remaining', nextAction: 'Escalate and provide temporary cooling mitigation' },
      { item: 'Baggage belt intermittent stop', assetOrSystem: 'BHS-Belt-17', owner: 'BHS Duty Lead', priority: 'Critical', riskOrSla: 'Breach likely', nextAction: 'Add second engineer and notify operations control' },
      { item: 'Access-controlled electrical room fault', assetOrSystem: 'LV Panel T3', owner: 'Electrical + Security', priority: 'High', riskOrSla: 'Access delay', nextAction: 'Confirm permit and record delay evidence' },
    ],
    evidence: [
      { label: 'Breach rationale', status: 'Required', note: 'Cause of delay and mitigation action must be captured.' },
      { label: 'Customer communication', status: 'Review required', note: 'Passenger or tenant-facing risk needs service note.' },
      { label: 'SLA report export', status: 'Ready', note: 'Breach-risk rows feed SLA exception report.' },
    ],
  },
  'repeated-failures': {
    insight: 'Repeated failures point to asset aging, bad point mapping, PM gaps, or vendor response quality; they need long-term corrective action, not just another work order.',
    riskLevel: 'High',
    affectedService: 'Reliability, maintenance cost, and recurring customer disruption',
    recommendedOwner: 'Reliability Manager',
    painPoints: [
      'Repeat faults increase MTTR and technician load while masking underlying asset degradation.',
      'Some repeated failures are caused by point quality or false alarms rather than physical failure.',
      'Vendor response can close the immediate call without reducing recurrence risk.',
    ],
    recommendations: [
      'Create reliability improvement action for assets with more than three repeats in the review window.',
      'Compare MTTR, MTBF, PM history, and source point quality before approving closure.',
      'Use vendor escalation when recurrence continues after corrective maintenance.',
    ],
    decisionRows: [
      { item: 'Escalator handrail speed mismatch', assetOrSystem: 'ESC-T1-07', owner: 'Reliability + Vendor', priority: 'High', riskOrSla: 'MTBF falling', nextAction: 'Open long-term vendor corrective action' },
      { item: 'AHU temperature high repeat', assetOrSystem: 'AHU-T2-04', owner: 'HVAC Reliability', priority: 'High', riskOrSla: 'Repeat count 6', nextAction: 'Check coil fouling and sensor drift together' },
      { item: 'Baggage belt overload repeat', assetOrSystem: 'BHS-Belt-17', owner: 'BHS Reliability', priority: 'Medium', riskOrSla: 'MTTR rising', nextAction: 'Review motor current trend and PM intervals' },
    ],
    evidence: [
      { label: 'Reliability evidence', status: 'Review required', note: 'MTTR, MTBF, source alarm, and work order history must be linked.' },
      { label: 'Improvement report', status: 'Available', note: 'Repeated failure items can feed reliability action report.' },
      { label: 'Customer value', status: 'High', note: 'Reducing recurrence lowers disruption and maintenance effort.' },
    ],
  },
}

const activeDeepSection = computed(() => ummsDeepSections[normalizeL3Id(route.query.l3, 'open-work-orders')] ?? defaultDeepSection)

function normalizeL3Id(value: unknown, defaultKey: string): string {
  const raw = typeof value === 'string' && value ? value : defaultKey
  const normalized = raw.replace(/-\d+$/, '')
  return normalized
}

const registryCustomerSection = computed<CustomerSection | undefined>(() => {
  const config = resolveL3RouteContentConfig(route.query.menu, route.query.l3)
  return config ? { ...config, targetTab: 'Overview' } : undefined
})

const activeCustomerSection = computed(
  () => customerSections[normalizeL3Id(route.query.l3, 'open-work-orders')] ?? registryCustomerSection.value ?? defaultCustomerSection,
)

const filters = reactive({
  status: '',
  priority: '',
  system: '',
  engineer: '',
  slaRisk: '',
})

const statusOptions = computed(() => uniqueValues('status'))
const priorityOptions = computed(() => uniqueValues('priority'))
const systemOptions = computed(() => uniqueValues('systemName'))
const engineerOptions = computed(() => uniqueValues('assignedEngineer'))
const slaRiskOptions = computed(() => uniqueValues('slaRisk'))

const filteredWorkOrders = computed(() => {
  const rows = workspace.value?.workOrders ?? []
  return rows.filter((row) => {
    return (!filters.status || row.status === filters.status)
      && (!filters.priority || row.priority === filters.priority)
      && (!filters.system || row.systemName === filters.system)
      && (!filters.engineer || row.assignedEngineer === filters.engineer)
      && (!filters.slaRisk || row.slaRisk === filters.slaRisk)
  })
})

const assignmentRows = computed(() => workspace.value?.engineerDispatch ?? [])
const preventiveRows = computed(() => workspace.value?.preventiveMaintenancePlans ?? [])
const predictiveRows = computed(() => workspace.value?.predictiveMaintenance ?? [])
const executionRows = computed(() => workspace.value?.maintenanceTasks ?? [])
const assetContextRows = computed(() => workspace.value?.assetContext ?? [])
const eventContextRows = computed(() => workspace.value?.eventContext ?? [])
const evidenceRows = computed(() => workspace.value?.evidenceTimeline ?? [])
const evidenceLinkageRows = computed(() => workspace.value?.evidenceLinkage ?? [])
const reportRows = computed(() => workspace.value?.reportLinkage ?? [])
const guardrailRows = computed(() => workspace.value?.guardrails ?? [])
const hmiContextRows = computed(() => (filteredWorkOrders.value.length ? filteredWorkOrders.value : workspace.value?.workOrders ?? []).slice(0, 6))
const partsVendorRows = computed(() =>
  (workspace.value?.correctiveMaintenanceFlow ?? []).map((row, index) => ({
    step: valueFromRecord(row, ['step', 'stage', 'item', 'action', 'name'], `Coordination item ${index + 1}`),
    owner: valueFromRecord(row, ['owner', 'team', 'vendor', 'assignedOwner'], 'Maintenance owner'),
    status: valueFromRecord(row, ['status', 'state', 'readiness'], 'Review'),
    evidence: valueFromRecord(row, ['evidence', 'evidenceStatus', 'vendorEvidence', 'notes'], 'Evidence review required'),
  })),
)
const customerAcceptanceRows = computed(() =>
  Object.entries(workspace.value?.customerAcceptance ?? {}).map(([key, value]) => ({
    label: labelFromKey(key),
    value: displayValue(value),
  })),
)
const closureReadinessRows = computed(() => [
  { label: 'Fault source evidence', status: evidenceRows.value.some((row) => row.faultSource) ? 'Available' : 'Review required', note: 'Source alarm, fault, or event evidence should support closure.' },
  { label: 'Technician notes', status: evidenceRows.value.some((row) => row.engineerUpdate) || executionRows.value.length > 0 ? 'Available' : 'Review required', note: 'Technician execution notes and checklist status are reviewed before closure.' },
  { label: 'Before / after evidence', status: evidenceRows.value.some((row) => row.attachmentReference) ? 'Available' : 'Review required', note: 'Attachment references should support field completion.' },
  { label: 'Parts used', status: partsVendorRows.value.length > 0 ? 'Review' : 'Gated', note: 'Parts usage is reviewed from corrective coordination data when available.' },
  { label: 'Vendor evidence', status: partsVendorRows.value.some((row) => /vendor/i.test(`${row.owner} ${row.evidence}`)) ? 'Review' : 'Gated', note: 'Vendor response evidence is required where vendor responsibility applies.' },
  { label: 'Supervisor review', status: workspace.value?.workOrders.some((row) => /pending evidence|at risk|watch/i.test(`${row.status} ${row.slaRisk}`)) ? 'Review required' : 'Ready', note: 'High-impact or repeated fault records require owner review.' },
  { label: 'Customer Sign-off', status: customerAcceptanceRows.value.length > 0 ? 'Review' : 'Gated', note: 'Customer sign-off is gated by closure evidence readiness.' },
])
const controlBoundaryRows = computed(() => [
  { label: 'Readonly projection active', value: String(workspace.value?.mode === 'read_only' || workspace.value?.workOrders.some((row) => row.readOnly) || false) },
  { label: 'Formal write disabled', value: String(!(workspace.value?.workOrderWrite || workspace.value?.taskWrite || workspace.value?.approvalWrite)) },
  { label: 'No runtime activation from Work Management', value: String(!(workspace.value?.runtimeActivation || workspace.value?.deviceControl || workspace.value?.edgeCommandExecution || workspace.value?.linkCommandExecution)) },
  { label: 'Asset quality gate may block formal overlay', value: 'blocked_by_data_quality' },
])
const decisionSignals = computed(() => {
  const rows = workspace.value?.workOrders ?? []
  const highPriority = rows.filter((row) => /critical|high/i.test(row.priority)).length
  const slaAtRisk = rows.filter((row) => /at risk|overdue|due today|watch/i.test(row.slaRisk)).length
  const faultLinked = rows.filter((row) => row.sourceFault || row.sourceEvent).length
  const closureMissing = rows.filter((row) => row.evidenceCount <= 0 || /pending evidence|review/i.test(row.status)).length
  return [
    { label: 'Open Work Orders', value: String(rows.filter((row) => !/closed/i.test(row.status)).length), note: 'Active maintenance queue' },
    { label: 'Emergency / High Priority', value: String(highPriority), note: 'Critical and high priority work' },
    { label: 'SLA At Risk', value: String(slaAtRisk), note: 'SLA exposure requiring review' },
    { label: 'Fault-linked Work Orders', value: String(faultLinked), note: 'Source event or alarm/fault linked' },
    { label: 'Closure Evidence Missing', value: String(closureMissing), note: 'Closure evidence requiring review' },
    { label: 'Customer Sign-off Pending', value: customerAcceptanceRows.value.length > 0 ? String(customerAcceptanceRows.value.length) : 'Gated', note: 'Gated by closure evidence readiness' },
  ]
})

function uniqueValues(field: keyof UmmsGaR2WorkOrder): string[] {
  const rows = workspace.value?.workOrders ?? []
  return [...new Set(rows.map((row) => String(row[field] ?? '')).filter(Boolean))].sort()
}

function tagType(value: string): 'success' | 'warning' | 'danger' | 'info' | 'primary' {
  const normalized = value.toLowerCase()
  if (normalized.includes('critical') || normalized.includes('overdue') || normalized.includes('at risk')) return 'danger'
  if (normalized.includes('high') || normalized.includes('due today') || normalized.includes('watch')) return 'warning'
  if (normalized.includes('closed') || normalized.includes('normal') || normalized.includes('on track')) return 'success'
  return 'info'
}

function displayValue(value: unknown): string {
  if (Array.isArray(value)) return value.map((item) => displayValue(item)).join(', ')
  if (typeof value === 'object' && value !== null) return Object.entries(value).map(([key, item]) => `${labelFromKey(key)}: ${displayValue(item)}`).join(' / ')
  if (value === undefined || value === null || value === '') return 'Review required'
  return String(value)
}

function valueFromRecord(row: Record<string, unknown>, keys: string[], defaultValue: string): string {
  for (const key of keys) {
    const value = row[key]
    if (value !== undefined && value !== null && value !== '') return displayValue(value)
  }
  return defaultValue
}

function labelFromKey(key: string): string {
  return key
    .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

function openReport(report: string) {
  reportToast.value = `${report} view prepared for read-only review.`
}

async function loadWorkspace() {
  loading.value = true
  apiError.value = ''
  try {
    workspace.value = await getUmmsGaR2Workspace()
  } catch (error) {
    apiError.value = error instanceof ApiError ? error.message : 'UMMS workspace data unavailable.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void loadWorkspace()
})

watch(activeCustomerSection, (section) => {
  activeTab.value = section.targetTab
}, { immediate: true })
</script>

<template>
  <section class="umms-page" v-loading="loading">
    <header class="workspace-head">
      <div>
        <p class="eyebrow">Work Management / MMS</p>
        <h1>Work Management / MMS Control Center</h1>
        <p class="summary">
          Maintenance execution across fault-linked work orders, preventive maintenance, assignment, SLA exposure,
          parts, vendor coordination and closure evidence.
        </p>
        <div class="selected-section">
          <span>Selected section</span>
          <strong>{{ activeCustomerSection.title }}</strong>
        </div>
      </div>
      <el-button type="primary" plain>{{ activeCustomerSection.primaryAction }}</el-button>
    </header>

    <el-alert
      v-if="apiError"
      class="section-gap"
      type="warning"
      show-icon
      :closable="false"
      :title="customerUnavailableMessage"
    />

    <template v-if="workspace">
      <section class="workflow-strip section-gap" aria-label="Workflow Readiness">
        <article v-for="(step, index) in workflowSteps" :key="step.label">
          <span>{{ index + 1 }}</span>
          <strong>{{ step.label }}</strong>
          <em>{{ step.note }}</em>
        </article>
      </section>

      <section class="decision-grid section-gap" aria-label="Decision Signal row">
        <article v-for="signal in decisionSignals" :key="signal.label" class="decision-card">
          <span>{{ signal.label }}</span>
          <strong>{{ signal.value }}</strong>
          <em>{{ signal.note }}</em>
        </article>
      </section>

      <section class="control-boundary section-gap">
        <div>
          <span>Control boundary</span>
          <strong>Readonly projection active</strong>
          <p>Formal write disabled. No runtime activation from Work Management. Asset quality gate may block formal overlay.</p>
        </div>
        <article v-for="item in controlBoundaryRows" :key="item.label">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
        </article>
      </section>

      <section class="deep-summary section-gap">
        <div>
          <span>Operational Insight</span>
          <strong>{{ activeDeepSection.insight }}</strong>
        </div>
        <div>
          <span>Risk Level</span>
          <el-tag :type="tagType(activeDeepSection.riskLevel)">{{ activeDeepSection.riskLevel }}</el-tag>
        </div>
        <div>
          <span>Affected Service</span>
          <strong>{{ activeDeepSection.affectedService }}</strong>
        </div>
        <div>
          <span>Recommended Owner</span>
          <strong>{{ activeDeepSection.recommendedOwner }}</strong>
        </div>
      </section>

      <section class="summary-grid section-gap">
        <article v-for="metric in activeCustomerSection.metrics" :key="metric.label" class="metric-card">
          <span>{{ metric.label }}</span>
          <strong>{{ metric.value }}</strong>
          <em>{{ metric.note }}</em>
        </article>
      </section>

      <div class="deep-grid section-gap">
        <section class="panel">
          <h2>Operational Pain Points</h2>
          <ul class="deep-list">
            <li v-for="item in activeDeepSection.painPoints" :key="item">{{ item }}</li>
          </ul>
        </section>
        <section class="panel">
          <h2>Recommended Actions</h2>
          <ul class="deep-list">
            <li v-for="item in activeDeepSection.recommendations" :key="item">{{ item }}</li>
          </ul>
        </section>
      </div>

      <el-table :data="activeDeepSection.decisionRows" stripe border class="section-gap">
        <el-table-column prop="item" label="Item" min-width="230" />
        <el-table-column prop="assetOrSystem" label="Asset / System" min-width="220" />
        <el-table-column prop="owner" label="Owner / Team" min-width="180" />
        <el-table-column prop="priority" label="Priority" min-width="130" />
        <el-table-column prop="riskOrSla" label="SLA / Risk" min-width="160" />
        <el-table-column prop="nextAction" label="Next Action" min-width="300" />
      </el-table>

      <section class="evidence-grid section-gap">
        <article v-for="item in activeDeepSection.evidence" :key="item.label" class="evidence-card">
          <span>{{ item.label }}</span>
          <el-tag :type="tagType(item.status)">{{ item.status }}</el-tag>
          <p>{{ item.note }}</p>
        </article>
      </section>

      <section class="summary-grid section-gap">
        <article v-for="card in workspace.overviewCards" :key="card.label" class="metric-card">
          <span>{{ card.label }}</span>
          <strong>{{ card.value }}</strong>
          <em>{{ card.status }}</em>
        </article>
      </section>

      <section class="metadata-strip section-gap">
        <div>
          <span>L1 / L2</span>
          <strong>{{ workspace.menu.l1 }} / {{ workspace.menu.l2.join(', ') }}</strong>
        </div>
        <div>
          <span>L3 content tabs</span>
          <strong>{{ tabs.join(' · ') }}</strong>
        </div>
      </section>

      <section class="panel section-gap">
        <div class="section-headline">
          <div>
            <p class="eyebrow">HMI / Asset / Fault Context</p>
            <h2>Fault-linked Work Order Context</h2>
          </div>
          <el-tag type="info">asset quality gate</el-tag>
        </div>
        <el-table :data="hmiContextRows" stripe border>
          <el-table-column prop="workOrderId" label="Work Order" min-width="150" fixed />
          <el-table-column prop="sourceEvent" label="Source Event" min-width="150" />
          <el-table-column prop="sourceFault" label="Source Alarm / Fault" min-width="230" />
          <el-table-column prop="linkedUhmiPanel" label="HMI Panel" min-width="230" />
          <el-table-column prop="assetName" label="Asset" min-width="190" />
          <el-table-column prop="systemName" label="System" min-width="150" />
          <el-table-column prop="location" label="Location" min-width="240" />
          <el-table-column prop="linkedUcdeEvidence" label="UCDE Evidence" min-width="190" />
          <el-table-column prop="linkedReport" label="Linked Report" min-width="190" />
          <el-table-column label="readOnly" min-width="120">
            <template #default="{ row }">{{ row.readOnly }}</template>
          </el-table-column>
        </el-table>
      </section>

      <el-tabs v-model="activeTab" type="card" class="section-gap workspace-tabs">
        <el-tab-pane v-for="tab in tabs" :key="tab" :label="tab" :name="tab">
          <template v-if="tab === 'Overview'">
            <div class="two-column">
              <section class="panel">
                <h2>Work Order Status</h2>
                <div v-for="item in workspace.statusDistribution" :key="item.key" class="bar-row">
                  <span>{{ item.key }}</span>
                  <strong>{{ item.count }}</strong>
                </div>
              </section>
              <section class="panel">
                <h2>Priority Distribution</h2>
                <div v-for="item in workspace.priorityDistribution" :key="item.key" class="bar-row">
                  <span>{{ item.key }}</span>
                  <el-tag :type="tagType(item.key)">{{ item.count }}</el-tag>
                </div>
              </section>
            </div>

            <div class="two-column section-gap">
              <section class="panel">
                <h2>SLA Risk List</h2>
                <div v-for="item in workspace.slaRiskList" :key="item.workOrderId" class="risk-row">
                  <div>
                    <strong>{{ item.workOrderId }}</strong>
                    <span>{{ item.title }}</span>
                  </div>
                  <el-tag :type="tagType(item.risk)">{{ item.risk }}</el-tag>
                </div>
              </section>
              <section class="panel">
                <h2>Fault-to-Work Order Conversion</h2>
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="Detected faults">{{ workspace.faultToWorkOrderConversion.detectedFaults }}</el-descriptions-item>
                  <el-descriptions-item label="Converted work orders">{{ workspace.faultToWorkOrderConversion.convertedWorkOrders }}</el-descriptions-item>
                  <el-descriptions-item label="Conversion rate">{{ workspace.faultToWorkOrderConversion.conversionRate }}</el-descriptions-item>
                  <el-descriptions-item label="Top source">{{ workspace.faultToWorkOrderConversion.topSource }}</el-descriptions-item>
                </el-descriptions>
              </section>
            </div>

            <section class="panel section-gap">
              <h2>Top Affected Systems</h2>
              <el-table :data="workspace.topAffectedSystems" stripe border>
                <el-table-column prop="systemName" label="System" min-width="160" />
                <el-table-column prop="openWorkOrders" label="Open Work Orders" min-width="160" />
                <el-table-column prop="criticality" label="Criticality" min-width="140" />
                <el-table-column prop="topAsset" label="Top Asset" min-width="220" />
              </el-table>
            </section>

            <section class="panel section-gap">
              <h2>Latest Maintenance Activities</h2>
              <div v-for="item in workspace.latestActivities" :key="`${item.time}-${item.workOrderId}`" class="timeline-row">
                <span>{{ item.time }}</span>
                <strong>{{ item.actor }}</strong>
                <p>{{ item.action }} · {{ item.workOrderId }} · {{ item.evidenceRef }}</p>
              </div>
            </section>
          </template>

          <template v-else-if="tab === 'Work Orders'">
            <section class="filter-strip">
              <el-select v-model="filters.status" clearable placeholder="Status">
                <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
              </el-select>
              <el-select v-model="filters.priority" clearable placeholder="Priority">
                <el-option v-for="item in priorityOptions" :key="item" :label="item" :value="item" />
              </el-select>
              <el-select v-model="filters.system" clearable placeholder="System">
                <el-option v-for="item in systemOptions" :key="item" :label="item" :value="item" />
              </el-select>
              <el-select v-model="filters.engineer" clearable placeholder="Assigned Engineer">
                <el-option v-for="item in engineerOptions" :key="item" :label="item" :value="item" />
              </el-select>
              <el-select v-model="filters.slaRisk" clearable placeholder="SLA Risk">
                <el-option v-for="item in slaRiskOptions" :key="item" :label="item" :value="item" />
              </el-select>
            </section>
            <el-table :data="filteredWorkOrders" stripe border class="section-gap">
              <el-table-column prop="workOrderId" label="WO ID" min-width="150" fixed />
              <el-table-column prop="title" label="Title" min-width="280" />
              <el-table-column prop="maintenanceType" label="Type" min-width="140" />
              <el-table-column prop="sourceEvent" label="Source Event" min-width="150" />
              <el-table-column prop="sourceFault" label="Source Alarm / Fault" min-width="220" />
              <el-table-column prop="assetName" label="Asset" min-width="190" />
              <el-table-column prop="systemName" label="System" min-width="150" />
              <el-table-column prop="location" label="Location" min-width="240" />
              <el-table-column label="Priority" min-width="120">
                <template #default="{ row }"><el-tag :type="tagType(row.priority)">{{ row.priority }}</el-tag></template>
              </el-table-column>
              <el-table-column prop="status" label="Status" min-width="140" />
              <el-table-column prop="slaDue" label="SLA Due" min-width="170" />
              <el-table-column prop="assignedEngineer" label="Assigned Engineer" min-width="170" />
              <el-table-column prop="createdTime" label="Created Time" min-width="170" />
              <el-table-column prop="evidenceCount" label="Evidence Count" min-width="140" />
              <el-table-column prop="linkedUhmiPanel" label="HMI Panel" min-width="230" />
              <el-table-column prop="linkedUcdeEvidence" label="UCDE Evidence" min-width="190" />
              <el-table-column prop="linkedReport" label="Linked Report" min-width="190" />
              <el-table-column label="readOnly" min-width="120">
                <template #default="{ row }">{{ row.readOnly }}</template>
              </el-table-column>
            </el-table>
          </template>

          <template v-else-if="tab === 'Preventive'">
            <el-table :data="preventiveRows" stripe border>
              <el-table-column prop="planId" label="Plan" min-width="160" />
              <el-table-column prop="planName" label="Scheduled PM Task" min-width="260" />
              <el-table-column prop="frequency" label="Frequency" min-width="130" />
              <el-table-column prop="nextDueDate" label="Next Due Date" min-width="160" />
              <el-table-column prop="assetGroup" label="Asset / System" min-width="220" />
              <el-table-column prop="systemName" label="System" min-width="170" />
              <el-table-column prop="complianceStatus" label="Compliance Status" min-width="170" />
              <el-table-column prop="checklistReadiness" label="Checklist Readiness" min-width="190" />
            </el-table>
          </template>

          <template v-else-if="tab === 'Predictive'">
            <el-table :data="predictiveRows" stripe border>
              <el-table-column prop="predictionId" label="Prediction" min-width="160" />
              <el-table-column prop="assetName" label="Asset" min-width="210" />
              <el-table-column prop="systemName" label="System" min-width="160" />
              <el-table-column prop="location" label="Location" min-width="220" />
              <el-table-column prop="failureRisk" label="Predicted Failure Risk" min-width="190" />
              <el-table-column prop="healthScore" label="Asset Health Score" min-width="170" />
              <el-table-column prop="trendSummary" label="Trend / Anomaly Summary" min-width="260" />
              <el-table-column prop="recommendedAction" label="Recommended Action" min-width="260" />
              <el-table-column prop="confidence" label="Confidence" min-width="130" />
              <el-table-column prop="severity" label="Severity" min-width="120" />
            </el-table>
          </template>

          <template v-else-if="tab === 'Assignments'">
            <el-table :data="assignmentRows" stripe border>
              <el-table-column prop="engineerName" label="Engineer" min-width="180" />
              <el-table-column prop="activeWorkOrders" label="Assigned Work Orders" min-width="190" />
              <el-table-column prop="skill" label="Skill / Discipline" min-width="220" />
              <el-table-column prop="availability" label="Shift Availability" min-width="180" />
              <el-table-column prop="siteZone" label="Zone" min-width="180" />
              <el-table-column prop="shift" label="Shift" min-width="140" />
              <el-table-column prop="escalationOwner" label="Escalation Owner" min-width="190" />
            </el-table>
          </template>

          <template v-else-if="tab === 'SLA & Aging'">
            <div class="two-column">
              <section class="panel">
                <h2>Aging Buckets</h2>
                <div v-for="item in workspace.slaAging.agingBuckets" :key="item.key" class="bar-row">
                  <span>{{ item.key }}</span>
                  <strong>{{ item.count }}</strong>
                </div>
              </section>
              <section class="panel">
                <h2>MTTR / Response</h2>
                <div class="large-metric">{{ workspace.slaAging.mttrHours }}h</div>
                <p>Average MTTR</p>
                <div class="large-metric small">{{ workspace.slaAging.averageResponseMinutes }}m</div>
                <p>Average response time</p>
              </section>
            </div>
            <section class="panel section-gap">
              <h2>Due Soon / Overdue</h2>
              <el-table :data="[...workspace.slaAging.dueSoon, ...workspace.slaAging.overdue]" stripe border>
                <el-table-column prop="workOrderId" label="Work Order" min-width="150" />
                <el-table-column prop="title" label="Title" min-width="280" />
                <el-table-column prop="priority" label="Priority" min-width="120" />
                <el-table-column prop="slaDue" label="SLA Due" min-width="170" />
                <el-table-column prop="owner" label="Owner" min-width="170" />
                <el-table-column prop="risk" label="Risk" min-width="140" />
              </el-table>
            </section>
          </template>

          <template v-else-if="tab === 'Execution'">
            <section class="panel">
              <div class="section-headline">
                <div>
                  <p class="eyebrow">Technician Execution</p>
                  <h2>Maintenance Task Execution</h2>
                </div>
                <el-tag type="info">readonly projection</el-tag>
              </div>
              <el-table :data="executionRows" stripe border>
                <el-table-column prop="taskId" label="Task" min-width="150" />
                <el-table-column prop="taskName" label="Checklist Item" min-width="260" />
                <el-table-column prop="workOrderId" label="Work Order" min-width="150" />
                <el-table-column prop="engineer" label="Assigned Engineer / Technician" min-width="220" />
                <el-table-column prop="role" label="Role" min-width="180" />
                <el-table-column prop="status" label="Status" min-width="150" />
                <el-table-column prop="checklistStatus" label="Checklist Status" min-width="180" />
                <el-table-column prop="evidenceRequired" label="Evidence" min-width="180" />
                <el-table-column prop="linkedAsset" label="Linked Asset" min-width="200" />
                <el-table-column prop="linkedEvent" label="Linked Event" min-width="180" />
              </el-table>
            </section>

            <section class="panel section-gap">
              <h2>Event and Asset Execution Context</h2>
              <div class="two-column">
                <el-table :data="eventContextRows" stripe border>
                  <el-table-column prop="eventId" label="Event" min-width="150" />
                  <el-table-column prop="severity" label="Severity" min-width="120" />
                  <el-table-column prop="sourceSystem" label="Source System" min-width="170" />
                  <el-table-column prop="linkedAsset" label="Linked Asset" min-width="190" />
                  <el-table-column prop="linkedWorkOrder" label="Linked Work Order" min-width="190" />
                  <el-table-column prop="evidenceLinked" label="Evidence" min-width="170" />
                  <el-table-column prop="status" label="Status" min-width="130" />
                </el-table>
                <el-table :data="assetContextRows" stripe border>
                  <el-table-column prop="assetName" label="Asset" min-width="190" />
                  <el-table-column prop="systemName" label="System" min-width="150" />
                  <el-table-column prop="category" label="Category" min-width="150" />
                  <el-table-column prop="location" label="Location" min-width="220" />
                  <el-table-column prop="zone" label="Zone" min-width="150" />
                </el-table>
              </div>
            </section>
          </template>

          <template v-else-if="tab === 'Parts / Vendor'">
            <section class="panel">
              <div class="section-headline">
                <div>
                  <p class="eyebrow">Parts / Vendor</p>
                  <h2>Parts / Vendor Coordination</h2>
                </div>
                <el-tag type="warning">formal write disabled</el-tag>
              </div>
              <el-alert
                v-if="partsVendorRows.length === 0"
                type="info"
                :closable="false"
                show-icon
                title="Parts / Vendor coordination is gated by corrective work order and closure evidence readiness."
                class="report-alert"
              />
              <el-table :data="partsVendorRows" stripe border>
                <el-table-column prop="step" label="Parts / Vendor Notes" min-width="260" />
                <el-table-column prop="owner" label="Vendor / Owner" min-width="210" />
                <el-table-column prop="status" label="Status" min-width="160" />
                <el-table-column prop="evidence" label="Vendor Evidence" min-width="300" />
              </el-table>
            </section>
          </template>

          <template v-else-if="tab === 'Evidence'">
            <section class="panel">
              <h2>Work Order Evidence Timeline</h2>
              <div v-for="item in evidenceRows" :key="`${item.time}-${item.workOrderId}`" class="evidence-row">
                <div>
                  <strong>{{ item.time }} · {{ item.workOrderId }}</strong>
                  <p>Fault source: {{ item.faultSource }}</p>
                  <p>Operator action: {{ item.operatorAction }}</p>
                  <p>Engineer update: {{ item.engineerUpdate }}</p>
                </div>
                <div>
                  <el-tag type="info">{{ item.attachmentReference }}</el-tag>
                  <el-tag type="success">{{ item.approvalClosureRecord }}</el-tag>
                </div>
              </div>
            </section>
            <section class="panel section-gap">
              <h2>Evidence Linkage</h2>
              <el-table :data="evidenceLinkageRows" stripe border>
                <el-table-column prop="linkage" label="Evidence Linkage" min-width="260" />
                <el-table-column prop="coverage" label="Coverage" min-width="280" />
                <el-table-column label="readOnly" min-width="120">
                  <template #default="{ row }">{{ row.readOnly }}</template>
                </el-table-column>
              </el-table>
            </section>
          </template>

          <template v-else-if="tab === 'Closure'">
            <section class="closure-grid">
              <article v-for="item in closureReadinessRows" :key="item.label" class="evidence-card">
                <span>{{ item.label }}</span>
                <el-tag :type="tagType(item.status)">{{ item.status }}</el-tag>
                <p>{{ item.note }}</p>
              </article>
            </section>

            <section class="panel section-gap">
              <div class="section-headline">
                <div>
                  <p class="eyebrow">Customer Sign-off</p>
                  <h2>Customer Acceptance Gate</h2>
                </div>
                <el-tag type="warning">evidence gated</el-tag>
              </div>
              <el-alert
                v-if="customerAcceptanceRows.length === 0"
                type="info"
                :closable="false"
                show-icon
                title="Customer sign-off is gated by closure evidence readiness."
                class="report-alert"
              />
              <el-table :data="customerAcceptanceRows" stripe border>
                <el-table-column prop="label" label="Customer Sign-off Field" min-width="240" />
                <el-table-column prop="value" label="Status / Value" min-width="360" />
              </el-table>
            </section>

            <section v-if="guardrailRows.length" class="panel section-gap">
              <h2>Operational Guardrails</h2>
              <ul class="deep-list">
                <li v-for="item in guardrailRows" :key="item">{{ item }}</li>
              </ul>
            </section>
          </template>

          <template v-else>
            <el-alert
              v-if="reportToast"
              type="success"
              :closable="false"
              show-icon
              :title="reportToast"
              class="report-alert"
            />
            <el-table :data="reportRows" stripe border>
              <el-table-column prop="report" label="Report" min-width="260" />
              <el-table-column prop="coverage" label="Coverage" min-width="320" />
              <el-table-column prop="status" label="Status" min-width="150" />
              <el-table-column label="Entry" min-width="180">
                <template #default="{ row }">
                  <el-button type="primary" size="small" @click="openReport(row.report)">
                    {{ row.actionLabel }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </template>
        </el-tab-pane>
      </el-tabs>
    </template>
  </section>
</template>

<style scoped>
.umms-page {
  min-height: 100%;
  padding: 20px;
  background: #f5f8f7;
  color: #1e2d2b;
}

.workspace-head {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 20px;
  border: 1px solid #dbe6e2;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 10px 24px rgb(38 65 58 / 8%);
}

.workspace-head h1 {
  margin: 4px 0 8px;
  font-size: 28px;
  line-height: 1.2;
  letter-spacing: 0;
}

.eyebrow,
.summary,
.metadata-strip span,
.metric-card span {
  margin: 0;
  color: #60736f;
}

.eyebrow {
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
}

.summary {
  max-width: 780px;
}

.selected-section {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-top: 12px;
}

.selected-section span {
  color: #60736f;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}

.selected-section strong {
  color: #0f766e;
}

.head-badges {
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start;
  justify-content: flex-end;
  gap: 8px;
}

.section-gap {
  margin-top: 16px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.workflow-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(145px, 1fr));
  gap: 8px;
}

.workflow-strip article {
  position: relative;
  min-height: 92px;
  padding: 12px;
  border: 1px solid #dbe6e2;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 8px 20px rgb(38 65 58 / 6%);
}

.workflow-strip span {
  display: inline-flex;
  width: 24px;
  height: 24px;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  background: #e2f2ee;
  color: #0f766e;
  font-size: 12px;
  font-weight: 800;
}

.workflow-strip strong {
  display: block;
  margin-top: 8px;
  color: #163b35;
  line-height: 1.25;
}

.workflow-strip em {
  display: block;
  margin-top: 6px;
  color: #60736f;
  font-size: 12px;
  font-style: normal;
}

.decision-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 12px;
}

.decision-card {
  padding: 14px;
  border: 1px solid #dbe6e2;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 8px 20px rgb(38 65 58 / 6%);
}

.decision-card span,
.control-boundary span {
  display: block;
  color: #60736f;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}

.decision-card strong {
  display: block;
  margin: 8px 0 4px;
  color: #087467;
  font-size: 24px;
  line-height: 1;
}

.decision-card em {
  color: #28746a;
  font-style: normal;
}

.control-boundary {
  display: grid;
  grid-template-columns: minmax(280px, 1.8fr) repeat(4, minmax(140px, 1fr));
  gap: 12px;
  padding: 14px;
  border: 1px solid #cfe2dc;
  border-left: 4px solid #0f766e;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 8px 20px rgb(38 65 58 / 6%);
}

.control-boundary strong {
  display: block;
  margin-top: 6px;
  color: #163b35;
}

.control-boundary p {
  margin: 8px 0 0;
  color: #60736f;
}

.deep-summary {
  display: grid;
  grid-template-columns: minmax(260px, 2fr) minmax(130px, 0.7fr) minmax(220px, 1.2fr) minmax(180px, 1fr);
  gap: 12px;
  padding: 14px;
  border: 1px solid #cfe2dc;
  border-left: 4px solid #247668;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 10px 24px rgb(38 65 58 / 8%);
}

.deep-summary span,
.evidence-card span {
  display: block;
  margin-bottom: 6px;
  color: #60736f;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}

.deep-summary strong {
  display: block;
  color: #163b35;
  line-height: 1.35;
}

.deep-grid,
.evidence-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.evidence-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.closure-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 12px;
}

.deep-list {
  margin: 0;
  padding-left: 18px;
  color: #29433f;
  line-height: 1.55;
}

.deep-list li + li {
  margin-top: 8px;
}

.evidence-card {
  padding: 14px;
  border: 1px solid #dbe6e2;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 8px 20px rgb(38 65 58 / 6%);
}

.evidence-card p {
  margin: 10px 0 0;
  color: #29433f;
  line-height: 1.45;
}

.metric-card,
.metadata-strip,
.workspace-tabs,
.panel {
  border: 1px solid #dbe6e2;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 8px 20px rgb(38 65 58 / 6%);
}

.metric-card {
  padding: 14px;
}

.metric-card strong {
  display: block;
  margin: 8px 0 4px;
  color: #087467;
  font-size: 26px;
  line-height: 1;
}

.metric-card em {
  color: #28746a;
  font-style: normal;
}

.metadata-strip {
  display: grid;
  grid-template-columns: minmax(240px, 1fr) minmax(0, 2fr);
  gap: 14px;
  padding: 14px;
}

.metadata-strip strong {
  display: block;
  margin-top: 4px;
}

.workspace-tabs {
  padding: 14px;
}

.two-column {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.panel {
  padding: 14px;
}

.panel h2 {
  margin: 0 0 12px;
  color: #193f3a;
  font-size: 17px;
  font-weight: 700;
}

.section-headline {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 12px;
}

.section-headline h2 {
  margin-bottom: 0;
}

.bar-row,
.risk-row,
.timeline-row,
.evidence-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-top: 1px solid #edf2f0;
}

.bar-row:first-of-type,
.risk-row:first-of-type,
.timeline-row:first-of-type,
.evidence-row:first-of-type {
  border-top: 0;
}

.risk-row span,
.timeline-row p,
.evidence-row p {
  display: block;
  margin: 4px 0 0;
  color: #60736f;
}

.filter-strip {
  display: grid;
  grid-template-columns: repeat(5, minmax(150px, 1fr));
  gap: 10px;
}

.large-metric {
  color: #087467;
  font-size: 34px;
  font-weight: 800;
}

.large-metric.small {
  margin-top: 12px;
  font-size: 26px;
}

.evidence-row > div:last-child {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-content: flex-start;
  gap: 8px;
}

.report-alert {
  margin-bottom: 12px;
}

@media (max-width: 900px) {
  .workspace-head,
  .metadata-strip,
  .two-column,
  .deep-summary,
  .deep-grid,
  .evidence-grid,
  .closure-grid,
  .control-boundary,
  .filter-strip {
    grid-template-columns: 1fr;
    flex-direction: column;
  }

  .head-badges {
    justify-content: flex-start;
  }
}
</style>
