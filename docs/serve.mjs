#!/usr/bin/env node
// Optional, dependency-free local docs server. Run: node docs/serve.mjs
import http from 'node:http';
import https from 'node:https';
import { constants } from 'node:fs';
import { open, realpath } from 'node:fs/promises';
import { isIP } from 'node:net';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const API_PREFIXES = new Set([
  'auth', 'usuarios', 'categorias', 'transacoes', 'metas', 'relatorios',
]);
const API_METHODS = new Set(['GET', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']);
const PROXY_TIMEOUT_MS = 30_000;
const HOP_HEADERS = new Set([
  'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
  'te', 'trailer', 'transfer-encoding', 'upgrade', 'proxy-connection',
]);
const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.svg': 'image/svg+xml',
};

function configuration() {
  const host = process.env.HOST ?? '127.0.0.1';
  const portText = process.env.PORT ?? '5500';
  const hostnameValid = host.length <= 253 && host.split('.').every(
    (label) => /^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$/i.test(label),
  );
  if (!isIP(host) && !hostnameValid) {
    throw new Error('HOST must be an IP address or valid hostname (IPv6 without brackets).');
  }
  if (!/^\d+$/.test(portText) || Number(portText) < 1 || Number(portText) > 65535) {
    throw new Error('PORT must be an integer between 1 and 65535.');
  }
  const api = new URL(process.env.API_URL ?? 'http://127.0.0.1:8000');
  if (!['http:', 'https:'].includes(api.protocol)
    || !api.hostname || api.username || api.password || api.search || api.hash) {
    throw new Error('API_URL must be an HTTP(S) URL without credentials, query, or fragment.');
  }
  api.pathname = api.pathname.replace(/\/+$/, '');
  return { host, port: Number(portText), api };
}

function json(res, status, detail, extraHeaders = {}) {
  if (res.destroyed || res.writableEnded) return;
  const body = JSON.stringify({ detail });
  res.writeHead(status, {
    'content-type': 'application/json; charset=utf-8',
    'content-length': Buffer.byteLength(body),
    'cache-control': 'no-store',
    'x-content-type-options': 'nosniff',
    ...extraHeaders,
  });
  res.end(body);
}

function cleanHeaders(headers) {
  const excluded = new Set(HOP_HEADERS);
  for (const name of String(headers.connection ?? '').split(',')) {
    excluded.add(name.trim().toLowerCase());
  }
  return Object.fromEntries(
    Object.entries(headers).filter(([name]) => !excluded.has(name.toLowerCase())),
  );
}

function allowedAsset(relative) {
  return relative === 'index.html' || relative === 'favicon.svg'
    || /^(?:css\/(?:[^/]+\/)*[^/]+\.css|js\/(?:[^/]+\/)*[^/]+\.js)$/.test(relative);
}

function safeSegments(pathname) {
  return !pathname.includes('\\') && !/[\u0000-\u001f\u007f%]/.test(pathname)
    && pathname.split('/').every((segment) => !segment.startsWith('.'));
}

async function serveAsset(req, res, pathname, root) {
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    json(res, 405, 'Static files support GET and HEAD only.', { allow: 'GET, HEAD' });
    return;
  }
  const relative = pathname === '/' ? 'index.html' : pathname.slice(1);
  if (!allowedAsset(relative)) {
    json(res, 404, 'Not found.');
    return;
  }
  let file;
  try {
    const resolved = await realpath(path.join(root, relative));
    const actualRelative = path.relative(root, resolved);
    // Check the canonical target too: even an in-root symlink cannot expose docs/source.
    if (path.isAbsolute(actualRelative) || !safeSegments(actualRelative)
      || !allowedAsset(actualRelative.split(path.sep).join('/'))) {
      json(res, 404, 'Not found.');
      return;
    }
    file = await open(resolved, constants.O_RDONLY | constants.O_NOFOLLOW);
    const stat = await file.stat();
    if (!stat.isFile()) {
      await file.close();
      file = undefined;
      json(res, 404, 'Not found.');
      return;
    }
    if (res.destroyed) {
      await file.close();
      return;
    }
    res.writeHead(200, {
      'content-type': MIME_TYPES[path.extname(relative)],
      'content-length': stat.size,
      'cache-control': 'no-store',
      'x-content-type-options': 'nosniff',
    });
    if (req.method === 'HEAD') {
      await file.close();
      res.end();
      return;
    }
    const stream = file.createReadStream();
    file = undefined; // The stream now owns and closes the descriptor.
    stream.on('error', () => res.destroy());
    res.on('close', () => stream.destroy());
    stream.pipe(res);
  } catch (error) {
    if (file) await file.close().catch(() => {});
    if (res.headersSent) {
      res.destroy();
    } else {
      json(res, ['ENOENT', 'ENOTDIR', 'EACCES', 'ELOOP'].includes(error.code) ? 404 : 500,
        error.code === 'ENOENT' ? 'Not found. Create the docs assets first.' : 'Static file unavailable.');
    }
  }
}

