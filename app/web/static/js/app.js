// Basic helper to attach Authorization automatically
async function api(path, options = {}) {
  const token = localStorage.getItem("token");
  const headers = options.headers || {};
  if (token) headers["Authorization"] = "Bearer " + token;
  return fetch(path, { ...options, headers });
}
