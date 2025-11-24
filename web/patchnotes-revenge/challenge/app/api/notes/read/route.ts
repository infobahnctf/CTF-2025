'use server';
import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

const ALLOWED = ['.json', '.txt'];
const BASE_DIR = '/tmp/data';

export async function GET(req: Request) {
  try {
    const url = new URL(req.url);
    const file = url.searchParams.get('file') || '';

    if (!file) {
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

    const text = raw.toString('utf8');
    if (file.endsWith('.json')) {
      try {
        const json = JSON.parse(text);
        return NextResponse.json({ filename: file, content: text, json });
      } catch {
        return NextResponse.json({ filename: file, content: text });
      }
    }

    return NextResponse.json({ filename: file, content: text });
  } catch (e: any) {
    return NextResponse.json({ error: 'internal' }, { status: 500 });
  }
}
