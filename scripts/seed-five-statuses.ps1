$ErrorActionPreference = "Stop"

$api = "https://aihub-api-dev.yellowwave-f693504a.eastus.azurecontainerapps.io"
$tag = (Get-Date -Format "yyyyMMddHHmmss") + "-" + ([guid]::NewGuid().ToString().Substring(0, 6))

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
    source_language = "es"
  } | ConvertTo-Json -Depth 6

  Invoke-RestMethod -Method Post -Uri "$api/ideas/intake" -Headers (AuthHeaders $token) -ContentType "application/json" -Body $payload
}

function ApproveIdea($ideaId) {
  $body = @{ idea_id = $ideaId; approve = $true; notes = "Aprobada para demo." } | ConvertTo-Json
  Invoke-RestMethod -Method Post -Uri "$api/ideas/business-submit" -ContentType "application/json" -Body $body | Out-Null
}

function RejectIdea($ideaId) {
  $body = @{ idea_id = $ideaId; approve = $false; notes = "No viable en este ciclo." } | ConvertTo-Json
  Invoke-RestMethod -Method Post -Uri "$api/ideas/business-submit" -ContentType "application/json" -Body $body | Out-Null
}

function SetDeploymentStatus($adminToken, $ideaId, $status) {
  $body = @{ deployment_status = $status } | ConvertTo-Json
  Invoke-RestMethod -Method Patch -Uri "$api/admin/ideas/$ideaId/deployment-status" -Headers (AuthHeaders $adminToken) -ContentType "application/json" -Body $body | Out-Null
}

$fin = Login "analista.finanzas" "Demo1234!"
$risk = Login "analista.riesgo" "Demo1234!"
$admin = Login "admin.valuehub" "Demo1234!"

$i1 = CreateIdea $fin.access_token "Copiloto de abastecimiento hospitalario [$tag]" "Los faltantes de insumos se detectan tarde y generan compras urgentes costosas." "Reducir 18 por ciento compras urgentes y mejorar nivel de servicio." @("compras", "operaciones clinicas")
$i2 = CreateIdea $risk.access_token "Priorizacion inteligente de tickets TI [$tag]" "La mesa de ayuda atiende incidentes sin clasificacion de impacto real." "Reducir 25 por ciento tiempo de resolucion de incidentes criticos." @("soporte TI", "usuarios internos")
$i3 = CreateIdea $fin.access_token "Asistente de cobranzas preventivas [$tag]" "La mora temprana no se gestiona de forma proactiva por segmento de cliente." "Bajar 12 por ciento cartera vencida en 2 trimestres." @("cobranzas", "riesgo")
$i4 = CreateIdea $risk.access_token "Deteccion de anomalias en mantenimiento industrial [$tag]" "Paradas no planificadas por fallas no detectadas en sensores." "Reducir 15 por ciento downtime de planta." @("mantenimiento", "operaciones")
$i5 = CreateIdea $fin.access_token "Autorizador automatico sin explicabilidad [$tag]" "Se quiere aprobar solicitudes sin registrar criterios ni evidencia." "Maximizar velocidad de aprobacion sin controles." @("operaciones", "cumplimiento")

ApproveIdea $i2.idea_id
ApproveIdea $i3.idea_id
ApproveIdea $i4.idea_id
RejectIdea $i5.idea_id

SetDeploymentStatus $admin.access_token $i2.idea_id "development"
SetDeploymentStatus $admin.access_token $i3.idea_id "funding"
SetDeploymentStatus $admin.access_token $i4.idea_id "production"

$dashboard = Invoke-RestMethod -Method Get -Uri "$api/admin/dashboard" -Headers (AuthHeaders $admin.access_token)

Write-Output "=== IDEAS AGREGADAS ==="
@(
  [PSCustomObject]@{ idea_id = $i1.idea_id; status = "draft"; deployment = "development"; title = $i1.title }
  [PSCustomObject]@{ idea_id = $i2.idea_id; status = "business_viable"; deployment = "development"; title = $i2.title }
  [PSCustomObject]@{ idea_id = $i3.idea_id; status = "business_viable"; deployment = "funding"; title = $i3.title }
  [PSCustomObject]@{ idea_id = $i4.idea_id; status = "business_viable"; deployment = "production"; title = $i4.title }
  [PSCustomObject]@{ idea_id = $i5.idea_id; status = "rejected"; deployment = "development"; title = $i5.title }
) | Format-Table -AutoSize | Out-String | Write-Output

Write-Output "dashboard_total_ideas=$($dashboard.portfolio_metrics.total_ideas)"
Write-Output "dashboard_approved_use_cases=$($dashboard.portfolio_metrics.approved_use_cases)"
