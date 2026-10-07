# Prompt para o seu agente integrar a Decisions API

Use no Claude Code, no Codex ou em outro agente de código. Não depende do Codex: é uma API da OpenAI como qualquer outra e exige uma chave da plataforma OpenAI (cobrada à parte da assinatura).

```text
Integre a Decisions API da OpenAI neste sistema. Ela é nova e você
provavelmente não a conhece: ANTES de escrever código, leia a documentação
oficial em Markdown:
https://developers.openai.com/api/docs/guides/decisions.md
Siga exatamente o formato descrito (POST /v1/decisions, modelo gpt-6-luna,
perguntas predicate/choice/score) e use a versão mais recente do SDK oficial.

Funcionalidade:
- Ao clicar em "Analisar", envie a mensagem do cliente numa ÚNICA chamada
  com as perguntas juntas: <sim/não>, <escolha de assunto> e <nota de gravidade>.
- Escreva instruções, alternativas e níveis em português, dizendo o que cada
  opção significa. Mantenha uma alternativa "outro" para o que não encaixar.
- A chamada acontece no servidor; a chave fica no .env (OPENAI_API_KEY).
- No painel, mostre: resposta, confiança, tempo da chamada, tokens de entrada
  e custo (preço por 1M de tokens lido do .env, porque pode mudar).
- Confiança abaixo de 0,6: destaque em amarelo como "revisar".
- Se a API recusar uma pergunta (type "refusal"), mostre na tela; não quebre.
- Salve o resultado e exiba um selo de gravidade em cada mensagem.

Se houver foto: reduza a imagem antes de enviar, mande como data URL base64
na mesma chamada e acrescente uma pergunta predicate específica da foto.
```

Depois que o agente disser "testei", **teste você mesmo**: confira se a chave estava no `.env` no momento do teste e rode alguns casos reais pela tela.
