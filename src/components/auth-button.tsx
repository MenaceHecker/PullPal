'use client'

import { signIn, signOut, useSession } from 'next-auth/react'
import { Button } from '@/components/ui/button'
import { Github } from 'lucide-react'
import { useEffect, useState } from 'react'

interface AuthButtonProps {
  variant?: 'default' | 'hero'
}

export function AuthButton({ variant = 'default' }: AuthButtonProps) {
  const { data: session, status } = useSession()
  const [mounted, setMounted] = useState(false)

  // Prevent hydration mismatch
  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <Button disabled size={variant === 'hero' ? 'lg' : 'default'}>
        Loading...
      </Button>
    )
  }

  if (status === 'loading') {
    return (
      <Button disabled size={variant === 'hero' ? 'lg' : 'default'}>
        Loading...
      </Button>
    )
  }

  if (session) {
    return (
      <div className="flex items-center space-x-4">
        <span className="text-white hidden sm:inline">
          Welcome, {session.user?.name}
        </span>
        <Button
          variant="outline"
          onClick={() => signOut()}
          className="cursor-pointer"
        >
          Sign Out
        </Button>
      </div>
    )
  }

  return (
    <Button
      onClick={() => signIn('github')}
      size={variant === 'hero' ? 'lg' : 'default'}
      className={`${variant === 'hero' ? 'text-lg px-8 py-3' : ''} cursor-pointer`}
    >
      <Github className="mr-2 h-4 w-4" />
      Sign in with GitHub
    </Button>
  )
}
