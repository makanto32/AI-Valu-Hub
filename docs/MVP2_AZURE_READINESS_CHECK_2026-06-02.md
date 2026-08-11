# MVP2 Azure Readiness Check - 2026-06-02

## Resultado general

Parcialmente listo para Azure.

- MVP2 backend y frontend funcionales en local.
- Flujo E2E validado: login -> intake -> aclaracion -> chat tecnico -> architecture package -> upload de archivo de contexto.
- Imagenes Docker de API y frontend construyen correctamente.
- Infraestructura foundation compila en Bicep.

## Correcciones aplicadas durante validacion

1. Bug de upload admin de archivos de contexto corregido.
- Causa: colision de nombre entre funcion importada y endpoint en API.
- Archivo: api/app/main.py

2. Loop infinito de aclaraciones cuando solo existia 1 pregunta corregido.
- Causa: umbral de completitud/confiabilidad impedia avanzar de needs_clarification a business_viable en escenarios de una sola pregunta.
- Archivo: api/app/main.py

## Evidencia de validacion funcional

Validacion E2E ejecutada con TestClient:
- login_status: 200
- mine_status: 200
- clarify_q_status_1: 200
- clarify_submit_status_1: 200
- status_after_clarify: business_viable
- technical_questions_status: 200
- technical_chat_status: 200
- technical_recommendation: continue
- technical_feasibility: 86
- architecture_status: 200
- admin_upload_status: 200

## Evidencia de build/deploy readiness

- Frontend build: OK (vite build)
- Docker build API: OK
- Docker build frontend: OK
- Bicep compile: OK con warnings no bloqueantes

Warnings Bicep detectados:
- infra/main.bicep line 107: BCP334
- infra/main.bicep line 179: BCP334
- infra/main.bicep line 215: BCP318

## Brechas para publicar en Azure

1. Falta pipeline de despliegue de apps
- Actualmente existe foundation, pero no definiciones finales de Container Apps para API y frontend en IaC.

2. Configuracion de ACR
- main.parameters.json tiene enableAcr=true.
- Confirmar que la suscripcion permite ACR o cambiar a alternativa de despliegue.

3. Secrets y configuracion runtime
- Definir valores productivos para variables de storage, auth provider y DB path.
- Conectar secretos por Key Vault/Managed Identity.

4. Base de datos productiva
- SQLite funciona local y para demo, pero para productivo se recomienda PostgreSQL/SQL administrado.

## Go/No-Go recomendado

- GO tecnico para continuar con publicacion de MVP2 en entorno dev de Azure.
- NO-GO productivo hasta cerrar brechas de despliegue repetible, secretos y persistencia administrada.

## Siguientes pasos sugeridos

1. Crear definicion de Container Apps para API y frontend (con env vars y managed identity).
2. Definir workflow de build/push a ACR por tag MVP2.
3. Ajustar parametros de infra segun capacidad real de suscripcion.
4. Ejecutar smoke test post-deploy en endpoint health + flujo E2E basico.
