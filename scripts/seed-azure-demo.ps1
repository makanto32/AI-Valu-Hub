$ErrorActionPreference = "Stop"

$api = "https://aihub-api-dev.yellowwave-f693504a.eastus.azurecontainerapps.io"
$seedTag = Get-Date -Format "yyyyMMddHHmmss"

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
  } | ConvertTo-Json -Depth 5

  try {
    Invoke-RestMethod -Method Post -Uri "$api/ideas/intake" -Headers (AuthHeaders $token) -ContentType "application/json" -Body $payload
  }
  catch {
    $detail = $_.ErrorDetails.Message
    if ($detail -match "idea_id=([0-9a-fA-F-]{36})") {
      $existingId = $matches[1]
      Write-Output "Idea duplicada detectada, reutilizando: $existingId"
      return Invoke-RestMethod -Method Get -Uri "$api/ideas/$existingId" -Headers (AuthHeaders $token)
    }
    throw
  }
}

function EnsureBusinessViable($token, $idea) {
  $current = $idea

  if ($current.status -eq "needs_clarification") {
    $q = Invoke-RestMethod -Method Get -Uri "$api/ideas/$($current.idea_id)/clarification-questions" -Headers (AuthHeaders $token)
    $answers = @()
    foreach ($item in $q.questions) {
      $answerText = if ($item.suggested_answers.Count -gt 0) { $item.suggested_answers[0] } else { "Contamos con KPI y baseline historico con validacion de negocio y cumplimiento." }
      $answers += @{ question_id = $item.question_id; answer = $answerText }
    }
    $clarifyBody = @{ answers = $answers } | ConvertTo-Json -Depth 8
    $current = Invoke-RestMethod -Method Post -Uri "$api/ideas/$($current.idea_id)/clarify" -Headers (AuthHeaders $token) -ContentType "application/json" -Body $clarifyBody
  }

  if ($current.status -ne "business_viable") {
    $bs = @{ idea_id = $current.idea_id; approve = $true; notes = "Aprobada para demo ejecutiva en Azure." } | ConvertTo-Json
    $current = Invoke-RestMethod -Method Post -Uri "$api/ideas/business-submit" -ContentType "application/json" -Body $bs
  }

  $current
}

function RunTechnicalAndArchitecture($token, $ideaId) {
  $q = $null
  try {
    $q = Invoke-RestMethod -Method Get -Uri "$api/ideas/$ideaId/technical-questions" -Headers (AuthHeaders $token)
  }
  catch {
    $detail = $_.ErrorDetails.Message
    if ($detail -match "ya cuenta con validacion tecnica") {
      Write-Output "Validacion tecnica ya existente para $ideaId, se omite chat tecnico"
      try {
        $null = Invoke-RestMethod -Method Post -Uri "$api/ideas/$ideaId/architecture-package" -Headers (AuthHeaders $token)
      }
      catch {
        $archDetail = $_.ErrorDetails.Message
        if ($archDetail -match "ya cuenta con validacion tecnica" -or $archDetail -match "No se puede generar arquitectura" -or $archDetail -match "Primero debes completar") {
          Write-Output "Arquitectura no aplicable o ya existente para $ideaId"
          return
        }
        throw
      }
      return
    }
    throw
  }

  $answers = @()

  foreach ($item in $q.questions) {
    $answerText = if ($item.suggested_answers.Count -gt 0) { $item.suggested_answers[0] } else { "Integracion via API REST, cifrado en transito y datos anonimizados para piloto." }
    $answers += @{ question_id = $item.question_id; answer = $answerText }
  }

  $chatBody = @{ answers = $answers } | ConvertTo-Json -Depth 8
  $null = Invoke-RestMethod -Method Post -Uri "$api/ideas/$ideaId/technical-chat" -Headers (AuthHeaders $token) -ContentType "application/json" -Body $chatBody
  try {
    $null = Invoke-RestMethod -Method Post -Uri "$api/ideas/$ideaId/architecture-package" -Headers (AuthHeaders $token)
  }
  catch {
    $archDetail = $_.ErrorDetails.Message
    if ($archDetail -match "ya cuenta con validacion tecnica" -or $archDetail -match "No se puede generar arquitectura") {
      Write-Output "Arquitectura no aplicable o ya existente para $ideaId"
      return
    }
    throw
  }
}

