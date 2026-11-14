import { API_BASE_URL } from './config.js';

const SESSION_KEY = 'controle-financeiro.token';
let token = '';
try { token = sessionStorage.getItem(SESSION_KEY) || ''; } catch { /* Navegador sem armazenamento: sessão em memória. */ }

export class ApiError extends Error {
  constructor(message, status = 0) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export function setToken(value) {
  token = value || '';
  try {
    if (token) sessionStorage.setItem(SESSION_KEY, token);
    else sessionStorage.removeItem(SESSION_KEY);
  } catch { /* O acesso continua disponível nesta página. */ }
}
export const hasToken = () => Boolean(token);

const fields = {
  nome: 'Nome', email: 'E-mail', senha: 'Senha', descricao: 'Descrição',
  valor: 'Valor', valor_inicial: 'Valor inicial', valor_final: 'Valor da meta',
  valor_limite: 'Limite', data: 'Data', data_inicio: 'Data inicial',
  data_fim: 'Data final', categoria_id: 'Categoria', tipo: 'Tipo',
};
function errorMessage(body, status) {
  if (status >= 500) return 'O servidor não conseguiu concluir a operação. Tente novamente mais tarde.';
  if (typeof body?.detail === 'string') {
    if (body.detail === 'Credenciais inválidas') return 'E-mail ou senha incorretos. Confira seus dados.';
    return body.detail;
  }
  if (Array.isArray(body?.detail)) {
    const names = [...new Set(body.detail.map(item => fields[item.loc?.at(-1)] || 'Dados do formulário'))];
    return `Confira os campos: ${names.join(', ')}. Os dados não foram aceitos pela API.`;
  }
  return `Não foi possível concluir a operação (HTTP ${status}). Tente novamente.`;
}

async function request(path, { method = 'GET', body, authenticated = true, form = false } = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  const headers = { Accept: 'application/json' };
  const sentToken = token;
  if (authenticated && token) headers.Authorization = `Bearer ${token}`;
  if (body !== undefined) headers['Content-Type'] = form ? 'application/x-www-form-urlencoded' : 'application/json';
  try {
    const response = await fetch(`${API_BASE_URL.replace(/\/$/, '')}${path}`, {
      method, headers, signal: controller.signal, credentials: 'omit',
      cache: 'no-store',
      body: body === undefined ? undefined : form ? new URLSearchParams(body) : JSON.stringify(body),
    });
    const text = response.status === 204 ? '' : await response.text();
    let data = null;
    if (text) {
      try { data = JSON.parse(text); }
      catch {
        if (response.ok) throw new ApiError('A API respondeu em um formato inesperado. Confira a configuração do servidor.', response.status);
      }
    }
    if (!response.ok) {
      if (response.status === 401 && authenticated && sentToken === token) {
        setToken('');
        window.dispatchEvent(new Event('session-expired'));
      }
      throw new ApiError(errorMessage(data, response.status), response.status);
    }
    return data;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    const uncertain = method !== 'GET' ? ' A operação pode ter sido recebida: confira seus dados antes de reenviar.' : '';
    if (error.name === 'AbortError') throw new ApiError(`A API demorou para responder. Confira a conexão.${uncertain}`);
    throw new ApiError(`Não foi possível conectar à API. Verifique se ela está em execução e se o endereço e o CORS estão configurados.${uncertain}`);
  } finally {
    clearTimeout(timeout);
  }
}

async function listAll(path) {
  const items = [];
  let total = Infinity;
  while (items.length < total) {
    const page = await request(`${path}?skip=${items.length}&limit=100`);
    if (!page || !Array.isArray(page.items) || !Number.isInteger(page.total)) {
      throw new ApiError('A lista recebida da API está em um formato inesperado.');
    }
    total = page.total;
    if (!page.items.length) break;
    items.push(...page.items);
  }
  return items;
}

export const api = {
  login: (email, password) => request('/auth/login', {
    method: 'POST', authenticated: false, form: true, body: { username: email, password },
  }),
  register: body => request('/usuarios/', { method: 'POST', authenticated: false, body }),
  me: () => request('/auth/me'),
  transactions: () => listAll('/transacoes/'),
  categories: () => listAll('/categorias/'),
  goals: () => listAll('/metas/'),
  create: (resource, body) => request(`/${resource}/`, { method: 'POST', body }),
  update: (resource, id, body) => request(`/${resource}/${id}`, { method: 'PUT', body }),
  remove: (resource, id) => request(`/${resource}/${id}`, { method: 'DELETE' }),
  contribute: (id, valor) => request(`/metas/${id}/adicionar-valor`, { method: 'POST', body: { valor } }),
};
