// Execute com Node 22+: node --test frontend/tests/api.test.mjs
// Testes de contrato do cliente; não substituem os testes contra a API real.
import { afterEach, test } from 'node:test';
import assert from 'node:assert/strict';
import { api, ApiError, hasToken, setToken } from '../js/api.js';

const originalFetch = globalThis.fetch;
afterEach(() => {
  globalThis.fetch = originalFetch;
  setToken('');
  delete globalThis.window;
});
const json = (body, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { 'Content-Type': 'application/json' },
});

test('login envia formulário OAuth2 e não envia token', async () => {
  setToken('anterior');
  globalThis.fetch = async (url, options) => {
    assert.equal(url, '/api/auth/login');
    assert.equal(options.method, 'POST');
    assert.equal(options.headers.Authorization, undefined);
    assert.equal(options.headers['Content-Type'], 'application/x-www-form-urlencoded');
    assert.equal(options.body.get('username'), 'ana@example.com');
    assert.equal(options.body.get('password'), 'Senha123');
    return json({ access_token: 'novo', token_type: 'bearer' });
  };
  assert.equal((await api.login('ana@example.com', 'Senha123')).access_token, 'novo');
});

test('cadastro é público e usa somente os campos enviados', async () => {
  const body = { nome: 'Ana', email: 'ana@example.com', senha: 'Senha123' };
  globalThis.fetch = async (url, options) => {
    assert.equal(url, '/api/usuarios/');
    assert.equal(options.headers.Authorization, undefined);
    assert.deepEqual(JSON.parse(options.body), body);
    return json({ id: 1, nome: 'Ana' }, 201);
  };
  assert.equal((await api.register(body)).id, 1);
});

test('listas percorrem todas as páginas da API', async () => {
  let call = 0;
  setToken('token-teste');
  globalThis.fetch = async (url, options) => {
    assert.equal(options.headers.Authorization, 'Bearer token-teste');
    assert.equal(url, `/api/transacoes/?skip=${call === 0 ? 0 : 100}&limit=100`);
    const items = call++ === 0 ? Array.from({ length: 100 }, (_, index) => ({ id: index + 1 })) : [{ id: 101 }];
    return json({ items, total: 101, skip: 0, limit: 100 });
  };
  assert.equal((await api.transactions()).length, 101);
  assert.equal(call, 2);
});

test('atualização preserva categoria nula intencional', async () => {
  globalThis.fetch = async (url, options) => {
    assert.equal(url, '/api/transacoes/7');
    assert.equal(options.method, 'PUT');
    assert.deepEqual(JSON.parse(options.body), { categoria_id: null });
    return json({ id: 7, categoria_id: null });
  };
  await api.update('transacoes', 7, { categoria_id: null });
});

test('aporte usa objeto valor e rota documentada', async () => {
  globalThis.fetch = async (url, options) => {
    assert.equal(url, '/api/metas/2/adicionar-valor');
    assert.equal(options.method, 'POST');
    assert.deepEqual(JSON.parse(options.body), { valor: 25.5 });
    return json({ id: 2, valor_inicial: 25.5 });
  };
  await api.contribute(2, 25.5);
});

test('resposta 204 não exige corpo JSON', async () => {
  globalThis.fetch = async () => new Response(null, { status: 204 });
  assert.equal(await api.remove('metas', 2), null);
});

test('erros de negócio são exibidos sem perder a mensagem', async () => {
  globalThis.fetch = async () => json({ detail: 'Categoria com este nome já existe' }, 400);
  await assert.rejects(api.create('categorias', {}), error =>
    error instanceof ApiError && error.status === 400 && /já existe/.test(error.message));
});

test('validação 422 identifica os campos em português', async () => {
  globalThis.fetch = async () => json({ detail: [{ loc: ['body', 'valor_final'], msg: 'invalid' }] }, 422);
  await assert.rejects(api.create('metas', {}), /Valor da meta/);
});

test('401 protegido limpa sessão e avisa a interface', async () => {
  let events = 0;
  globalThis.window = { dispatchEvent(event) { assert.equal(event.type, 'session-expired'); events++; } };
  setToken('expirado');
  globalThis.fetch = async () => json({ detail: 'Acesso negado' }, 401);
  await assert.rejects(api.me(), ApiError);
  assert.equal(hasToken(), false);
  assert.equal(events, 1);
});

test('401 do login não encerra outra sessão', async () => {
  setToken('anterior');
  globalThis.fetch = async () => json({ detail: 'Credenciais inválidas' }, 401);
  await assert.rejects(api.login('ana@example.com', 'errada'), /incorretos/);
  assert.equal(hasToken(), true);
});

test('500 não expõe resposta interna do servidor', async () => {
  globalThis.fetch = async () => new Response('Traceback interno', { status: 500 });
  await assert.rejects(api.me(), error => error.status === 500 && !error.message.includes('Traceback'));
});

test('falha de rede em envio alerta sobre resultado incerto', async () => {
  globalThis.fetch = async () => { throw new TypeError('Failed to fetch'); };
  await assert.rejects(api.create('transacoes', {}), /confira seus dados antes de reenviar/);
});

test('resposta de sucesso inválida é tratada como erro', async () => {
  globalThis.fetch = async () => new Response('<html>proxy incorreto</html>', { status: 200 });
  await assert.rejects(api.me(), /formato inesperado/);
});
