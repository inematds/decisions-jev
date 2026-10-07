# OpenAI Decisions API × Jev — comparação com fonte

Levantamento de 07/10/2026. Cada linha diz de onde veio a informação. Nada aqui foi medido pelo INEMA: este repositório não chamou nenhuma das duas APIs.

## 1. O que a documentação oficial da OpenAI diz

Fonte: [guia Decisions da OpenAI](https://developers.openai.com/api/docs/guides/decisions) (versão em Markdown: acrescente `.md` à URL).

- Endpoint próprio: `POST /v1/decisions`. Não é o Responses API nem chat.
- Situação: **beta pública**, com GA prevista "nas próximas semanas". (A data de lançamento, 06/10/2026, vem da cobertura do lançamento, não do guia.)
- Modelo: `gpt-6-luna` é o único disponível.
- Entrada: texto, imagem ou os dois. Imagem **só como data URL base64** (URL http/https e `file_id` não são aceitos).
- Três tipos de pergunta, que podem ir juntas na mesma requisição:
  - `predicate` — probabilidade de 0 a 1 de uma condição ser verdadeira.
  - `choice` — escolhe um `value` da lista `choices`, com distribuição de probabilidades e campo `confidence`.
  - `score` — `levels` ordenados (índice começa em 0); devolve média ponderada, que pode cair entre níveis (ex.: 1,1), com `confidence`.
- Resposta: lista `answers`; cada item repete o `name` da pergunta. Uma pergunta pode voltar como `type: "refusal"` — recusa explícita, não um "falso" disfarçado.
- Preço: **US$ 0,10 por 1M de tokens de entrada**; sem cobrança de saída nem de cache. Há adicionais de processamento regional e de contexto longo.
- ZDR e HIPAA para clientes elegíveis; residência de dados nos EUA e na Europa.
- Playground no painel da OpenAI.

## 2. O que dá para conferir no projeto Jev do INEMA

Fonte: [inematds/jev](https://github.com/inematds/jev) (`jev_lab/core.py`, `reports/openrouter-smoke.json`).

- Modelo `~typesafe/jev-latest` pelo OpenRouter (`/api/alpha/decisions`) ou pela API TypeSafe.
- Requisição com `state` (texto, objeto ou lista) e `questions` como **objeto** de perguntas nomeadas.
- Tipos: `choice`, `noul` (sim/não) e `score`; alternativas e níveis em `criteria`.
- Só texto: não aceita imagem.
- Preço usado no laboratório: US$ 0,042 por 1M de tokens de entrada. Diferente da OpenAI, a resposta do Jev traz `output_tokens` e o `cost` cobrado.
- O formato de resposta usado no `jev_lab` não tem tipo de recusa. Que o Jev "sempre responde dentro das opções" é observação do autor do vídeo 1; por isso vale incluir uma opção `insuficiente`.

## 3. Mapa de equivalência (o que a ponte faz)

| Jev | Decisions API | Observação |
|---|---|---|
| `state` | `input` | Objeto/lista do Jev vira texto JSON. |
| `questions` (objeto) | `questions` (lista com `name`) | O nome da chave vira `name`. |
| `noul` | `predicate` | Descrições `true`/`false` do Jev entram nas instruções. |
| `choice` + `criteria` {valor: descrição} | `choice` + `choices` [{value, description}] | — |
| `score` + `criteria` [níveis] | `score` + `levels` [{label, description}] | Índices a partir de 0 nos dois. |
| `probabilities` {valor: p} | `probabilities` [{value, probability}] | A ponte normaliza para o mesmo formato. |
| — | `refusal` | Sem equivalente no Jev. Tratar como revisão humana. |
| — | `input_image` | O Jev não lê imagem; a ponte descarta e avisa. |

## 4. Números que apareceram nos vídeos (medições dos autores, não nossas)

Fontes: [vídeo 1, "OpenAI's Decisions API just dropped. Here's how it compares to Jev"](https://www.youtube.com/watch?v=uTU5Ihgl_7Q), assistido em transcrição bengali, e um segundo vídeo em espanhol, com integração num sistema de triagem de clínica veterinária. O segundo chegou só como transcrição, sem link; não identificamos o canal.

| Item | Relato | Fonte |
|---|---|---|
| Preço | Jev ≈ 58% mais barato por token de entrada (0,042 × 0,10) | vídeo 1, coerente com as tabelas acima |
| Latência média | OpenAI 146 ms × Jev 155 ms em perguntas de checagem de relatório | vídeo 1 |
| Latência mediana | levemente melhor no Jev | vídeo 1 |
| Incidentes (mais complexo) | 181 × 143 ms, diferença a favor da OpenAI; custo do Jev ≈ metade | vídeo 1 |
| Precisão | empate nos testes do autor (perguntas fáceis, 100% de acordo) | vídeo 1 |
| Latência observada | ~300 ms numa chamada, o dobro dos ~150 ms anunciados; outras perto do anunciado | vídeo 2 |
| Imagem | foto com e sem dano e caixa fechada classificadas corretamente; foto custa um pouco mais de tokens | vídeos 1 e 2 |
| Saúde | em triagem veterinária o modelo foi "cauteloso", marcando urgência com folga | vídeo 2 |

São testes pequenos, feitos pelos autores, com perguntas fáceis. Servem de indício, não de benchmark.

## 5. Quando usar cada um (resumo prático)

- **Tem imagem** (foto de produto, de ferimento, print) → Decisions API. O Jev ainda não lê imagem.
- **Muito volume, só texto** → o Jev custa menos por token de entrada; em milhões de registros a diferença pesa.
- **Precisa de recusa explícita** em temas sensíveis → Decisions API devolve `refusal`. No Jev, crie a opção `insuficiente`.
- **Latência** → nas medições dos vídeos, a diferença fica na casa de dezenas de ms; para uma pessoa esperando, é imperceptível.
- **Os dois** → formule as perguntas uma vez (formato Jev ou OpenAI), converta com a ponte e compare no seu próprio conjunto antes de escolher.

Em ambos: confiança baixa (ex.: < 0,6) ou recusa → revisão humana. A decisão do modelo não executa nada sozinha; o seu sistema continua responsável pela ação.
