"""CLI da ponte.

  python3 -m ponte converter jev-openai exemplos/plantao-pet.jev.json
  python3 -m ponte converter openai-jev exemplos/devolucao-foto.openai.json
  python3 -m ponte demo                      # offline, respostas simuladas
  python3 -m ponte ao-vivo exemplos/plantao-pet.jev.json [--imagem foto.jpg]

O modo ao-vivo chama as duas APIs pagas e só roda com PERMITIR_API=1.
As chaves são lidas em tempo de execução (OPENAI_API_KEY, OPENROUTER_API_KEY)
do ambiente ou de um .env indicado em PONTE_ENV; nunca são impressas.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen

from . import conversao as c

RAIZ = Path(__file__).resolve().parents[1]
ENDPOINT = {'openai': 'https://api.openai.com/v1/decisions',
            'jev': 'https://openrouter.ai/api/alpha/decisions'}
CHAVE = {'openai': 'OPENAI_API_KEY', 'jev': 'OPENROUTER_API_KEY'}


def _ler(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def _imprimir(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def cmd_converter(a):
    req = _ler(a.arquivo)
    if a.sentido == 'jev-openai':
        imgs = [c.imagem_data_url(i) for i in a.imagem or []]
        out = c.jev_para_openai(req, imgs)
        if imgs:  # não despejar base64 na tela
            for parte in out['input'][0]['content']:
                if parte['type'] == 'input_image':
                    parte['image_url'] = parte['image_url'][:40] + '…'
        _imprimir(out)
    else:
        out, descartadas = c.openai_para_jev(req)
        _imprimir(out)
        if descartadas:
            print(f'# aviso: {descartadas} imagem(ns) descartada(s) — o Jev só lê texto', file=sys.stderr)


def tabela(nome_caso, na, nb, ms=None, custos=None):
    print(f'\n== {nome_caso}')
    print(f'{"pergunta":<22}{"Decisions (OpenAI)":<30}{"Jev":<30}igual?')
    for linha in c.comparar(na, nb):
        p = linha['pergunta']
        def fmt(item):
            if not item:
                return '—'
            if item['recusa']:
                return 'RECUSOU'
            v = item['valor']
            v = f'{v:.2f}' if isinstance(v, float) else str(v)
            conf = item['confianca'] if item['confianca'] is not None else item['probabilidade']
            alerta = ' ⚠revisar' if c.revisar(item) else ''
            return f'{v} ({conf:.0%}){alerta}' if conf is not None else v + alerta
        print(f'{p:<22}{fmt(na.get(p)):<30}{fmt(nb.get(p)):<30}{"sim" if linha["concordam"] else "NÃO"}')
    if ms:
        print(f'latência ms: OpenAI {ms[0]:.0f} · Jev {ms[1]:.0f}')
    if custos:
        print(f'custo US$:   OpenAI {custos[0]:.8f} · Jev {custos[1]:.8f}')


def cmd_demo(a):
    pasta = RAIZ / 'exemplos' / 'simulado'
    for arq in sorted(pasta.glob('*.json')):
        d = _ler(arq)
        na = c.normalizar('openai', d['openai'])
        nb = c.normalizar('jev', d['jev'])
        tabela(d['caso'] + '  [SIMULADO]', na, nb)
    print('\nRespostas simuladas e autorais: servem para estudar o formato, não medem os modelos.')


def _carregar_chave(nome):
    if os.environ.get(nome):
        return os.environ[nome]
    env = os.environ.get('PONTE_ENV')
    if env and Path(env).exists():
        for linha in Path(env).read_text().splitlines():
            if linha.startswith(nome + '='):
                return linha.split('=', 1)[1].strip().strip('"\'')
    raise SystemExit(f'Falta {nome} (ambiente ou PONTE_ENV).')


def _post(provedor, corpo):
    chave = _carregar_chave(CHAVE[provedor])
    req = Request(ENDPOINT[provedor], data=json.dumps(corpo).encode(), method='POST',
                  headers={'Authorization': f'Bearer {chave}', 'Content-Type': 'application/json'})
    t = time.perf_counter()
    with urlopen(req, timeout=60) as r:
        dados = json.loads(r.read())
    return dados, (time.perf_counter() - t) * 1000


def cmd_ao_vivo(a):
    if os.environ.get('PERMITIR_API') != '1':
        raise SystemExit('Modo ao-vivo chama APIs pagas. Defina PERMITIR_API=1 para confirmar.')
    req_jev = _ler(a.arquivo)
    imgs = [c.imagem_data_url(i) for i in a.imagem or []]
    req_oa = c.jev_para_openai(req_jev, imgs)
    r_oa, ms_oa = _post('openai', req_oa)
    r_jev, ms_jev = _post('jev', req_jev)
    tok = (r_oa.get('usage') or {}).get('input_tokens', 0)
    custo_oa = c.custo_estimado('openai', tok)
    custo_jev = (r_jev.get('usage') or {}).get('cost') or 0
    tabela(Path(a.arquivo).name, c.normalizar('openai', r_oa), c.normalizar('jev', r_jev),
           (ms_oa, ms_jev), (custo_oa, custo_jev))
    if imgs:
        print('Obs.: a imagem foi só para a OpenAI; o Jev recebeu apenas o texto.')


def main(argv=None):
    p = argparse.ArgumentParser(prog='ponte', description='Ponte Jev ↔ OpenAI Decisions API')
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('converter')
    s.add_argument('sentido', choices=['jev-openai', 'openai-jev'])
    s.add_argument('arquivo')
    s.add_argument('--imagem', action='append')
    s.set_defaults(f=cmd_converter)
    s = sub.add_parser('demo')
    s.set_defaults(f=cmd_demo)
    s = sub.add_parser('ao-vivo')
    s.add_argument('arquivo')
    s.add_argument('--imagem', action='append')
    s.set_defaults(f=cmd_ao_vivo)
    a = p.parse_args(argv)
    a.f(a)


if __name__ == '__main__':
    main()
