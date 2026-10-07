import json
import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from ponte import conversao as c  # noqa: E402


def ler(nome):
    return json.loads((RAIZ / 'exemplos' / nome).read_text(encoding='utf-8'))


class Conversao(unittest.TestCase):
    def test_jev_para_openai_tipos(self):
        out = c.jev_para_openai(ler('plantao-pet.jev.json'))
        self.assertEqual(out['model'], 'gpt-6-luna')
        tipos = {q['name']: q['type'] for q in out['questions']}
        self.assertEqual(tipos, {'atender_hoje': 'predicate', 'assunto': 'choice', 'gravidade': 'score'})
        score = next(q for q in out['questions'] if q['type'] == 'score')
        self.assertEqual([n['label'] for n in score['levels']], ['baixa', 'moderada', 'alta'])
        choice = next(q for q in out['questions'] if q['type'] == 'choice')
        self.assertEqual(choice['choices'][0], {'value': 'emergencia', 'description': 'Sintoma agudo, dor, trauma ou risco imediato.'})

    def test_estado_objeto_vira_texto(self):
        out = c.jev_para_openai(ler('incidente-checkout.jev.json'))
        self.assertIn('gateway de pagamento', out['input'])

    def test_imagem_vira_mensagem(self):
        out = c.jev_para_openai(ler('plantao-pet.jev.json'), ['data:image/png;base64,AAA'])
        partes = out['input'][0]['content']
        self.assertEqual([p['type'] for p in partes], ['input_text', 'input_image'])

    def test_openai_para_jev_descarta_imagem(self):
        req, descartadas = c.openai_para_jev(ler('devolucao-foto.openai.json'))
        self.assertEqual(descartadas, 1)
        self.assertEqual(req['questions']['dano_visivel']['type'], 'noul')
        self.assertIn('nao_avaliavel', req['questions']['situacao']['criteria'])

    def test_ida_e_volta(self):
        original = ler('plantao-pet.jev.json')
        volta, _ = c.openai_para_jev(c.jev_para_openai(original))
        self.assertEqual(set(volta['questions']), set(original['questions']))
        self.assertEqual(volta['questions']['assunto']['criteria'], original['questions']['assunto']['criteria'])

    def test_erros(self):
        with self.assertRaises(c.PonteErro):
            c.jev_para_openai({'state': 'x', 'questions': {}})
        with self.assertRaises(c.PonteErro):
            c.jev_para_openai({'state': 'x', 'questions': {'a': {'type': 'choice', 'instructions': 'i', 'criteria': {'so': 'uma'}}}})


class Respostas(unittest.TestCase):
    def setUp(self):
        self.d = json.loads((RAIZ / 'exemplos/simulado/1-plantao-pet.json').read_text())

    def test_normaliza_os_dois_formatos(self):
        a = c.normalizar('openai', self.d['openai'])
        b = c.normalizar('jev', self.d['jev'])
        self.assertEqual(a['assunto']['probabilidade'], 0.88)
        self.assertEqual(b['assunto']['probabilidade'], 0.8)
        self.assertEqual(b['atender_hoje']['tipo'], 'predicate')
        self.assertTrue(all(l['concordam'] for l in c.comparar(a, b)))

    def test_recusa(self):
        d = json.loads((RAIZ / 'exemplos/simulado/3-recusa.json').read_text())
        a = c.normalizar('openai', d['openai'])
        self.assertTrue(a['perfil']['recusa'])
        self.assertTrue(c.revisar(a['perfil']))
        self.assertFalse(c.comparar(a, c.normalizar('jev', d['jev']))[0]['concordam'])

    def test_revisao_predicate_incerto(self):
        item = {'tipo': 'predicate', 'valor': 0.52, 'probabilidade': 0.52, 'confianca': None, 'recusa': False}
        self.assertTrue(c.revisar(item))
        item['probabilidade'] = 0.05
        self.assertFalse(c.revisar(item))

    def test_custo(self):
        self.assertAlmostEqual(c.custo_estimado('openai', 1_000_000), 0.10)
        self.assertAlmostEqual(c.custo_estimado('jev', 1_000_000), 0.042)


class Cli(unittest.TestCase):
    def rodar(self, *args, env=None):
        import os
        e = {**os.environ, 'PERMITIR_API': ''}
        return subprocess.run([sys.executable, '-m', 'ponte', *args], cwd=RAIZ, capture_output=True, text=True, env=e)

    def test_demo(self):
        r = self.rodar('demo')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('RECUSOU', r.stdout)
        self.assertIn('SIMULADO', r.stdout)

    def test_ao_vivo_bloqueado_sem_permissao(self):
        r = self.rodar('ao-vivo', 'exemplos/plantao-pet.jev.json')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('PERMITIR_API', r.stderr)


if __name__ == '__main__':
    unittest.main()
