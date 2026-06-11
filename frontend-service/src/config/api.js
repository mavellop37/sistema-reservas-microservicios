const stripTrailingSlash = (url) => url.replace(/\/+$/, "");

export const API_AUTH_URL = stripTrailingSlash(
  import.meta.env.VITE_API_AUTH_URL || "http://127.0.0.1:8000",
);

export const API_RESERVATION_URL = stripTrailingSlash(
  import.meta.env.VITE_API_RESERVATION_URL || "http://127.0.0.1:8001",
);
