"""Ponte entre o formato Jev (TypeSafe/OpenRouter) e a Decisions API da OpenAI.

Só biblioteca padrão. Converte requisições nos dois sentidos e normaliza as
respostas para um formato único, para comparar os dois provedores lado a lado.
Nenhuma função deste módulo acessa a rede.
"""
import base64
import mimetypes
from pathlib import Path

OPENAI_MODEL = 'gpt-6-luna'
JEV_MODEL = '~typesafe/jev-latest'

# Preço por 1M de tokens de entrada, em dólares (fontes no docs/comparacao.md).
# A OpenAI não cobra saída na Decisions API; o Jev informa o custo na resposta.
PRECO_ENTRADA = {'openai': 0.10, 'jev': 0.042}

TIPOS_JEV_OPENAI = {'choice': 'choice', 'noul': 'predicate', 'score': 'score'}
TIPOS_OPENAI_JEV = {v: k for k, v in TIPOS_JEV_OPENAI.items()}


class PonteErro(ValueError):
    pass


def imagem_data_url(caminho):
    """Lê uma imagem local e devolve data URL base64 (a Decisions API não aceita URL http)."""
    p = Path(caminho)
    tipo = mimetypes.guess_type(p.name)[0]
    if not tipo or not tipo.startswith('image/'):
        raise PonteErro(f'Arquivo não parece imagem: {p.name}')
    return f'data:{tipo};base64,' + base64.b64encode(p.read_bytes()).decode()


def _texto_estado(state):
    if isinstance(state, str):
        return state
    import json
    return json.dumps(state, ensure_ascii=False)


def jev_para_openai(req, imagens=()):
    """Requisição Jev -> corpo de POST /v1/decisions.

    `imagens` são data URLs já prontas (use imagem_data_url). O Jev não aceita
    imagem; quando houver, o input vira mensagem com partes de texto e imagem.
    """
    questions = req.get('questions')
    if not isinstance(questions, dict) or not questions:
        raise PonteErro('Requisição Jev sem perguntas.')
    texto = _texto_estado(req.get('state'))
    if imagens:
        partes = [{'type': 'input_text', 'text': texto}]
        partes += [{'type': 'input_image', 'image_url': u} for u in imagens]
        entrada = [{'role': 'user', 'content': partes}]
    else:
        entrada = texto
    saida = []
    for nome, q in questions.items():
        tipo = TIPOS_JEV_OPENAI.get(q.get('type'))
        if not tipo:
            raise PonteErro(f'Tipo desconhecido em {nome}: {q.get("type")}')
        item = {'type': tipo, 'name': nome, 'instructions': q['instructions']}
        crit = q.get('criteria')
        if tipo == 'choice':
            if not isinstance(crit, dict) or len(crit) < 2:
                raise PonteErro(f'Choice {nome} precisa de 2+ alternativas.')
            item['choices'] = [{'value': k, 'description': v} for k, v in crit.items()]
        elif tipo == 'score':
            if not isinstance(crit, list) or len(crit) < 2:
                raise PonteErro(f'Score {nome} precisa de 2+ níveis.')
            item['levels'] = [_nivel_openai(n) for n in crit]
        elif tipo == 'predicate' and isinstance(crit, dict):
            # Predicate não tem descrição de sim/não: o critério entra nas instruções.
            extra = '; '.join(f'{k}: {v}' for k, v in crit.items())
            item['instructions'] += f' ({extra})'
        saida.append(item)
    return {'model': OPENAI_MODEL, 'input': entrada, 'questions': saida}


def _nivel_openai(nivel):
    if isinstance(nivel, dict):
        rotulo = nivel.get('label') or nivel.get('name') or nivel.get('value')
        return {'label': str(rotulo), 'description': nivel.get('description', '')}
    return {'label': str(nivel), 'description': str(nivel)}


