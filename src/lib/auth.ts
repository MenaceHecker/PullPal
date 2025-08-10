// Fix 1: Update lib/auth.ts with proper configuration
import { NextAuthOptions } from 'next-auth'
import GitHubProvider from 'next-auth/providers/github'

export const authOptions: NextAuthOptions = {
  providers: [
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
      authorization: {
        params: {
          scope: 'read:user user:email repo'
        }
      }
    }),
  ],
  callbacks: {
    async jwt({ token, account }) {
      if (account) {
        token.accessToken = account.access_token
      }
      return token
    },
    async session({ session, token }) {
      // Ensure we have a properly typed session
      return {
        ...session,
        accessToken: token.accessToken as string
      }
    },
  },
  pages: {
    signIn: '/auth/signin',
    error: '/auth/error',
  },
  // Add these important configurations
  secret: process.env.NEXTAUTH_SECRET,
  session: {
    strategy: 'jwt',
  },
  debug: process.env.NODE_ENV === 'development',
}
