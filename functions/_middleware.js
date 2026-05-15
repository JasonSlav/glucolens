export async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  
  const apiPaths = ['/upload', '/generate_chart', '/debug_col'];
  if (!apiPaths.includes(url.pathname)) {
    return context.next();
  }

  // Gunakan env variable, fallback ke hardcode jika belum disetel
  const BACKEND_URL = env.BACKEND_URL || 'https://jasonslav.pythonanywhere.com';
  url.hostname = new URL(BACKEND_URL).hostname;
  url.protocol = new URL(BACKEND_URL).protocol;

  const modifiedRequest = new Request(url.toString(), {
    method: request.method,
    headers: request.headers,
    body: request.body,
    redirect: 'follow'
  });

  return fetch(modifiedRequest);
}