/* =========================================================================
 * store.js — хранение сессии (JWT + данные пользователя)
 * =======================================================================*/
(function (App) {
  'use strict';
  const S = App.CONFIG.STORAGE;

  const Auth = {
    getAccess() { return localStorage.getItem(S.ACCESS); },
    getRefresh() { return localStorage.getItem(S.REFRESH); },

    getUser() {
      try { return JSON.parse(localStorage.getItem(S.USER) || 'null'); }
      catch (_) { return null; }
    },

    setSession({ access, refresh, user }) {
      if (access) localStorage.setItem(S.ACCESS, access);
      if (refresh) localStorage.setItem(S.REFRESH, refresh);
      if (user) localStorage.setItem(S.USER, JSON.stringify(user));
    },

    setUser(user) {
      if (user) localStorage.setItem(S.USER, JSON.stringify(user));
    },

    clear() {
      localStorage.removeItem(S.ACCESS);
      localStorage.removeItem(S.REFRESH);
      localStorage.removeItem(S.USER);
    },

    isAuthenticated() {
      return !!this.getAccess();
    },

    getRole() {
      const u = this.getUser();
      return u && u.role ? String(u.role).toUpperCase() : null;
    },

    hasRole(...roles) {
      const role = this.getRole();
      return roles.map((r) => String(r).toUpperCase()).includes(role);
    },

    displayName() {
      const u = this.getUser();
      if (!u) return '';
      return u.full_name || u.name || u.username || '';
    },
  };

  const ROLE_LABELS = {
    DIRECTOR: 'Директор',
    TEACHER: 'Преподаватель',
    STUDENT: 'Ученик',
  };

  App.auth = Auth;
  App.roleLabel = (role) => ROLE_LABELS[String(role || '').toUpperCase()] || role;
})(window.App);