function SetDeploymentStatus($adminToken, $ideaId, $status) {
  $body = @{ deployment_status = $status } | ConvertTo-Json
  try {
    Invoke-RestMethod -Method Patch -Uri "$api/admin/ideas/$ideaId/deployment-status" -Headers (AuthHeaders $adminToken) -ContentType "application/json" -Body $body
  }
  catch {
    $detail = $_.ErrorDetails.Message
    if ($detail -match "Not Found") {
      Write-Output "Endpoint de deployment-status no disponible en este backend, se omite actualización para $ideaId"
      return $null
    }
    throw
  }
}

$fin = Login "analista.finanzas" "Demo1234!"
$risk = Login "analista.riesgo" "Demo1234!"
$admin = Login "admin.valuehub" "Demo1234!"

$ideaA = CreateIdea $fin.access_token "Copiloto KYC para onboarding digital [$seedTag]" "El equipo tarda demasiado en validar expedientes KYC y hay retrabajo por inconsistencias documentales." "Reducir 25% el tiempo promedio de onboarding y bajar 15% los reprocesos en 90 dias." @("operaciones", "riesgo", "cumplimiento")
$ideaB = CreateIdea $fin.access_token "Deteccion temprana de fraude en transferencias [$seedTag]" "Se identifican patrones de fraude de forma tardia y se elevan reclamos de clientes." "Disminuir 20% perdidas por fraude y mejorar tiempo de respuesta en alertas criticas." @("riesgo", "fraude", "mesa de monitoreo")
$ideaC = CreateIdea $risk.access_token "Asistente regulatorio para auditorias internas [$seedTag]" "La preparacion de evidencias para auditoria consume mucho tiempo y depende de expertos puntuales." "Reducir 30% horas de preparacion de auditoria y mejorar trazabilidad de evidencias." @("cumplimiento", "auditoria", "riesgo operacional")
$ideaD = CreateIdea $risk.access_token "Scoring crediticio opaco sin explicabilidad [$seedTag]" "Se desea acelerar aprobaciones de credito sin detallar factores de decision al cliente." "Aumentar 18% conversion en creditos de consumo en 60 dias." @("riesgo credito", "negocio retail")

$ideaA = EnsureBusinessViable $fin.access_token $ideaA
$ideaB = EnsureBusinessViable $fin.access_token $ideaB
$ideaC = EnsureBusinessViable $risk.access_token $ideaC

RunTechnicalAndArchitecture $fin.access_token $ideaA.idea_id
RunTechnicalAndArchitecture $fin.access_token $ideaB.idea_id
RunTechnicalAndArchitecture $risk.access_token $ideaC.idea_id

$null = SetDeploymentStatus $admin.access_token $ideaA.idea_id "production"
$null = SetDeploymentStatus $admin.access_token $ideaB.idea_id "funding"
$null = SetDeploymentStatus $admin.access_token $ideaC.idea_id "development"

$rejectBody = @{ idea_id = $ideaD.idea_id; approve = $false; notes = "Rechazada en demo por riesgo de explicabilidad." } | ConvertTo-Json
$ideaD = Invoke-RestMethod -Method Post -Uri "$api/ideas/business-submit" -ContentType "application/json" -Body $rejectBody

$dashboard = $null
try {
  $dashboard = Invoke-RestMethod -Method Get -Uri "$api/admin/dashboard" -Headers (AuthHeaders $admin.access_token)
}
catch {
  $detail = $_.ErrorDetails.Message
  if ($detail -match "Not Found") {
    Write-Output "Endpoint /admin/dashboard no disponible en este backend"
  }
  else {
    throw
  }
}
$ideas = Invoke-RestMethod -Method Get -Uri "$api/ideas"

Write-Output "Seed completado en Azure API"
Write-Output "Ideas creadas: $($ideaA.idea_id), $($ideaB.idea_id), $($ideaC.idea_id), $($ideaD.idea_id)"
Write-Output "Estados despliegue: $($ideaA.title)=production | $($ideaB.title)=funding | $($ideaC.title)=development"
if ($null -ne $dashboard) {
  Write-Output "Resumen dashboard: approved_use_cases=$($dashboard.approved_use_cases), estimated_monthly_token_cost_usd=$($dashboard.estimated_monthly_token_cost_usd), ideas_total=$($ideas.Count)"
}
else {
  Write-Output "Resumen dataset: ideas_total=$($ideas.Count)"
}
