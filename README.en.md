# ⚖️ Decisions × Jev

[![Decisions × Jev](guia/assets/banner-en.jpg)](https://inematds.github.io/decisions-jev/guia/en/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## What it is

OpenAI launched the Decisions API: you send a text or a photo with closed questions and get back only the answer — yes/no, one option from your list or a score — with its probability, no running text. It is the same idea as Jev, the decision model INEMA already studies. This project explains the differences with the source of each piece of information and ships a Python bridge that converts questions from one format to the other and compares the answers. To study, just read and run the offline demo; to call the real APIs, you need your own keys.

## 📖 User guide

Full guide (landing + step by step): **https://inematds.github.io/decisions-jev/guia/en/**

## In 30 seconds

| | OpenAI Decisions API | Jev | Microsoft-Decision-1 |
|---|---|---|---|
| Yes/no | `predicate` | `noul` | yes/no |
| One option from a list | `choice` + `choices` | `choice` + `criteria` | multiple choice |
| Score | `score` + `levels` | `score` + `criteria` | rating and rubric |
| Image | yes (base64) | no | no (text only, up to 32,768 tokens) |
| Refusal | `refusal` | does not exist | not stated |
| Input price | US$ 0.10 / 1M tokens | US$ 0.042 / 1M tokens | US$ 0.042 / 1M tokens (output free) |

Sources, the videos' numbers and when to use each one: [docs/comparacao.md](docs/comparacao.md) (in Portuguese).

## Usage

```bash
python3 -m ponte demo                                              # offline, simulated answers
python3 -m ponte converter jev-openai exemplos/plantao-pet.jev.json [--imagem foto.jpg]
python3 -m ponte converter openai-jev exemplos/devolucao-foto.openai.json
PERMITIR_API=1 python3 -m ponte ao-vivo exemplos/plantao-pet.jev.json  # paid call, on both
python3 -m unittest discover -s testes                             # 12 tests
```

The `ao-vivo` mode reads `OPENAI_API_KEY` and `OPENROUTER_API_KEY` from the environment (or from a `.env` in `PONTE_ENV`) and has not been run by INEMA yet. Prompt for your agent to integrate the API: [docs/prompt-integracao.md](docs/prompt-integracao.md) (in Portuguese).

## Structure

- `ponte/` — conversion, normalization, comparison and CLI (standard library only).
- `exemplos/` — original requests; `exemplos/simulado/` — the demo's simulated answers.
- `docs/` — comparison with sources and integration prompt.
- `guia/` — landing + guide in PT/EN/ES.

## Related

- [JEV area at INEMA Eventos](https://eventos.inema.pro/jev/) · [jev project](https://github.com/inematds/jev) · [JEV course](https://inematds.github.io/jev-curso/)

Independent educational project. Jev is a TypeSafe model; Decisions API is an OpenAI product. MIT license.
