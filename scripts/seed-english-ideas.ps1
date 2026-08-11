$ErrorActionPreference = "Stop"

$api = "https://aihub-api-dev.yellowwave-f693504a.eastus.azurecontainerapps.io"
$tag = (Get-Date -Format "yyyyMMddHHmmss") + "-EN-" + ([guid]::NewGuid().ToString().Substring(0, 6))

function Login($username, $password) {
  $body = @{ username = $username; password = $password } | ConvertTo-Json
  Invoke-RestMethod -Method Post -Uri "$api/auth/login" -ContentType "application/json" -Body $body
}

function AuthHeaders($token) {
  @{ Authorization = "Bearer $token" }
}

function CreateIdea($token, $title, $problem, $value, $users) {
  $payload = @{
    tenant_id = "contoso-demo"
    title = $title
    problem_statement = $problem
    expected_value = $value
    affected_users = $users
    source_language = "en"
  } | ConvertTo-Json -Depth 6

  Invoke-RestMethod -Method Post -Uri "$api/ideas/intake" -Headers (AuthHeaders $token) -ContentType "application/json" -Body $payload
}

function ApproveIdea($ideaId) {
  $body = @{ idea_id = $ideaId; approve = $true; notes = "Approved for executive demo." } | ConvertTo-Json
  Invoke-RestMethod -Method Post -Uri "$api/ideas/business-submit" -ContentType "application/json" -Body $body | Out-Null
}

function RejectIdea($ideaId) {
  $body = @{ idea_id = $ideaId; approve = $false; notes = "Rejected for current cycle due to policy concerns." } | ConvertTo-Json
  Invoke-RestMethod -Method Post -Uri "$api/ideas/business-submit" -ContentType "application/json" -Body $body | Out-Null
}

function SetDeploymentStatus($adminToken, $ideaId, $status) {
  $body = @{ deployment_status = $status } | ConvertTo-Json
  Invoke-RestMethod -Method Patch -Uri "$api/admin/ideas/$ideaId/deployment-status" -Headers (AuthHeaders $adminToken) -ContentType "application/json" -Body $body | Out-Null
}

$fin = Login "analista.finanzas" "Demo1234!"
$risk = Login "analista.riesgo" "Demo1234!"
$admin = Login "admin.valuehub" "Demo1234!"

$i1 = CreateIdea $fin.access_token "AI assistant for insurance claim triage [$tag]" "Claim handlers spend too much time manually sorting incoming requests by urgency and complexity." "Reduce first-response time by 28 percent and improve SLA compliance in 90 days." @("claims", "operations")
$i2 = CreateIdea $risk.access_token "Smart prioritization for incident response [$tag]" "Security incidents are queued without clear business impact scoring." "Cut critical incident resolution time by 22 percent." @("security", "IT operations")
$i3 = CreateIdea $fin.access_token "Automated finance close anomaly checks [$tag]" "Month-end close requires repetitive spreadsheet checks that delay reporting." "Reduce close cycle effort by 30 percent and improve audit readiness." @("finance", "controlling")
$i4 = CreateIdea $risk.access_token "Opaque auto-approval for high-risk transactions [$tag]" "The proposal seeks automatic approvals with no explainability trail." "Increase throughput regardless of governance constraints." @("risk", "compliance")

ApproveIdea $i2.idea_id
ApproveIdea $i3.idea_id
RejectIdea $i4.idea_id

SetDeploymentStatus $admin.access_token $i2.idea_id "development"
SetDeploymentStatus $admin.access_token $i3.idea_id "funding"

$dashboard = Invoke-RestMethod -Method Get -Uri "$api/admin/dashboard" -Headers (AuthHeaders $admin.access_token)

Write-Output "=== ENGLISH IDEAS INGESTED ==="
@(
  [PSCustomObject]@{ idea_id = $i1.idea_id; status = "draft"; deployment = "development"; source_language = "en"; title = $i1.title }
  [PSCustomObject]@{ idea_id = $i2.idea_id; status = "business_viable"; deployment = "development"; source_language = "en"; title = $i2.title }
  [PSCustomObject]@{ idea_id = $i3.idea_id; status = "business_viable"; deployment = "funding"; source_language = "en"; title = $i3.title }
  [PSCustomObject]@{ idea_id = $i4.idea_id; status = "rejected"; deployment = "development"; source_language = "en"; title = $i4.title }
) | Format-Table -AutoSize | Out-String | Write-Output

Write-Output "dashboard_total_ideas=$($dashboard.portfolio_metrics.total_ideas)"
Write-Output "dashboard_approved_use_cases=$($dashboard.portfolio_metrics.approved_use_cases)"
