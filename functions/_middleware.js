const BACKEND_URL = 'https://jasonslav.pythonanywhere.com';

export async function onRequest(context) {
  const { request } = context;
  const url = new URL(request.url);
  
  const apiPaths = ['/upload', '/generate_chart', '/debug_col'];
  if (!apiPaths.includes(url.pathname)) {
    return context.next();
  }

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