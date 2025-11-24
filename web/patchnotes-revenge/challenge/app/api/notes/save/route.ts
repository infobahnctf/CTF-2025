'use server';
import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

const ALLOW_SAVE = ['.json', '.txt'];
const BASE_DIR = '/tmp/data';

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { file, content } = body || {};

    if (!file || typeof content !== 'string') {
      return NextResponse.json({ error: 'file and content required' }, { status: 400 });
    }

    const ok = ALLOW_SAVE.some(ext => file.endsWith(ext));
    if (!ok) return NextResponse.json({ error: 'extension not allowed for save' }, { status: 400 });

    if (!BASE_DIR) return NextResponse.json({ error: 'data directory not found' }, { status: 500 });

    const fullPath = path.join(BASE_DIR, file);

    await fs.writeFile(fullPath, content, 'utf8');

    return NextResponse.json({ ok: true });
  } catch (e: any) {
    return NextResponse.json({ error: 'internal' }, { status: 500 });
  }
}
