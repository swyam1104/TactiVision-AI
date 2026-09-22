// Centralized API configuration for production and local development.
// In the browser, we use relative URL '' so requests hit the Next.js /api/v1 rewrite proxy.
// This routes traffic through Vercel's edge network to Railway, completely eliminating:
// 1. Client-side ISP/Wi-Fi DNS blocks on *.up.railway.app
// 2. Browser CORS preflight failures
// 3. Mixed Content warnings
export const API_BASE_URL = typeof window !== 'undefined'
  ? ''
  : (process.env.NEXT_PUBLIC_API_URL || 'https://tactivision-backend-production.up.railway.app').replace(/\/$/, '');
