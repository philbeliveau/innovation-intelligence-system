import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";
import { NextResponse } from 'next/server'

// Define public routes (everything else requires authentication)
const isPublicRoute = createRouteMatcher([
  "/",
  "/upload",
  "/sign-in(.*)",
  "/sign-up(.*)",
]);

export default clerkMiddleware(async (auth, req) => {
  // Protect all routes except explicitly public ones
  if (!isPublicRoute(req)) {
    await auth.protect();
  }

  // Get response (Clerk middleware returns NextResponse)
  const response = NextResponse.next();

  // Add Content Security Policy headers
  response.headers.set(
    'Content-Security-Policy',
    [
      "default-src 'self'",
      "script-src 'self' 'unsafe-eval' 'unsafe-inline' https://*.clerk.accounts.dev https://*.clerk.com", // Allow Clerk scripts
      "style-src 'self' 'unsafe-inline' https://*.clerk.accounts.dev https://*.clerk.com", // Allow Clerk styles
      "img-src 'self' data: https: blob:", // Allow images from Clerk, Vercel Blob, etc.
      "font-src 'self' data: https://*.clerk.accounts.dev https://*.clerk.com https://r2cdn.perplexity.ai", // Allow Clerk and external fonts
      "connect-src 'self' https://*.clerk.accounts.dev https://*.clerk.com https://*.vercel-storage.com https://*.railway.app",
      "frame-src 'self' https://*.clerk.accounts.dev https://*.clerk.com", // Allow Clerk iframes
      "frame-ancestors 'none'", // Prevent clickjacking
      "base-uri 'self'",
      "form-action 'self'"
    ].join('; ')
  );

  // Additional security headers
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');

  return response;
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    "/((?!_next|[^?]*\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    // Always run for API routes
    "/(api|trpc)(.*)",
  ],
};
