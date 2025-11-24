const cache = new Map();

function arrayBufferToBase64(buffer) {
  return btoa(String.fromCharCode(...new Uint8Array(buffer)));
}

function base64ToArrayBuffer(base64) {
  return Uint8Array.from(atob(base64), (c) => c.charCodeAt(0)).buffer;
}

async function getKey() {
  const stored = await chrome.storage.local.get("key");
  let exportedKey = stored.key;

  if (!exportedKey) {
    const key = await crypto.subtle.generateKey(
      { name: "AES-GCM", length: 256 },
      true,
      ["encrypt", "decrypt"]
    );
    exportedKey = await crypto.subtle.exportKey("jwk", key);
    await chrome.storage.local.set({ key: exportedKey });
    return key;
  }

  const key = await crypto.subtle.importKey(
    "jwk",
    exportedKey,
    { name: "AES-GCM" },
    false,
    ["encrypt", "decrypt"]
  );
  return key;
}

async function getPasswords() {
  let { passwords } = await chrome.storage.local.get("passwords");
  if (!passwords) {
    passwords = Object.create(null);
    await chrome.storage.local.set({ passwords });
  }
  return passwords;
}

async function getOrigins() {
  const passwords = await getPasswords();
  return Object.keys(passwords);
}

async function getCredential(sender) {
  const url = new URL(sender.url);
  const path = url.origin + url.pathname;

  if (cache.has(path)) {
    return cache.get(path);
  }
  const key = await getKey();
  const passwords = await getPasswords();

  const item = passwords[sender.origin];
  if (!item) return null;

  const { iv, encrypted } = item;
  const ivBuffer = base64ToArrayBuffer(iv);
  const encryptedBuffer = base64ToArrayBuffer(encrypted);

  const decoder = new TextDecoder();
  const decrypted = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv: new Uint8Array(ivBuffer) },
    key,
    encryptedBuffer
  );
  const data = JSON.parse(decoder.decode(decrypted));
  cache.set(path, data);
  return data;
}

async function saveCredential(sender, login, password) {
  const origin = sender.origin;
  const url = new URL(sender.url);
  const path = url.origin + url.pathname;

  const key = await getKey();
  const passwords = await getPasswords();

  const encoder = new TextEncoder();
  const data = encoder.encode(JSON.stringify({ origin, login, password }));
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const encrypted = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv },
    key,
    data
  );

  passwords[origin] = {
    iv: arrayBufferToBase64(iv.buffer),
    encrypted: arrayBufferToBase64(encrypted),
  };

  await chrome.storage.local.set({ passwords });
  cache.set(path, { origin, login, password });
  return true;
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "getOrigins") {
    getOrigins().then(sendResponse);
    return true;
  }

  if (msg.action === "getCredential") {
    getCredential(sender).then(sendResponse);
    return true;
  }
  if (msg.action === "saveCredential") {
    saveCredential(sender, msg.login, msg.password).then((ok) => {
      sendResponse({ success: ok });
    });
    return true;
  }
});
