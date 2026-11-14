import { amountInput, cents, escapeHtml as e, money, today } from './utils.js';

const amount = (id, label, value, { min = '0.01', max } = {}) =>
  `<div><label for="${id}">${label}</label><input id="${id}" name="${id}" type="number" inputmode="decimal" step="0.01" min="${min}" max="${max ?? '999999999999.99'}" value="${e(amountInput(value))}" required></div>`;
const name = (id, label, value, max) => `<div class="wide"><label for="${id}">${label}</label><input id="${id}" name="${id}" maxlength="${max}" value="${e(value)}" required></div>`;
const date = (id, label, value, required = false) => `<div><label for="${id}">${label}</label><input id="${id}" name="${id}" type="date" value="${e(value)}" ${required ? 'required' : ''}></div>`;

export function buildForm(kind, item, categories) {
  const editing = Boolean(item);
  let fields;
  let hint;
  let title;
  if (kind === 'transaction') {
    title = editing ? 'Editar transação' : 'Nova transação';
    fields = name('descricao', 'Descrição', item?.descricao || '', 255)
      + `<div><label for="tipo">Tipo</label><select id="tipo" name="tipo" required><option value="despesa" ${item?.tipo !== 'receita' ? 'selected' : ''}>Despesa</option><option value="receita" ${item?.tipo === 'receita' ? 'selected' : ''}>Receita</option></select></div>`
      + amount('valor', 'Valor (R$)', item?.valor || 0)
      + date('data', 'Data', item?.data || today(), true)
      + `<div class="wide"><label for="categoria_id">Categoria (opcional)</label><select id="categoria_id" name="categoria_id"><option value="">Sem categoria</option>${categories.map(category => `<option value="${category.id}" ${category.id === item?.categoria_id ? 'selected' : ''}>${e(category.nome)}</option>`).join('')}</select></div>`;
    hint = categories.length ? 'O valor deve ser positivo. O tipo define se é uma entrada ou uma saída.' : 'Você pode salvar sem categoria e organizá-la depois.';
  } else if (kind === 'category') {
    title = editing ? 'Editar categoria' : 'Nova categoria';
    fields = name('nome', 'Nome da categoria', item?.nome || '', 100)
      + amount('valor_inicial', 'Saldo inicial (R$)', item?.valor_inicial || 0, { min: '0' })
      + amount('valor_limite', 'Limite de despesas (R$)', item?.valor_limite || 0);
    hint = 'O limite deve ser maior que o saldo inicial. A API considera todas as despesas da categoria, sem reinício mensal.';
  } else if (kind === 'goal') {
    title = editing ? 'Editar meta' : 'Nova meta';
    fields = name('nome', 'Nome da meta', item?.nome || '', 100)
      + amount('valor_final', 'Valor da meta (R$)', item?.valor_final || 0)
      + amount('valor_inicial', 'Valor já guardado (R$)', item?.valor_inicial || 0, { min: '0' })
      + date('data_inicio', 'Data inicial (opcional)', item?.data_inicio || '')
      + date('data_fim', 'Data final (opcional)', item?.data_fim || '');
    hint = 'Acompanhar uma meta não cria transações nem desconta valores do seu saldo.';
  } else {
    title = 'Guardar valor';
    const remaining = (cents(item.valor_final) - cents(item.valor_inicial)) / 100;
    fields = `<p class="wide">Meta: <strong>${e(item.nome)}</strong>. Faltam ${e(money(remaining))}.</p>`
      + amount('valor', 'Valor para guardar (R$)', 0, { max: amountInput(remaining) });
    hint = 'O valor será somado ao total guardado nesta meta. Isso não cria uma despesa.';
  }
  return { fields, hint, title };
}

export function validateRecord(kind, form) {
  for (const input of form.querySelectorAll('input')) input.setCustomValidity('');
  const data = new FormData(form);
  const text = key => String(data.get(key) || '').trim();
  const number = key => Number(data.get(key));
  const invalid = (key, message) => {
    const input = form.elements.namedItem(key);
    input.setCustomValidity(message);
    input.reportValidity();
    return null;
  };
  if (kind === 'transaction') {
    if (!text('descricao')) return invalid('descricao', 'Escreva uma descrição.');
    return { descricao: text('descricao'), valor: number('valor'), tipo: text('tipo'), data: text('data'), categoria_id: text('categoria_id') ? number('categoria_id') : null };
  }
  if (kind === 'contribution') return { valor: number('valor') };
  if (!text('nome')) return invalid('nome', 'Escreva um nome.');
  if (kind === 'category') {
    if (cents(number('valor_limite')) <= cents(number('valor_inicial'))) return invalid('valor_limite', 'O limite deve ser maior que o saldo inicial.');
    return { nome: text('nome'), valor_inicial: number('valor_inicial'), valor_limite: number('valor_limite') };
  }
  if (cents(number('valor_final')) < cents(number('valor_inicial'))) return invalid('valor_final', 'A meta não pode ser menor que o valor já guardado.');
  if (text('data_inicio') && text('data_fim') && text('data_fim') <= text('data_inicio')) return invalid('data_fim', 'A data final deve ser posterior à data inicial.');
  return { nome: text('nome'), valor_inicial: number('valor_inicial'), valor_final: number('valor_final'), data_inicio: text('data_inicio') || null, data_fim: text('data_fim') || null };
}
