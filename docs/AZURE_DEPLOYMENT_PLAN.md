# Azure Deployment Plan

## Objetivo
Provisionar la base cloud-native de AI Opportunity Hub en Azure para publicar imagenes validadas localmente en Container Apps a medida que avancemos por MVPs.

## Decision de arquitectura
- El runtime de agentes sera Microsoft Foundry.
- Container Apps alojara frontend, API y workers auxiliares.
- La API actuara como capa de orquestacion entre UI, persistencia y agentes en Foundry.

## Foundation actual
- IaC en Bicep para recursos compartidos.
- Dockerfile para API FastAPI.
- Dockerfile para frontend React/Vite servido con Nginx.
- Base de secretos y configuracion para integrar Foundry posteriormente.
- Despliegue pensado para `az containerapp up --source` cuando ACR no este disponible en la suscripcion.

## Flujo esperado
1. Validar localmente frontend y API.
2. Construir imagenes versionadas por MVP.
3. Publicar imagenes en Azure Container Registry.
4. Crear o actualizar Container Apps apuntando al tag validado.
5. Repetir en cada MVP aprobado.

## Siguiente paso despues de foundation
- Crear scripts para build/push de imagenes.
- Crear definiciones de Container App para `frontend` y `api`.
- Conectar secretos y endpoints desde Key Vault y PostgreSQL/Storage.
- Integrar cliente de Microsoft Foundry y registrar los agentes especializados por etapa.