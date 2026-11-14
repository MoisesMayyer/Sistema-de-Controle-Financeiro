export const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
})[char]);

const currency = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });
export const money = value => currency.format(Number(value) || 0);
export const cents = value => Math.round(Number(value) * 100);
export const amountInput = value => (Number(value) || 0).toFixed(2);
export const today = () => {
  const date = new Date();
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
};
export const dateLabel = value => value ? new Intl.DateTimeFormat('pt-BR').format(new Date(`${value}T12:00:00`)) : 'Sem prazo';

export const icons = {
  edit: '<svg aria-hidden="true" viewBox="0 0 24 24"><path d="m15 5 4 4M4 20l4-1 12-12a3 3 0 0 0-4-4L4 15z"/></svg>',
  delete: '<svg aria-hidden="true" viewBox="0 0 24 24"><path d="M3 6h18M9 6V3h6v3M5 6l1 15h12l1-15M10 10v7M14 10v7"/></svg>',
};

export function actionButtons(kind, item) {
  const name = escapeHtml(item.descricao || item.nome);
  return `<div class="row-actions">
    <button class="icon-button" type="button" data-edit="${kind}" data-id="${item.id}" aria-label="Editar ${name}" title="Editar">${icons.edit}</button>
    <button class="icon-button" type="button" data-delete="${kind}" data-id="${item.id}" aria-label="Excluir ${name}" title="Excluir">${icons.delete}</button>
  </div>`;
}

export function emptyState(title, description, kind, label) {
  return `<div class="empty-state"><h3>${escapeHtml(title)}</h3><p>${escapeHtml(description)}</p>${kind ? `<button type="button" class="button secondary" data-create="${kind}">${escapeHtml(label)}</button>` : ''}</div>`;
}
