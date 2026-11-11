$ErrorActionPreference = "Stop"
$base = "http://localhost:8080"

$payload = @{
  query = "What is the purpose of FATHER Chassis and which capabilities are shared?"
  sources = @(
    @{
      source_id = "src-001"
      source_type = "document"
      title = "FATHER Architecture Note"
      uri = "local://father-architecture"
      content = "FATHER Chassis is a reusable production platform for agent systems. Shared capabilities include state, workflow, model routing, RAG, evidence, audit, guardrails and observability."
    },
    @{
      source_id = "src-002"
      source_type = "document"
      title = "Factory Note"
      uri = "local://factory-note"
      content = "FATHER Factory assembles products from a shared chassis, standard blocks, domain packs, agents and configuration."
    }
  )
} | ConvertTo-Json -Depth 10

Write-Host "[1/3] Run OSINT/Knowledge product workflow"
$result = Invoke-RestMethod "$base/products/osint/workflow" -Method Post -ContentType "application/json" -Body $payload
if (-not $result.passed) { throw "OSINT product workflow failed" }

Write-Host "[2/3] Validate product report"
if ($result.report.evidence_count -lt 1) { throw "Evidence missing" }
if ([string]::IsNullOrWhiteSpace($result.report.trace_id)) { throw "Trace missing" }
if ($result.audit_event_count -lt 2) { throw "Audit incomplete" }

Write-Host "[3/3] Validate source traceability"
if ($result.report.source_ids.Count -lt 1) { throw "Source IDs missing from evidence" }

Write-Host "`nOSINT PRODUCT QUALIFICATION: PASS"
$result | ConvertTo-Json -Depth 10
