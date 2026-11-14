import { api, hasToken, setToken } from './api.js';
import { buildForm, validateRecord } from './forms.js';
import { renderSummary, renderTransactions, renderGoals, renderCategories, renderCategoryFilter } from './render.js';

const $ = selector => document.querySelector(selector);
const resources = { transaction: 'transacoes', category: 'categorias', goal: 'metas' };
const collections = { transaction: 'transactions', category: 'categories', goal: 'goals' };
const pages = {
  'visao-geral': ['Visão geral', 'Um olhar simples para suas finanças.', 'Nova transação', 'transaction'],
  transacoes: ['Transações', 'Tudo o que entra e sai, em um só lugar.', 'Nova transação', 'transaction'],
  metas: ['Metas', 'Planeje seus próximos passos e acompanhe o progresso.', 'Nova meta', 'goal'],
  categorias: ['Categorias', 'Organize seus movimentos e acompanhe os limites.', 'Nova categoria', 'category'],
};
let state = { user: null, transactions: [], categories: [], goals: [], loaded: false };
let authMode = 'login';
let authBusy = false;
let mutationBusy = false;
let editor = null;
let pendingDraft = null;
let loadVersion = 0;
let notificationTimeout;

function message(selector, text) {
  const element = $(selector);
  element.textContent = text;
  element.hidden = !text;
}
function notify(text) {
  clearTimeout(notificationTimeout);
  message('#notification', text);
  notificationTimeout = setTimeout(() => { $('#notification').hidden = true; }, 6500);
}
function currentPage() {
  return Object.hasOwn(pages, location.hash.slice(1)) ? location.hash.slice(1) : 'visao-geral';
}
function showAuth(text = '', preserveDraft = false) {
  if (preserveDraft && editor && state.user) {
    pendingDraft = {
      ownerId: state.user.id, editor,
      values: [...$('#record-fields').querySelectorAll('[name]')].map(input => [input.name, input.value]),
    };
  }
  loadVersion++;
  state = { user: null, transactions: [], categories: [], goals: [], loaded: false };
  editor = null;
  $('#record-form').reset();
  $('#record-fields').replaceChildren();
  $('#editor').hidden = true;
  $('#application').hidden = true;
  $('#auth').hidden = false;
  $('#notification').hidden = true;
  if ($('#confirmation').open) $('#confirmation').close('cancel');
  $('.skip-link').href = '#auth-title';
  $('#auth-password').value = '';
  $('#auth-confirm').value = '';
  document.title = 'Entrar · Controle financeiro';
  switchAuth('login', false);
  message('#auth-message', text);
}
function switchAuth(mode, focus = true) {
  if (authBusy) return;
  authMode = mode;
  const register = mode === 'register';
  $('#name-field').hidden = !register;
  $('#confirm-field').hidden = !register;
  for (const selector of ['#auth-name', '#auth-confirm']) {
    $(selector).disabled = !register;
    $(selector).required = register;
  }
  $('#auth-name').minLength = 3;
  $('#auth-password').minLength = register ? 6 : 1;
  $('#auth-password').autocomplete = register ? 'new-password' : 'current-password';
  $('#auth-password').setCustomValidity('');
  $('#auth-confirm').setCustomValidity('');
  $('#password-hint').hidden = !register;
  if (register) $('#auth-password').setAttribute('aria-describedby', 'password-hint');
  else $('#auth-password').removeAttribute('aria-describedby');
  $('#password-hint').textContent = 'Use pelo menos 6 caracteres. Não use apenas espaços.';
  $('#auth-title').textContent = register ? 'Comece pela sua conta.' : 'Bom ter você aqui.';
  $('#auth-description').textContent = register ? 'Preencha seus dados para começar a organizar.' : 'Entre na sua conta para continuar.';
  $('#auth-submit').innerHTML = `${register ? 'Criar minha conta' : 'Entrar na conta'} <span aria-hidden="true">→</span>`;
  $('#login-tab').toggleAttribute('aria-current', !register);
  $('#register-tab').toggleAttribute('aria-current', register);
  $('#login-tab').setAttribute('aria-current', !register ? 'page' : 'false');
  $('#register-tab').setAttribute('aria-current', register ? 'page' : 'false');
  // Só a página ativa recebe o atributo, também usado no CSS.
  if (register) $('#login-tab').removeAttribute('aria-current');
  else $('#register-tab').removeAttribute('aria-current');
  message('#auth-message', '');
  document.title = `${register ? 'Criar conta' : 'Entrar'} · Controle financeiro`;
  if (focus) $(register ? '#auth-name' : '#auth-email').focus();
}
function authPending(pending) {
  authBusy = pending;
  for (const button of $('#auth').querySelectorAll('button')) button.disabled = pending;
  for (const input of $('#auth-form').querySelectorAll('input')) {
    if (!input.closest('[hidden]')) input.readOnly = pending;
  }
  $('#auth-form').setAttribute('aria-busy', String(pending));
  $('#auth-submit').textContent = pending ? 'Aguarde…' : authMode === 'register' ? 'Criar minha conta' : 'Entrar na conta';
}

