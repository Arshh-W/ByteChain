const API_BASE_URL = https://bytechain.onrender.com;

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      Accept: "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const error = await response.json();
      message = error.detail || error.message || message;
    } catch {
      // Keep the status-based message when the server response is not JSON.
    }
    throw new Error(message);
  }

  return response.json();
}

export function analyzeFile(file) {
  const body = new FormData();
  body.append("file", file);
  return request("/api/analyze", { method: "POST", body });
}
