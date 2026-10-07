# Changelog

## v1.0.0 — 2026-10-07
- Ponte Jev ↔ OpenAI Decisions API (`ponte/`, só biblioteca padrão): conversão de requisições nos dois sentidos, normalização de respostas, comparação e política de revisão.
- Modo `demo` offline com respostas simuladas; modo `ao-vivo` só com `PERMITIR_API=1` (ainda não executado).
- Exemplos autorais: plantão pet, incidente de checkout, devolução com foto.
- `docs/comparacao.md` com fonte por linha e `docs/prompt-integracao.md`.
- 12 testes (`python3 -m unittest discover -s testes`).
- Guia PT/EN/ES em `guia/`.