async function submitAuth(event) {
  event.preventDefault();
  if (authBusy) return;
  const register = authMode === 'register';
  const nome = $('#auth-name').value.trim();
  const email = $('#auth-email').value.trim();
  const senha = $('#auth-password').value;
  if (register && nome.length < 3) {
    $('#auth-name').setCustomValidity('Use pelo menos 3 caracteres, sem contar espaços nas pontas.');
    $('#auth-name').reportValidity();
    return;
  }
  if (register && !senha.trim()) {
    $('#auth-password').setCustomValidity('A senha não pode conter apenas espaços.');
    $('#auth-password').reportValidity();
    return;
  }
  if (register && senha !== $('#auth-confirm').value) {
    $('#auth-confirm').setCustomValidity('As senhas precisam ser iguais.');
    $('#auth-confirm').reportValidity();
    return;
  }
  authPending(true);
  message('#auth-message', '');
  let created = false;
  try {
    if (register) {
      await api.register({ nome, email, senha });
      created = true;
    }
    const session = await api.login(email, senha);
    if (!session?.access_token) throw new Error('A API não retornou um token de acesso.');
    setToken(session.access_token);
    const user = await api.me();
    authPending(false);
    await enterApp(user);
    $('#auth-form').reset();
    if (created) notify('Conta criada. Seu controle financeiro já pode começar.');
  } catch (error) {
    if (created) {
      authPending(false);
      switchAuth('login');
      $('#auth-email').value = email;
      message('#auth-message', 'Sua conta foi criada, mas não foi possível entrar automaticamente. Entre com o e-mail e a senha cadastrados.');
    } else message('#auth-message', error.message);
  } finally {
    authPending(false);
  }
}

async function enterApp(user) {
  state.user = user;
  $('#auth').hidden = true;
  $('#application').hidden = false;
  $('#user-name').textContent = user.nome;
  $('#user-avatar').textContent = user.nome.trim().slice(0, 1).toLocaleUpperCase('pt-BR') || 'U';
  $('#editor').hidden = true;
  $('.skip-link').href = '#main';
  renderPage();
  await loadData();
}
function restorePendingDraft() {
  if (pendingDraft && state.user) {
    const draft = pendingDraft;
    pendingDraft = null;
    if (draft.ownerId === state.user.id) {
      const kind = draft.editor.kind;
      const source = kind === 'contribution' ? state.goals : state[collections[kind]];
      const item = draft.editor.item ? source.find(record => record.id === draft.editor.item.id) : null;
      if (!draft.editor.item || item) {
        openEditor(kind, item);
        for (const [name, value] of draft.values) {
          const input = $('#record-form').elements.namedItem(name);
          if (input) input.value = value;
        }
        notify('Seu formulário foi recuperado. Confira os dados antes de salvar.');
      }
    }
  }
}
async function loadData() {
  const version = ++loadVersion;
  $('#loading').hidden = false;
  $('#load-error').hidden = true;
  $('#main').setAttribute('aria-busy', 'true');
  $('#primary-action').disabled = true;
  try {
    const [transactions, categories, goals] = await Promise.all([api.transactions(), api.categories(), api.goals()]);
    if (version !== loadVersion || !hasToken()) return;
    Object.assign(state, { transactions, categories, goals, loaded: true });
    renderCategoryFilter(categories);
    renderData();
    restorePendingDraft();
    return true;
  } catch (error) {
    if (version !== loadVersion || !hasToken()) return false;
    message('#load-error-text', `${error.message}${state.loaded ? ' Os dados exibidos podem estar desatualizados.' : ''}`);
    $('#load-error').hidden = false;
    return false;
  } finally {
    if (version === loadVersion) {
      $('#loading').hidden = true;
      $('#main').setAttribute('aria-busy', 'false');
      $('#primary-action').disabled = !state.loaded;
    }
  }
}

