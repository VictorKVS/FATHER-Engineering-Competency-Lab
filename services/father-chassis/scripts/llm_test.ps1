$ErrorActionPreference = "Stop"
$base = "http://localhost:8080"

Write-Host "[1/4] Probe local OpenAI-compatible model"
$probe = Invoke-RestMethod "$base/models/local/probe"
if (-not $probe.configured) {
    throw "Local LLM is not configured. Set FATHER_MODEL_BASE_URL and FATHER_MODEL_NAME in .env"
}
if (-not $probe.reachable) {
    throw "Local LLM endpoint is unreachable: $($probe.error)"
}
if (-not $probe.selected_present) {
    throw "Selected model '$($probe.model)' is not advertised by the endpoint"
}

Write-Host "[2/4] Run knowledge qualification"
$q = Invoke-RestMethod "$base/qualification/knowledge" -Method Post
if (-not $q.passed) {
    $q | ConvertTo-Json -Depth 10
    throw "Knowledge qualification failed"
}

Write-Host "[3/4] Validate trace and evidence"
if ([string]::IsNullOrWhiteSpace($q.trace_id)) { throw "trace_id missing" }
if ($q.evidence_count -lt 1) { throw "evidence missing" }

Write-Host "[4/4] Validate audit"
$audit = Invoke-RestMethod "$base/audit/$($q.trace_id)"
if ($audit.events.Count -lt 2) { throw "audit incomplete" }

Write-Host "`nLOCAL LLM QUALIFICATION: PASS"
$q | ConvertTo-Json -Depth 10
