// Encrypts stdin with a code (argv[2]) exactly as access.js decrypts it:
// PBKDF2-SHA256 -> AES-256-GCM. Prints the JSON payload. Used by tools/build.py.
import { webcrypto as crypto } from 'node:crypto';
const ITERATIONS = 310000;
const code = process.argv[2];
let text = '';
for await (const chunk of process.stdin) text += chunk;
const enc = new TextEncoder();
const salt = crypto.getRandomValues(new Uint8Array(16));
const iv = crypto.getRandomValues(new Uint8Array(12));
const base = await crypto.subtle.importKey('raw', enc.encode(code), 'PBKDF2', false, ['deriveKey']);
const key = await crypto.subtle.deriveKey({ name: 'PBKDF2', salt, iterations: ITERATIONS, hash: 'SHA-256' },
  base, { name: 'AES-GCM', length: 256 }, false, ['encrypt']);
const ct = new Uint8Array(await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, enc.encode(text)));
const b = (u) => Buffer.from(u).toString('base64');
process.stdout.write(JSON.stringify({ v: 1, n: ITERATIONS, s: b(salt), i: b(iv), c: b(ct) }));
