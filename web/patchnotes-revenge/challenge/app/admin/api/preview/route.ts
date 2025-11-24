'use server';
import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';
import { Window } from 'happy-dom';

const ALLOWED = ['.json', '.txt'];
const BASE_DIR = '/tmp/data';

export async function POST(req: Request) {
  try {
    const body = await req.json().catch(() => ({}));
    const { file } = body || {};
    if (!file || typeof file !== 'string') {
      return NextResponse.json({ error: 'file param required' }, { status: 400 });
    }

    const okExt = ALLOWED.some(ext => file.endsWith(ext));
    if (!okExt) {
      return NextResponse.json({ error: 'extension not allowed' }, { status: 400 });
    }

    if (!BASE_DIR) {
      return NextResponse.json({ error: 'data directory not found' }, { status: 500 });
    }

    const fullPath = path.join(BASE_DIR, file);
    let raw: Buffer | null = null;
    try {
      raw = await fs.readFile(fullPath);
    } catch (e: any) {
      return NextResponse.json({ error: 'file not found' }, { status: 404 });
    }

    const content = raw.toString('utf8');
    const window = new Window();
    window.document.write(content);

    const rendered = window.document.documentElement?.outerHTML;

    return NextResponse.json({ ok: true, rendered });
  } catch (e: any) {
    return NextResponse.json({ error: 'internal' }, { status: 500 });
  }
}
