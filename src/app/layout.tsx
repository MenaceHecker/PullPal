import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import {AuthProvider} from '../components/auth-provider'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'PullPal - AI Pair Programmer',
  description: 'Your AI assistant for smart pull requests and code review',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}