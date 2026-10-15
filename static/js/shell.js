/* =========================================================================
 * shell.js — оболочка многостраничного HTML-приложения:
 * проверка доступа по роли, заполнение сайдбара, логаут, демо-баннер.
 * =======================================================================*/
(function (App) {
  'use strict';
  const { h } = App.ui;

  const ROLE_LABEL = { DIRECTOR: 'Директор', TEACHER: 'Преподаватель', STUDENT: 'Ученик' };

  function initials(name) {
    if (!name) return '?';
    return String(name).split(/\s+/).slice(0, 2).map((w) => (w.charAt(0) || '').toUpperCase()).join('');
  }

  const shell = {
    LOGIN: 'login.html',
    folder: '', // папка текущей страницы ('director' | 'teacher' | 'student')
    // По умолчанию — пути из корня (для login.html). Страницы в подпапках
    // переопределяют на 'dashboard.html' вызовом App.shell.setup({ home: ... }).
    HOME: { DIRECTOR: 'director/dashboard.html', TEACHER: 'teacher/dashboard.html', STUDENT: 'student/dashboard.html' },
    ROLE_FOLDER: { DIRECTOR: 'director', TEACHER: 'teacher', STUDENT: 'student' },

    /** Настроить пути страниц (вызывается из каждой страницы). */
    setup(opts) {
      if (opts && opts.login) shell.LOGIN = opts.login;
      if (opts && opts.folder) shell.folder = opts.folder;
      if (opts && opts.home) {
        shell.HOME.DIRECTOR = opts.home;
        shell.HOME.TEACHER = opts.home;
        shell.HOME.STUDENT = opts.home;
      }
    },

    /** Путь к главной роли относительно текущей страницы. */
    homePathFor(role) {
      const folder = shell.ROLE_FOLDER[String(role || '').toUpperCase()];
      if (!folder) return shell.LOGIN;
      // Все страницы лежат на одном уровне: <роль>/dashboard.html.
      // Из любой подпапки до соседней роли путь ../<роль>/dashboard.html.
      return shell.folder ? `../${folder}/dashboard.html` : `${folder}/dashboard.html`;
    },

    /**
     * Проверка доступа. Если не авторизован — на страницу входа;
     * если роль не подходит — на главную своей роли. Возвращает true/false.
     */
    guard(roles) {
      if (!App.auth.isAuthenticated()) {
        location.replace(shell.LOGIN);
        return false;
      }
      const role = App.auth.getRole();
      if (roles && roles.length && !roles.includes(role)) {
        App.ui.toast('Недостаточно прав для этого раздела', 'error');
        location.replace(shell.homePathFor(role));
        return false;
      }
      return true;
    },

    /** Инициализация оболочки страницы (topbar, сайдбар, логаут, баннер). */
    init(opts) {
      const user = App.auth.getUser() || {};
      const role = App.auth.getRole();

      if (opts && opts.title) document.title = opts.title + ' — Э-Күндөлүк';

      const titleEl = document.querySelector('.topbar__title');
      if (titleEl) titleEl.textContent = (opts && opts.title) || 'Э-Күндөлүк';
      const subEl = document.querySelector('.topbar__subtitle');
      if (subEl && opts && opts.subtitle) subEl.textContent = opts.subtitle;

      const roleChip = document.querySelector('.role-chip');
      if (roleChip) roleChip.textContent = ROLE_LABEL[role] || role;

      const nameEl = document.querySelector('[data-user-name]');
      if (nameEl) nameEl.textContent = user.full_name || user.username || 'Пользователь';
      const avatarEl = document.querySelector('[data-user-avatar]');
      if (avatarEl) avatarEl.textContent = initials(user.full_name || user.username || '');

      const logoutBtn = document.getElementById('logout-btn');
      if (logoutBtn) logoutBtn.addEventListener('click', () => { App.api.logout(); location.href = shell.LOGIN; });

      const menuBtn = document.getElementById('menu-btn');
      if (menuBtn) menuBtn.addEventListener('click', () => {
        const shellEl = document.querySelector('.app-shell');
        if (shellEl) shellEl.classList.toggle('sidebar-open');
      });

      // подсветка активного пункта меню
      const current = (location.pathname.split(/[\\/]/).pop() || '').toLowerCase();
      document.querySelectorAll('.nav-item').forEach((a) => {
        const href = ((a.getAttribute('href') || '').split('#')[0]).toLowerCase();
        if (href === current || (href === 'dashboard.html' && current === '')) a.classList.add('is-active');
      });
    },

    logout() {
      App.api.logout();
      location.href = shell.LOGIN;
    },
  };

  App.shell = shell;
  App.homeForRole = (role) => shell.HOME[String(role || '').toUpperCase()] || shell.LOGIN;

  /* -------- общие помощники разметки (используются на всех страницах) -------- */

  App.shell.monthShort = function (dateISO) {
    if (!dateISO) return '';
    const d = new Date(dateISO);
    if (isNaN(d)) return '';
    return ['янв', 'фев', 'мар', 'апр', 'мая', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек'][d.getMonth()];
  };

  App.shell.eventCard = function (ev) {
    return h('div', { class: 'event-card' },
      h('div', { class: 'event-card__date' },
        h('span', { class: 'event-card__day' }, (ev.date || '').slice(8, 10) || '—'),
        h('span', { class: 'event-card__mon' }, App.shell.monthShort(ev.date)),
      ),
      h('div', { class: 'event-card__body' },
        h('h4', null, ev.title),
        h('p', { class: 'muted' },
          '📍 ' + (ev.place || '—'), ' · 🕒 ' + App.ui.formatTime(ev.time), ' · ' + App.ui.formatDate(ev.date)),
        ev.description ? h('p', { class: 'event-card__desc' }, ev.description) : null,
      ),
      Array.prototype.slice.call(arguments, 1).map((action) => h('div', { class: 'event-card__actions' }, action)),
    );
  };

  /** Загрузчик: контейнер -> спиннер -> render(data) | errorState+retry */
  App.shell.loadInto = async function (el, loader, render) {
    App.ui.mount(el, App.ui.spinner('Загрузка…'));
    try {
      const data = await loader();
      App.ui.mount(el, render(data));
    } catch (err) {
      console.error(err);
      App.ui.mount(el, App.ui.errorState(err.message || 'Не удалось загрузить данные', () => App.shell.loadInto(el, loader, render)));
    }
  };
})(window.App);