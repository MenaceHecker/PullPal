'use client'

import { signIn, getProviders } from 'next-auth/react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Github } from 'lucide-react'
import { useEffect, useState } from 'react'

export default function SignIn() {
  const [providers, setProviders] = useState<any>(null)

  useEffect(() => {
    const setAuthProviders = async () => {
      const res = await getProviders()
      setProviders(res)
    }
    setAuthProviders()
  }, [])

  if (!providers) {
    return <div>Loading...</div>
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">Welcome to PullPal</CardTitle>
          <CardDescription>
            Sign in with your GitHub account to get started
          </CardDescription>
        </CardHeader>
        <CardContent>
          {Object.values(providers).map((provider: any) => (
            <div key={provider.name}>
              <Button
                onClick={() => signIn(provider.id, { callbackUrl: '/dashboard' })}
                className="w-full"
                size="lg"
              >
                <Github className="mr-2 h-5 w-5" />
                Sign in with {provider.name}
              </Button>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
