import { InspectionStatus, Prisma, PrismaClient, SlaStatus, WorkOrderStatus } from '@prisma/client'

/**
 * Additional realistic UAT/demo data for UFMS Commercial V1.0 reports and workflows.
 */
export async function seedUatEnhancements(
  prisma: PrismaClient,
  seedNow: Date,
  parseTimestamp: (value: string) => Date,
) {
  await prisma.workOrder.update({
    where: { workOrderId: 'WO-001' },
    data: {
      metadata: {
        requesterFeedback: {
          rating: 4,
          comment: 'Technician responded quickly; awaiting final battery replacement.',
          submittedBy: 'requester',
          submittedAt: seedNow.toISOString(),
        },
      } as Prisma.InputJsonValue,
      requesterConfirmedAt: parseTimestamp('2026-06-02 12:00'),
      requesterConfirmedBy: 'requester',
    },
  })

  const breachedWoId = 'WO-UAT-001'
  const existingBreached = await prisma.workOrder.findUnique({ where: { workOrderId: breachedWoId } })
  if (!existingBreached) {
    await prisma.workOrder.create({
      data: {
        workOrderId: breachedWoId,
        workOrderNo: 'WO-2026-UAT-001',
        problemId: 'PRB-001',
        episodeId: 'EPI-001',
        assetId: 'AST-004',
        locationId: 'LOC-002',
        slaPolicyId: 'SLA-001',
        contractorId: 'CTR-002',
        title: 'UPS battery replacement — SLA breach scenario',
        assetLabel: 'AST-004',
        assignedTo: 'technician',
        priority: 'P1',
        status: WorkOrderStatus.IN_PROGRESS,
        slaStatus: SlaStatus.BREACHED,
        dueDate: parseTimestamp('2026-06-01 18:00'),
        slaDueAt: parseTimestamp('2026-06-01 14:00'),
        slaBreachedAt: parseTimestamp('2026-06-01 14:30'),
        createdAt: parseTimestamp('2026-06-01 10:00'),
        updatedAt: seedNow,
      },
    })
  }

  await prisma.inspectionRecord.createMany({
    data: [
      {
        inspectionRecordId: 'INSP-REC-002',
        inspectionPlanId: 'INSP-PLAN-001',
        assetId: 'AST-004',
        locationId: 'LOC-002',
        recordCode: 'INSP-2026-05-UPS',
        status: InspectionStatus.COMPLETED,
        scheduledAt: parseTimestamp('2026-05-01 09:00'),
        startedAt: parseTimestamp('2026-05-01 09:10'),
        completedAt: parseTimestamp('2026-05-01 09:45'),
        performedBy: 'USR-005',
        results: { 'BATT-VOLT': { value: true }, 'BATT-TEMP': { value: 28.5 } } as Prisma.InputJsonValue,
        createdAt: seedNow,
        updatedAt: seedNow,
      },
      {
        inspectionRecordId: 'INSP-REC-003',
        inspectionPlanId: 'INSP-PLAN-001',
        assetId: 'AST-004',
        locationId: 'LOC-002',
        recordCode: 'INSP-2026-04-UPS',
        status: InspectionStatus.MISSED,
        scheduledAt: parseTimestamp('2026-04-01 09:00'),
        createdAt: seedNow,
        updatedAt: seedNow,
      },
    ],
    skipDuplicates: true,
  })

  await prisma.auditLog.createMany({
    data: [
      {
        auditId: 'AUD-UFMS-001',
        entityType: 'work_order',
        entityId: 'WO-001',
        module: 'ufms',
        action: 'work_order_started',
        actor: 'operator',
        timestamp: parseTimestamp('2026-06-02 11:00'),
        hash: 'ufms-audit-hash-001',
        createdAt: seedNow,
        updatedAt: seedNow,
      },
      {
        auditId: 'AUD-UFMS-002',
        entityType: 'rfq_compliance',
        entityId: 'export',
        module: 'ufms',
        action: 'rfq_compliance_exported',
        actor: 'fmmanager',
        timestamp: parseTimestamp('2026-06-02 09:00'),
        hash: 'ufms-audit-hash-002',
        createdAt: seedNow,
        updatedAt: seedNow,
      },
      {
        auditId: 'AUD-UFMS-003',
        entityType: 'report',
        entityId: 'daily-fault-summary',
        module: 'ufms',
        action: 'report_exported',
        actor: 'auditor',
        timestamp: parseTimestamp('2026-06-02 09:30'),
        hash: 'ufms-audit-hash-003',
        createdAt: seedNow,
        updatedAt: seedNow,
      },
    ],
    skipDuplicates: true,
  })

  await prisma.rfqComplianceItem.updateMany({
    where: { requirementCode: 'RFQ-OPS-DASHBOARD' },
    data: {
      metadata: { evidenceRef: 'docs/ufms/rfq/RFQ-001-dashboard-coverage.pdf' } as Prisma.InputJsonValue,
    },
  })
}
