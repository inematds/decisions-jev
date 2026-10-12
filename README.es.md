# ⚖️ Decisions × Jev

[![Decisions × Jev](guia/assets/banner-es.jpg)](https://inematds.github.io/decisions-jev/guia/es/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## Qué es

OpenAI lanzó la Decisions API: envías un texto o una foto con preguntas cerradas y recibes solo la respuesta — sí/no, una opción de tu lista o una nota — con la probabilidad, sin texto corrido. Es la misma idea de Jev, el modelo de decisión que INEMA ya estudia. Este proyecto explica las diferencias con la fuente de cada dato y trae un puente en Python que convierte las preguntas de un formato a otro y compara las respuestas. Para estudiar basta con leer y ejecutar la demostración sin conexión; para llamar a las APIs de verdad, necesitas tus propias claves.

## 📖 Guía de uso

Guía completa (landing + paso a paso): **https://inematds.github.io/decisions-jev/guia/es/**

## En 30 segundos

| | OpenAI Decisions API | Jev | Microsoft-Decision-1 |
|---|---|---|---|
| Sí/no | `predicate` | `noul` | sí/no |
| Opción de la lista | `choice` + `choices` | `choice` + `criteria` | opción múltiple |
| Nota | `score` + `levels` | `score` + `criteria` | nota y rúbrica |
| Imagen | sí (base64) | no | no (solo texto, hasta 32.768 tokens) |
| Rechazo | `refusal` | no existe | no informado |
| Precio de entrada | US$ 0,10 / 1M de tokens | US$ 0,042 / 1M de tokens | US$ 0,042 / 1M de tokens (salida gratis) |

Fuentes, números de los videos y cuándo usar cada uno: [docs/comparacao.md (en portugués)](docs/comparacao.md).

## Uso

```bash
python3 -m ponte demo                                              # offline, respuestas simuladas
python3 -m ponte converter jev-openai exemplos/plantao-pet.jev.json [--imagem foto.jpg]
python3 -m ponte converter openai-jev exemplos/devolucao-foto.openai.json
PERMITIR_API=1 python3 -m ponte ao-vivo exemplos/plantao-pet.jev.json  # llamada pagada, en ambos
python3 -m unittest discover -s testes                             # 12 pruebas
```

El modo `ao-vivo` lee `OPENAI_API_KEY` y `OPENROUTER_API_KEY` del entorno (o de un `.env` en `PONTE_ENV`) y aún no ha sido ejecutado por INEMA. Prompt para que tu agente integre la API: [docs/prompt-integracao.md (en portugués)](docs/prompt-integracao.md).

## Estructura

- `ponte/` — conversión, normalización, comparación y CLI (solo biblioteca estándar).
- `exemplos/` — solicitudes de autoría propia; `exemplos/simulado/` — respuestas simuladas de la demo.
- `docs/` — comparación con fuente y prompt de integración.
- `guia/` — landing + guía en PT/EN/ES.

## Relacionados

- [Área JEV en INEMA Eventos](https://eventos.inema.pro/jev/) · [proyecto jev](https://github.com/inematds/jev) · [curso JEV](https://inematds.github.io/jev-curso/)

Proyecto educativo independiente. Jev es un modelo de TypeSafe; Decisions API es un producto de OpenAI. Licencia MIT.
