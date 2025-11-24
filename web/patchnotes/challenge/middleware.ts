import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  if (request.nextUrl.pathname.startsWith("/admin")) {
    return new NextResponse("Access to /admin is restricted.", { status: 403 });
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/admin/:path*"]
};