function renderData() {
  renderSummary(state.transactions);
  renderTransactions(state.transactions, state.categories, currentPage() === 'visao-geral');
  renderGoals(state.goals);
  renderCategories(state.categories);
  renderPage();
}
function renderPage() {
  if (!state.user) return;
  const page = currentPage();
  const [title, description, action] = pages[page];
  document.title = `${title} · Controle financeiro`;
  $('#page-title').textContent = title;
  $('#page-description').textContent = description;
  $('#primary-action span').textContent = action;
  for (const link of $('#navigation').querySelectorAll('a')) {
    if (link.dataset.page === page) link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  }
  $('#overview').hidden = page !== 'visao-geral' || !state.loaded;
  $('#transactions-section').hidden = !['visao-geral', 'transacoes'].includes(page) || !state.loaded;
  $('#filters').hidden = page !== 'transacoes';
  $('#all-transactions').hidden = page !== 'visao-geral';
  $('#transactions-title').textContent = page === 'visao-geral' ? 'Últimas transações' : 'Suas transações';
  $('#planning').hidden = page === 'transacoes' || !state.loaded;
  $('#planning').classList.toggle('single-column', page !== 'visao-geral');
  $('#goals-section').hidden = page === 'categorias';
  $('#categories-section').hidden = page === 'metas';
}

function openEditor(kind, item = null) {
  if (mutationBusy || !state.loaded) return;
  if (editor && !window.confirm('Descartar os dados deste formulário e abrir outro?')) return;
  editor = { kind, item };
  const config = buildForm(kind, item, state.categories);
  $('#editor-title').textContent = config.title;
  $('#record-fields').innerHTML = config.fields;
  $('#record-hint').textContent = config.hint;
  $('#record-submit').textContent = kind === 'contribution' ? 'Guardar valor' : item ? 'Salvar alterações' : 'Salvar';
  message('#record-message', '');
  $('#editor').hidden = false;
  $('#editor').scrollIntoView({ block: 'start', behavior: 'instant' });
  $('#record-fields').querySelector('input, select')?.focus({ preventScroll: true });
}
function closeEditor(ask = true) {
  if (mutationBusy) return;
  if (ask && editor && !window.confirm('Descartar os dados deste formulário?')) return;
  editor = null;
  $('#editor').hidden = true;
  $('#record-form').reset();
  $('#record-fields').replaceChildren();
  $('#primary-action').focus({ preventScroll: true });
}
function mutationPending(pending) {
  mutationBusy = pending;
  $('#record-form').setAttribute('aria-busy', String(pending));
  for (const element of $('#editor').querySelectorAll('button, input, select')) element.disabled = pending;
  for (const button of $('#main').querySelectorAll('[data-edit], [data-delete], [data-create], [data-contribute]')) button.disabled = pending;
  $('#primary-action').disabled = pending || !state.loaded;
  $('#logout').disabled = pending;
}

async function submitRecord(event) {
  event.preventDefault();
  if (!editor || mutationBusy) return;
  const { kind, item } = editor;
  const body = validateRecord(kind, $('#record-form'));
  if (!body) return;
  mutationPending(true);
  const label = $('#record-submit').textContent;
  $('#record-submit').textContent = 'Salvando…';
  message('#record-message', '');
  try {
    if (kind === 'contribution') await api.contribute(item.id, body.valor);
    else if (item) await api.update(resources[kind], item.id, body);
    else await api.create(resources[kind], body);
    mutationPending(false);
    closeEditor(false);
    notify(kind === 'contribution' ? 'Valor guardado na meta.' : item ? 'Alterações salvas.' : 'Registro criado.');
    await loadData();
  } catch (error) {
    if (state.user) message('#record-message', error.message);
  } finally {
    mutationPending(false);
    $('#record-submit').textContent = label;
  }
}