function proxy(req, res, rawPath, query, api) {
  if (!API_METHODS.has(req.method)) {
    json(res, 405, 'Unsupported API method.', { allow: [...API_METHODS].join(', ') });
    return;
  }
  // Concatenate validated paths, never resolve user input as a URL or follow redirects.
  const basePath = api.pathname.replace(/\/+$/, '');
  const headers = cleanHeaders(req.headers);
  headers.host = api.host;
  // Untrusted forwarding headers are not needed by this local helper.
  delete headers.forwarded;
  for (const name of Object.keys(headers)) {
    if (name.startsWith('x-forwarded-')) delete headers[name];
  }
  let response;
  let failed = false;
  const transport = api.protocol === 'https:' ? https : http;
  const upstream = transport.request({
    protocol: api.protocol,
    hostname: api.hostname.replace(/^\[|\]$/g, ''),
    port: api.port || undefined,
    method: req.method,
    path: `${basePath}${rawPath.slice(4)}${query}`,
    headers,
  });
  const timer = setTimeout(() => fail('API request timed out after 30 seconds.'), PROXY_TIMEOUT_MS);
  timer.unref();

  function fail(detail = 'API unavailable. Check that the backend is running and API_URL is correct.') {
    if (failed) return;
    failed = true;
    clearTimeout(timer);
    req.unpipe(upstream);
    req.resume();
    upstream.destroy();
    response?.destroy();
    if (res.headersSent) res.destroy();
    else json(res, 502, detail);
  }

  upstream.on('error', () => fail());
  upstream.on('response', (incoming) => {
    response = incoming;
    if (failed || res.destroyed) {
      incoming.destroy();
      return;
    }
    const responseHeaders = cleanHeaders(incoming.headers);
    // FastAPI's slash redirects must stay on the docs origin.
    if (responseHeaders.location) {
      try {
        const location = new URL(responseHeaders.location, api.origin + basePath + rawPath.slice(4));
        if (location.origin === api.origin
          && (location.pathname === basePath || location.pathname.startsWith(`${basePath}/`))) {
          responseHeaders.location = `/api${location.pathname.slice(basePath.length)}${location.search}${location.hash}`;
        }
      } catch {
        delete responseHeaders.location;
      }
    }
    incoming.on('error', () => fail());
    incoming.on('aborted', () => fail());
    res.writeHead(incoming.statusCode ?? 502, responseHeaders);
    incoming.pipe(res);
  });
  req.on('aborted', () => fail('Client disconnected.'));
  req.on('error', () => fail('Client request failed.'));
  res.on('close', () => {
    clearTimeout(timer);
    if (!res.writableFinished) {
      upstream.destroy();
      response?.destroy();
    }
  });
  res.on('finish', () => clearTimeout(timer));
  req.pipe(upstream);
}

async function main() {
  const { host, port, api } = configuration();
  const root = await realpath(fileURLToPath(new URL('.', import.meta.url)));
  const server = http.createServer((req, res) => {
    // Inspect the raw origin-form path before WHATWG URL normalization can erase traversal.
    const target = req.url ?? '';
    const queryIndex = target.indexOf('?');
    const rawPath = queryIndex < 0 ? target : target.slice(0, queryIndex);
    const query = queryIndex < 0 ? '' : target.slice(queryIndex);
    let pathname;
    try {
      pathname = decodeURIComponent(rawPath);
    } catch {
      json(res, 400, 'Malformed request path.');
      return;
    }
    if (!rawPath.startsWith('/') || rawPath.startsWith('//')
      || /%2f|%5c/i.test(rawPath) || !safeSegments(pathname)) {
      json(res, 400, 'Unsafe request path.');
      return;
    }
    if (pathname === '/api' || pathname.startsWith('/api/')) {
      if (!rawPath.startsWith('/api/')) {
        json(res, 400, 'Use the literal /api/ prefix.');
        return;
      }
      if (!API_PREFIXES.has(pathname.split('/')[2])) {
        json(res, 404, 'Unknown API route.');
        return;
      }
      proxy(req, res, rawPath, query, api);
      return;
    }
    void serveAsset(req, res, pathname, root);
  });
  server.requestTimeout = PROXY_TIMEOUT_MS;
  server.headersTimeout = 15_000;
  server.on('error', (error) => {
    console.error(`Frontend server: ${error.message}`);
    process.exitCode = 1;
  });
  server.listen(port, host, () => {
    const address = isIP(host) === 6 ? `[${host}]` : host;
    console.log(`Frontend: http://${address}:${port}`);
    console.log(`API proxy: /api/{${[...API_PREFIXES].join(',')}} → ${api.href}`);
    console.log('Usage: node docs/serve.mjs');
    console.log('Overrides: HOST=127.0.0.1 PORT=5500 API_URL=http://127.0.0.1:8000 node docs/serve.mjs');
  });
}

main().catch((error) => {
  console.error(`Frontend server: ${error.message}`);
  process.exitCode = 1;
});