def openai_para_jev(req):
    """Corpo da Decisions API -> requisição Jev. Imagens são descartadas e listadas."""
    entrada = req.get('input')
    descartadas = 0
    if isinstance(entrada, list):
        textos = []
        for msg in entrada:
            for parte in msg.get('content', []):
                if parte.get('type') == 'input_text':
                    textos.append(parte['text'])
                elif parte.get('type') == 'input_image':
                    descartadas += 1
        entrada = '\n'.join(textos)
    if not isinstance(entrada, str) or not entrada.strip():
        raise PonteErro('Sem texto para o Jev (ele não lê imagens).')
    questions = {}
    for q in req.get('questions', []):
        tipo = TIPOS_OPENAI_JEV.get(q.get('type'))
        if not tipo:
            raise PonteErro(f'Tipo desconhecido: {q.get("type")}')
        item = {'type': tipo, 'instructions': q['instructions']}
        if tipo == 'choice':
            item['criteria'] = {c['value']: c.get('description', '') for c in q['choices']}
        elif tipo == 'score':
            item['criteria'] = [{'label': n['label'], 'description': n.get('description', '')}
                                for n in q['levels']]
        questions[q['name']] = item
    return {'model': JEV_MODEL, 'state': entrada, 'questions': questions}, descartadas


def normalizar(provedor, resposta):
    """Resposta de qualquer lado -> {nome: {tipo, valor, probabilidade, confianca, recusa}}.

    valor: escolha (choice), probabilidade de sim (predicate/noul) ou score (0..n-1).
    """
    out = {}
    answers = resposta.get('answers')
    if provedor == 'openai':
        itens = [(a.get('name'), a) for a in answers or []]
    elif provedor == 'jev':
        itens = list((answers or {}).items())
    else:
        raise PonteErro(f'Provedor desconhecido: {provedor}')
    for nome, a in itens:
        tipo = a.get('type')
        if tipo == 'refusal':
            out[nome] = {'tipo': 'recusa', 'valor': None, 'probabilidade': None,
                         'confianca': None, 'recusa': True}
            continue
        tipo = {'noul': 'predicate'}.get(tipo, tipo)
        probs = a.get('probabilities')
        if isinstance(probs, list):  # OpenAI: [{value, probability}]
            probs = {p.get('value', p.get('label', i)): p['probability'] for i, p in enumerate(probs)}
        if tipo == 'choice':
            valor = a.get('choice')
            prob = (probs or {}).get(valor)
        elif tipo == 'predicate':
            valor = a.get('probability')
            prob = valor
        elif tipo == 'score':
            valor = a.get('score')
            prob = None
        else:
            raise PonteErro(f'Tipo de resposta desconhecido: {tipo}')
        out[nome] = {'tipo': tipo, 'valor': valor, 'probabilidade': prob,
                     'confianca': a.get('confidence'), 'recusa': False}
    return out


def custo_estimado(provedor, tokens_entrada, tokens_saida=0):
    """Custo pela tabela de entrada. Para o Jev, prefira o custo que a resposta informa."""
    return round(tokens_entrada * PRECO_ENTRADA[provedor] / 1_000_000, 10)


def revisar(item, limite=0.6):
    """Política didática: recusa ou confiança abaixo do limite vai para revisão humana."""
    if item['recusa']:
        return True
    medida = item['confianca'] if item['confianca'] is not None else item['probabilidade']
    if item['tipo'] == 'predicate' and medida is not None:
        medida = max(medida, 1 - medida)  # perto de 0,5 = incerto
    return medida is not None and medida < limite


def comparar(a, b):
    """Compara duas respostas normalizadas e diz onde concordam."""
    linhas = []
    for nome in sorted(set(a) | set(b)):
        x, y = a.get(nome), b.get(nome)
        if not x or not y:
            linhas.append({'pergunta': nome, 'concordam': False, 'motivo': 'faltou resposta'})
            continue
        if x['recusa'] or y['recusa']:
            ok = x['recusa'] == y['recusa']
        elif x['tipo'] == 'predicate':
            ok = (x['valor'] >= 0.5) == (y['valor'] >= 0.5)
        elif x['tipo'] == 'score':
            ok = round(x['valor']) == round(y['valor'])
        else:
            ok = x['valor'] == y['valor']
        linhas.append({'pergunta': nome, 'concordam': ok, 'a': x['valor'], 'b': y['valor']})
    return linhas
