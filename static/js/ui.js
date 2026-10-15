/* =========================================================================
 * ui.js — небольшая библиотека помощников для построения DOM
 * =======================================================================*/
(function (App) {
  'use strict';

  /**
   * h('div', {class:'x', onclick: fn}, child1, child2, ...)
   * Создаёт DOM-узел. Значениями могут быть строки, узлы, массивы, null.
   */
  function h(tag, attrs, ...children) {
    const el = document.createElement(tag);

    if (attrs && typeof attrs === 'object' && !(attrs instanceof Node) && !Array.isArray(attrs)) {
      for (const key of Object.keys(attrs)) {
        const value = attrs[key];
        if (value === null || value === undefined || value === false) continue;

        if (key === 'class' || key === 'className') {
          el.className = Array.isArray(value) ? value.filter(Boolean).join(' ') : value;
        } else if (key === 'style' && typeof value === 'object') {
          Object.assign(el.style, value);
        } else if (key === 'dataset' && typeof value === 'object') {
          Object.assign(el.dataset, value);
        } else if (key.startsWith('on') && typeof value === 'function') {
          el.addEventListener(key.slice(2).toLowerCase(), value);
        } else if (key === 'html') {
          el.innerHTML = value;
        } else if (key in el && key !== 'list' && key !== 'form') {
          try { el[key] = value; } catch (_) { el.setAttribute(key, value); }
        } else {
          el.setAttribute(key, value === true ? '' : value);
        }
      }
    } else if (attrs !== undefined && attrs !== null) {
      children.unshift(attrs);
    }

    appendChildren(el, children);
    return el;
  }

  function appendChildren(el, children) {
    for (const child of children.flat(Infinity)) {
      if (child === null || child === undefined || child === false || child === true) continue;
      el.appendChild(child instanceof Node ? child : document.createTextNode(String(child)));
    }
  }

  /** Очистить контейнер и вставить новые узлы. */
  function mount(container, ...nodes) {
    container.innerHTML = '';
    appendChildren(container, nodes);
    return container;
  }

  /** Универсальная текстовая экранизация. */
  function esc(str) {
    return String(str === null || str === undefined ? '' : str)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#039;');
  }

  /** Дата ISO/sql -> 'дд.мм.гггг' */
  function formatDate(value) {
    if (!value) return '—';
    const d = new Date(value);
    if (isNaN(d)) return String(value);
    return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' });
  }

  /** Время 'чч:мм' */
  function formatTime(value) {
    if (!value) return '—';
    return String(value).slice(0, 5);
  }

  /** Склонение: plural(5,'ученик','ученика','учеников') */
  function plural(n, one, few, many) {
    const mod10 = n % 10, mod100 = n % 100;
    if (mod10 === 1 && mod100 !== 11) return `${n} ${one}`;
    if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return `${n} ${few}`;
    return `${n} ${many}`;
  }

  /* ------------------------------- Toast ------------------------------- */
  function toast(message, type = 'info') {
    let holder = document.getElementById('toast-holder');
    if (!holder) {
      holder = h('div', { id: 'toast-holder', class: 'toast-holder' });
      document.body.appendChild(holder);
    }
    const node = h('div', { class: `toast toast--${type}` }, message);
    holder.appendChild(node);
    requestAnimationFrame(() => node.classList.add('is-visible'));
    setTimeout(() => {
      node.classList.remove('is-visible');
      setTimeout(() => node.remove(), 250);
    }, 3200);
  }

  /* ------------------------------- Modal ------------------------------- */
  /**
   * openModal({ title, body, submitLabel, onSubmit, wide, onOpen })
   *  - body: Node | Node[] | render(form) callback
   *  - onSubmit: (form) => Promise|void. Возвращает false — не закрывать.
   */
  function openModal(opts) {
    const {
      title = '', body = null, submitLabel = 'Сохранить',
      onSubmit = null, cancelLabel = 'Отмена', wide = false, danger = false,
    } = opts || {};

    const overlay = h('div', { class: 'modal-overlay' });
    const form = h('form', { class: `modal ${wide ? 'modal--wide' : ''}` });
    const errorBox = h('div', { class: 'modal__error', style: { display: 'none' } });

    const close = () => {
      overlay.classList.remove('is-open');
      overlay.remove();
    };

    form.appendChild(h('div', { class: 'modal__head' },
      h('h3', { class: 'modal__title' }, title),
      h('button', { type: 'button', class: 'modal__close', onclick: close, 'aria-label': 'Закрыть' }, '✕'),
    ));
    errorBox.appendChild(h('span', { html: '&nbsp;' }));
    form.appendChild(errorBox);

    const bodyWrap = h('div', { class: 'modal__body' });
    if (typeof body === 'function') bodyWrap.appendChild(body(form));
    else if (body) appendChildren(bodyWrap, [body]);
    form.appendChild(bodyWrap);

    const footer = h('div', { class: 'modal__foot' },
      h('button', { type: 'button', class: 'btn btn--ghost', onclick: close }, cancelLabel),
    );
    if (onSubmit) {
      footer.appendChild(h('button', { type: 'submit', class: `btn btn--${danger ? 'danger' : 'primary'}` }, submitLabel));
    }
    form.appendChild(footer);

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!onSubmit) return close();
      const submitBtn = footer.querySelector('button[type="submit"]');
      if (submitBtn) { submitBtn.disabled = true; submitBtn.classList.add('is-loading'); }
      errorBox.style.display = 'none';
      try {
        const result = await onSubmit(form);
        if (result !== false) close();
      } catch (err) {
        errorBox.style.display = '';
        errorBox.firstChild.innerHTML = esc(err && err.message ? err.message : 'Произошла ошибка');
      } finally {
        if (submitBtn) { submitBtn.disabled = false; submitBtn.classList.remove('is-loading'); }
      }
    });

    overlay.appendChild(form);
    overlay.addEventListener('mousedown', (e) => { if (e.target === overlay) close(); });
    document.addEventListener('keydown', function onEsc(e) {
      if (e.key === 'Escape') { close(); document.removeEventListener('keydown', onEsc); }
    });
    document.body.appendChild(overlay);
    overlay.classList.add('is-open');
    const firstInput = form.querySelector('input, select, textarea');
    if (firstInput) setTimeout(() => firstInput.focus(), 60);
    if (opts && typeof opts.onOpen === 'function') opts.onOpen(form);
    return { close, form };
  }

  /** Диалог подтверждения. */
  function confirmDialog(message, { title = 'Подтверждение', confirmLabel = 'Удалить' } = {}) {
    return new Promise((resolve) => {
      const modal = openModal({
        title, body: h('p', { class: 'confirm-text' }, message),
        submitLabel: confirmLabel, cancelLabel: 'Отмена', danger: true,
        onSubmit: () => resolve(true),
      });
      const overlay = modal.form.closest('.modal-overlay');
      if (!overlay) return;
      const finish = (val) => { resolve(val); modal.close(); };
      overlay.querySelector('.modal__close').addEventListener('click', () => finish(false));
      overlay.querySelectorAll('.btn--ghost').forEach((b) => b.addEventListener('click', () => finish(false)));
      overlay.addEventListener('mousedown', (e) => { if (e.target === overlay) finish(false); });
    });
  }

  /* ------------------------------ Form fields ------------------------------ */
  function field(label, control, hint) {
    return h('label', { class: 'field' },
      h('span', { class: 'field__label' }, label),
      control,
      hint ? h('span', { class: 'field__hint' }, hint) : null,
    );
  }

  function input(name, opts = {}) {
    return h('input', Object.assign({ class: 'input', name, autocomplete: 'off' }, opts));
  }

  function select(name, options, opts = {}) {
    const sel = h('select', Object.assign({ class: 'input', name }, opts));
    for (const opt of options) {
      const value = typeof opt === 'string' ? opt : opt.value;
      const label = typeof opt === 'string' ? opt : opt.label;
      sel.appendChild(h('option', { value }, label));
    }
    return sel;
  }

  /* ------------------------------- Misc -------------------------------- */
  function statusBadge(text) {
    const map = {
      'В работе': 'wip', 'Готово к зачету': 'ready', 'Сдано': 'done',
      'Сдан': 'done', 'Зачёт': 'done',
    };
    const cls = map[text] || 'neutral';
    return h('span', { class: `badge badge--${cls}` }, text);
  }

  function gradeBadge(value) {
    if (value === null || value === undefined || value === '') return h('span', { class: 'grade grade--none' }, '—');
    const n = Number(value);
    return h('span', { class: `grade grade--${n}` }, String(value));
  }

  function spinner(text = 'Загрузка…') {
    return h('div', { class: 'state' }, h('div', { class: 'spinner' }), h('span', null, text));
  }

  function emptyState(text, action) {
    return h('div', { class: 'state state--empty' },
      h('div', { class: 'state__icon', html: '🗒️' }),
      h('p', null, text),
      action || null,
    );
  }

  function errorState(text, onRetry) {
    return h('div', { class: 'state state--error' },
      h('div', { class: 'state__icon', html: '⚠️' }),
      h('p', null, text),
      onRetry ? h('button', { class: 'btn btn--ghost', onclick: onRetry }, 'Повторить') : null,
    );
  }

  /**
   * Асинхронный экран: спиннер -> render(data) | errorState с повтором.
   * @param {HTMLElement} container
   * @param {() => Promise<any>} loader
   * @param {(data:any) => Node|Node[]} render
   */
  async function asyncView(container, loader, render) {
    mount(container, spinner());
    try {
      const data = await loader();
      mount(container, render(data));
    } catch (err) {
      console.error(err);
      mount(container, errorState(err && err.message ? err.message : 'Не удалось загрузить данные', () => asyncView(container, loader, render)));
    }
  }

  App.ui = {
    h, mount, esc, formatDate, formatTime, plural,
    toast, openModal, confirmDialog,
    field, input, select,
    statusBadge, gradeBadge, spinner, emptyState, errorState, asyncView,
    appendChildren,
  };
})(window.App);
