import { withAuth } from 'next-auth/middleware'

export default withAuth(
  function middleware(req) {
    //any middleware logic
  },
  {
    callbacks: {
      authorized: ({ token }) => !!token
    },
  }
)

//have to protect these routes
export const config = {
  matcher: ['/dashboard/:path*', '/chat/:path*']
}