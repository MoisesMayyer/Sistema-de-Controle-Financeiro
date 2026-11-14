import { actionButtons, cents, dateLabel, emptyState, escapeHtml as e, money } from './utils.js';

export function renderSummary(transactions) {
  let income = 0;
  let expense = 0;
  for (const item of transactions) {
    if (item.tipo === 'receita') income += cents(item.valor);
    else expense += cents(item.valor);
  }
  document.querySelector('#income').textContent = money(income / 100);
  document.querySelector('#expenses').textContent = money(expense / 100);
  const balance = document.querySelector('#balance');
  balance.textContent = money((income - expense) / 100);
  balance.classList.toggle('expense-text', income < expense);
}

export function renderTransactions(transactions, categories, overview) {
  const search = overview ? '' : document.querySelector('#search').value.trim().toLocaleLowerCase('pt-BR');
  const type = overview ? '' : document.querySelector('#type-filter').value;
  const category = overview ? '' : document.querySelector('#category-filter').value;
  const filtered = transactions.filter(item =>
    (!search || item.descricao.toLocaleLowerCase('pt-BR').includes(search))
    && (!type || item.tipo === type)
    && (!category || String(item.categoria_id) === category));
  const visible = overview ? filtered.slice(0, 5) : filtered;
  document.querySelector('#transaction-count').textContent = overview
    ? `${Math.min(filtered.length, 5)} de ${filtered.length} registros`
    : `${filtered.length} ${filtered.length === 1 ? 'transação encontrada' : 'transações encontradas'}`;
  const container = document.querySelector('#transaction-list');
  if (!visible.length) {
    container.innerHTML = transactions.length
      ? emptyState('Nenhuma transação encontrada', 'Tente outra busca ou limpe os filtros.')
      : emptyState('Seu controle começa aqui', 'Adicione sua primeira receita ou despesa para acompanhar seu dinheiro.', 'transaction', 'Adicionar transação');
    return;
  }
  const categoryMap = new Map(categories.map(item => [item.id, item.nome]));
  container.innerHTML = `<table class="transaction-table">
    <caption class="sr-only">${overview ? 'Últimas cinco transações' : 'Transações encontradas'}, ordenadas por data mais recente</caption>
    <thead><tr><th scope="col">Descrição</th><th scope="col" class="date-col">Data</th><th scope="col" class="category-col">Categoria</th><th scope="col" class="amount amount-col">Valor</th><th scope="col" class="actions-col"><span class="sr-only">Ações</span></th></tr></thead>
    <tbody>${visible.map(item => {
      const categoryName = categoryMap.get(item.categoria_id) || 'Sem categoria';
      return `<tr><td class="description">${e(item.descricao)}<div class="mobile-meta">${e(dateLabel(item.data))} · ${e(categoryName)}</div></td>
        <td class="date-col">${e(dateLabel(item.data))}</td>
        <td class="category-col"><span class="category-tag">${e(categoryName)}</span></td>
        <td class="amount ${item.tipo === 'receita' ? 'income-text' : 'expense-text'}">${item.tipo === 'receita' ? '+' : '−'} ${e(money(item.valor))}<span class="type-label">${item.tipo === 'receita' ? 'Receita' : 'Despesa'}</span></td>
        <td class="actions-col">${actionButtons('transaction', item)}</td></tr>`;
    }).join('')}</tbody></table>`;
}

export function renderGoals(goals) {
  document.querySelector('#goal-list').innerHTML = goals.length ? goals.map(item => {
    const percentage = Math.max(0, Math.min(100, Number(item.porcentagem) || 0));
    const completed = cents(item.valor_inicial) >= cents(item.valor_final);
    return `<article class="goal-item ${completed ? 'complete' : ''}">
      <div class="item-header"><div class="item-copy"><h3>${e(item.nome)}</h3><p>${item.data_fim ? `Até ${e(dateLabel(item.data_fim))}` : 'Sem prazo definido'}</p></div>${actionButtons('goal', item)}</div>
      <div class="goal-amounts"><strong>${e(money(item.valor_inicial))}</strong><span>de ${e(money(item.valor_final))}</span></div>
      <progress max="100" value="${percentage}" aria-label="Progresso de ${e(item.nome)}">${percentage}%</progress>
      <div class="goal-footer"><span>${completed ? 'Meta alcançada' : `${percentage.toLocaleString('pt-BR')}% concluído`}</span>
      ${completed ? '' : `<button class="button subtle" type="button" data-contribute="${item.id}" aria-label="Guardar valor em ${e(item.nome)}">Guardar valor <span aria-hidden="true">→</span></button>`}</div>
    </article>`;
  }).join('') : emptyState('Dê um destino ao que você guarda', 'Crie uma meta e acompanhe quanto falta para chegar lá.', 'goal', 'Criar primeira meta');
}

export function renderCategories(categories) {
  document.querySelector('#category-list').innerHTML = categories.length ? categories.map(item => {
    const spent = Number(item.total_despesas) || 0;
    const over = spent > Number(item.valor_limite);
    return `<article class="category-item"><div class="item-copy"><h3>${e(item.nome)}</h3>
      <p>${e(money(spent))} em despesas · limite ${e(money(item.valor_limite))}</p>
      <div class="category-type ${over ? 'expense-text' : ''}">${over ? 'Limite ultrapassado' : `${Number(item.porcentagem_limite || 0).toLocaleString('pt-BR')}% do limite utilizado`} · Saldo ${e(money(item.saldo))}</div>
    </div>${actionButtons('category', item)}</article>`;
  }).join('') : emptyState('Organize por categoria', 'Agrupe transações e defina um limite para acompanhar seus gastos.', 'category', 'Criar primeira categoria');
}

export function renderCategoryFilter(categories) {
  const select = document.querySelector('#category-filter');
  const previous = select.value;
  select.innerHTML = '<option value="">Todas as categorias</option>' + categories.map(item =>
    `<option value="${item.id}">${e(item.nome)}</option>`).join('');
  if (categories.some(item => String(item.id) === previous)) select.value = previous;
}
