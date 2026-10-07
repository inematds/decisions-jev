# ⚖️ Decisions × Jev

[![Decisions × Jev](guia/assets/banner.jpg)](https://inematds.github.io/decisions-jev/guia/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## O que é

A OpenAI lançou a Decisions API: você manda um texto ou uma foto com perguntas fechadas e recebe só a resposta — sim/não, uma opção da sua lista ou uma nota — com a probabilidade, sem texto corrido. É a mesma ideia do Jev, o modelo de decisão que o INEMA já estuda. Este projeto explica as diferenças com a fonte de cada informação e traz uma ponte em Python que converte as perguntas de um formato para o outro e compara as respostas. Para estudar basta ler e rodar a demonstração offline; para chamar as APIs de verdade, você precisa das suas chaves.

## 📖 Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/decisions-jev/guia/**

## Em 30 segundos

| | OpenAI Decisions API | Jev |
|---|---|---|
| Sim/não | `predicate` | `noul` |
| Opção da lista | `choice` + `choices` | `choice` + `criteria` |
| Nota | `score` + `levels` | `score` + `criteria` |
| Imagem | sim (base64) | não |
| Recusa | `refusal` | não existe |
| Preço de entrada | US$ 0,10 / 1M tokens | US$ 0,042 / 1M tokens |

Fontes, números dos vídeos e quando usar cada um: [docs/comparacao.md](docs/comparacao.md).

## Uso

```bash
python3 -m ponte demo                                              # offline, respostas simuladas
python3 -m ponte converter jev-openai exemplos/plantao-pet.jev.json [--imagem foto.jpg]
python3 -m ponte converter openai-jev exemplos/devolucao-foto.openai.json
PERMITIR_API=1 python3 -m ponte ao-vivo exemplos/plantao-pet.jev.json  # chamada paga, nos dois
python3 -m unittest discover -s testes                             # 12 testes
```

O modo `ao-vivo` lê `OPENAI_API_KEY` e `OPENROUTER_API_KEY` do ambiente (ou de um `.env` em `PONTE_ENV`) e ainda não foi executado pelo INEMA. Prompt para o seu agente integrar a API: [docs/prompt-integracao.md](docs/prompt-integracao.md).

## Estrutura

- `ponte/` — conversão, normalização, comparação e CLI (só biblioteca padrão).
- `exemplos/` — requisições autorais; `exemplos/simulado/` — respostas simuladas da demo.
- `docs/` — comparação com fonte e prompt de integração.
- `guia/` — landing + guia em PT/EN/ES.

## Relacionados

- [Área JEV no INEMA Eventos](https://eventos.inema.pro/jev/) · [projeto jev](https://github.com/inematds/jev) · [curso JEV](https://inematds.github.io/jev-curso/)

Projeto educacional independente. Jev é um modelo da TypeSafe; Decisions API é um produto da OpenAI. Licença MIT.

## Vídeo

[Assistir ao vídeo explicativo](https://inematds.github.io/decisions-jev/videos/) (PT, 5min41s, avatar e voz do Nei; também [no YouTube](https://www.youtube.com/watch?v=O2061m5FG_I)). Fonte: vídeo de Mark Kashef no YouTube.