async function removeRecord(kind, item) {
  if (mutationBusy) return;
  const dialog = $('#confirmation');
  const name = item.nome || item.descricao;
  $('#confirmation-title').textContent = 'Excluir registro?';
  $('#confirmation-description').textContent = `“${name}” será excluído. Essa ação não pode ser desfeita.${kind === 'category' ? ' Categorias com transações associadas não podem ser excluídas.' : ''}`;
  dialog.returnValue = 'cancel';
  dialog.showModal();
  dialog.querySelector('[value="cancel"]').focus();
  const answer = await new Promise(resolve => dialog.addEventListener('close', () => resolve(dialog.returnValue), { once: true }));
  if (answer !== 'confirm') return;
  mutationPending(true);
  try {
    await api.remove(resources[kind], item.id);
    if (editor?.kind === kind && editor?.item?.id === item.id) {
      mutationPending(false);
      closeEditor(false);
      mutationPending(true);
    }
    notify('Registro excluído.');
    await loadData();
  } catch (error) {
    if (state.user) {
      message('#load-error-text', error.message);
      $('#load-error').hidden = false;
      $('#load-error').scrollIntoView({ block: 'center', behavior: 'instant' });
    }
  } finally { mutationPending(false); }
}

$('#auth-form').addEventListener('submit', submitAuth);
$('#login-tab').addEventListener('click', () => switchAuth('login'));
$('#register-tab').addEventListener('click', () => switchAuth('register'));
$('#toggle-password').addEventListener('click', () => {
  const visible = $('#auth-password').type === 'password';
  $('#auth-password').type = visible ? 'text' : 'password';
  $('#toggle-password').setAttribute('aria-pressed', String(visible));
  $('#toggle-password').textContent = visible ? 'Ocultar' : 'Mostrar';
});
$('#auth-form').addEventListener('input', event => {
  event.target.setCustomValidity?.('');
  $('#auth-confirm').setCustomValidity('');
});
$('#record-form').addEventListener('input', () => {
  for (const input of $('#record-form').querySelectorAll('input')) input.setCustomValidity('');
});
$('#record-form').addEventListener('submit', submitRecord);
$('#close-editor').addEventListener('click', () => closeEditor());
$('#primary-action').addEventListener('click', () => openEditor(pages[currentPage()][3]));
$('#retry').addEventListener('click', loadData);
$('#logout').addEventListener('click', () => {
  if (mutationBusy) return;
  if (editor && !window.confirm('Sair e descartar o formulário aberto?')) return;
  setToken('');
  pendingDraft = null;
  showAuth();
  $('#auth-email').focus();
});
window.addEventListener('session-expired', () => {
  showAuth('Sua sessão expirou. Entre novamente. Se havia um formulário aberto, ele será recuperado nesta aba ao acessar a mesma conta.', true);
  $('#auth-email').focus();
});
$('#main').addEventListener('click', event => {
  const create = event.target.closest('[data-create]');
  if (create) return openEditor(create.dataset.create);
  const contribute = event.target.closest('[data-contribute]');
  if (contribute) {
    const item = state.goals.find(goal => goal.id === Number(contribute.dataset.contribute));
    if (item) openEditor('contribution', item);
    return;
  }
  const button = event.target.closest('[data-edit], [data-delete]');
  if (!button) return;
  const kind = button.dataset.edit || button.dataset.delete;
  const item = state[collections[kind]]?.find(record => record.id === Number(button.dataset.id));
  if (!item) return;
  if (button.dataset.edit) openEditor(kind, item);
  else removeRecord(kind, item);
});
function filterTransactions() {
  if (state.loaded) renderTransactions(state.transactions, state.categories, false);
}
$('#filters').addEventListener('submit', event => event.preventDefault());
$('#filters').addEventListener('input', filterTransactions);
$('#filters').addEventListener('change', filterTransactions);
$('#filters').addEventListener('reset', () => queueMicrotask(filterTransactions));
window.addEventListener('hashchange', () => {
  if (!state.user) return;
  renderPage();
  if (state.loaded) renderTransactions(state.transactions, state.categories, currentPage() === 'visao-geral');
  $('#main').focus({ preventScroll: true });
});
window.addEventListener('beforeunload', event => {
  if (editor || mutationBusy) { event.preventDefault(); event.returnValue = ''; }
});

async function start() {
  switchAuth('login', false);
  if (!hasToken()) return;
  authPending(true);
  message('#auth-message', 'Conferindo sua sessão…');
  try {
    const user = await api.me();
    authPending(false);
    message('#auth-message', '');
    await enterApp(user);
  } catch (error) {
    authPending(false);
    // Mantém o token em falhas transitórias; credenciais inválidas já são limpas pela API.
    showAuth(error.status === 401 ? 'Sua sessão expirou. Entre novamente.' : error.message);
  } finally { authPending(false); }
}
start();
