/* =========================================================================
 * api.js — клиент Django REST API (JWT) с авто-обновлением access-токена
 * =======================================================================*/
(function (App) {
  'use strict';
  const C = App.CONFIG;
  const Auth = App.auth;

  function buildUrl(path) {
    if (/^https?:\/\//.test(path)) return path;
    return (C.API_BASE || '') + path;
  }

  function withQuery(path, params) {
    if (!params) return path;
    const usp = new URLSearchParams();
    Object.keys(params).forEach((k) => {
      const v = params[k];
      if (v !== undefined && v !== null && v !== '') usp.append(k, v);
    });
    const q = usp.toString();
    return q ? `${path}${path.includes('?') ? '&' : '?'}${q}` : path;
  }

  /* ------------------------- обновление токена ------------------------- */
  let refreshing = null;
  async function refreshAccess() {
    const refresh = Auth.getRefresh();
    if (!refresh) return null;
    if (refreshing) return refreshing;

    refreshing = (async () => {
      try {
        // В демо-режиме refresh обрабатывает мок
        const mockResult = App.mock.request('POST', C.ENDPOINTS.refresh, { body: { refresh } });
        let data;
        if (mockResult) {
          data = await mockResult;
        } else {
          const res = await fetch(buildUrl(C.ENDPOINTS.refresh), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh }),
          });
          if (!res.ok) throw new Error('refresh failed');
          data = await res.json();
        }
        if (data && data.access) {
          Auth.setSession({ access: data.access });
          return data.access;
        }
        return null;
      } catch (_) {
        return null;
      } finally {
        refreshing = null;
      }
    })();

    return refreshing;
  }

  /**
   * Выполнить запрос.
   * @param {string} method
   * @param {string} path
   * @param {object} opts { body, isForm, auth=true, _retry }
   */
  async function request(method, path, opts = {}) {
    const { body = null, isForm = false, auth = true, _retry = false } = opts;

    // --- Демо-режим: сначала пробуем мок ---
    const mockResult = App.mock.request(method, path, { body });
    if (mockResult) return mockResult;

    // --- Реальный запрос ---
    const headers = {};
    if (auth && Auth.getAccess()) headers['Authorization'] = 'Bearer ' + Auth.getAccess();

    let payload;
    if (isForm) {
      payload = body; // FormData — Content-Type выставит браузер
    } else if (body != null) {
      headers['Content-Type'] = 'application/json';
      payload = JSON.stringify(body);
    }

    let res;
    try {
      res = await fetch(buildUrl(path), { method, headers, body: payload });
    } catch (networkErr) {
      const err = new Error('Не удалось связаться с сервером. Проверьте соединение и адрес API.');
      err.status = 0;
      throw err;
    }

    // 401 -> пробуем обновить токен один раз
    if (res.status === 401 && auth && !_retry) {
      const newAccess = await refreshAccess();
      if (newAccess) return request(method, path, Object.assign({}, opts, { _retry: true }));
      Auth.clear();
      if (App.shell && App.shell.LOGIN) location.replace(App.shell.LOGIN);
      throw Object.assign(new Error('Сессия истекла, войдите заново.'), { status: 401 });
    }

    // 204 No Content
    if (res.status === 204) return null;

    const text = await res.text();
    let data = null;
    if (text) {
      try { data = JSON.parse(text); } catch (_) { data = text; }
    }

    if (!res.ok) {
      const err = new Error(extractError(data, res.status));
      err.status = res.status;
      err.data = data;
      throw err;
    }
    return data;
  }

  function extractError(data, status) {
    if (data && typeof data === 'object') {
      if (data.detail) return data.detail;
      if (data.message) return data.message;
      // DRF validation errors: { field: ["msg", ...] }
      const parts = [];
      for (const key of Object.keys(data)) {
        const val = Array.isArray(data[key]) ? data[key].join(', ') : data[key];
        parts.push(key === 'non_field_errors' ? val : `${key}: ${val}`);
      }
      if (parts.length) return parts.join('; ');
    }
    if (typeof data === 'string' && data) return data;
    return `Ошибка запроса (${status})`;
  }

  /* ------------------------------ методы ------------------------------ */
  const api = {
    buildUrl, withQuery, request,
    get: (path, params) => request('GET', withQuery(path, params)),
    post: (path, body) => request('POST', path, { body }),
    postForm: (path, formData) => request('POST', path, { body: formData, isForm: true }),
    patch: (path, body) => request('PATCH', path, { body }),
    put: (path, body) => request('PUT', path, { body }),
    del: (path) => request('DELETE', path),

    async login(username, password) {
      const data = await request('POST', C.ENDPOINTS.login, {
        body: { username, password }, auth: false,
      });
      const access = data.access || data.token || data.key;
      const refresh = data.refresh || null;
      if (!access) throw new Error('Сервер не вернул токен доступа.');
      let user = data.user || null;
      Auth.setSession({ access, refresh, user });
      if (!user) {
        user = await request('GET', C.ENDPOINTS.me, { _retry: true });
        Auth.setUser(user);
      }
      return user;
    },

    async fetchMe() {
      return request('GET', C.ENDPOINTS.me, { _retry: true });
    },

    logout() { Auth.clear(); },
  };

  App.api = api;
})(window.App);
