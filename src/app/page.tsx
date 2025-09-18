import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { AuthButton } from '@/components/auth-button'
import { Code, GitPullRequest, MessageSquare, Zap } from 'lucide-react'
import Link from 'next/link'

export default async function Home() {
  const session = await getServerSession(authOptions)

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <nav className="flex justify-between items-center mb-16">
          <div className="flex items-center space-x-3">
            <img
              src="/logo.png"
              alt="PullPal Logo"
              className="h-20 w-auto object-contain"
            />
            <span className="text-2xl font-bold text-white">PullPal</span>
          </div>

          <div className="flex items-center space-x-4">
            {session ? (
              <>
                <div className="text-right mr-4 hidden sm:block">
                  <p className="text-sm text-gray-300">Welcome back,</p>
                  <p className="text-white font-medium">
                    {session.user?.name || session.user?.email}
                  </p>
                </div>
                {session.user?.image && (
                  <img 
                    src={session.user.image} 
                    alt="Profile" 
                    className="w-10 h-10 rounded-full border-2 border-purple-500"
                  />
                )}
                <div className="flex items-center space-x-3">
                  <Link
                    href="/dashboard"
                    className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-2 rounded-lg font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-200"
                  >
                    Dashboard
                  </Link>
                  <Link
                    href="/api/auth/signout"
                    className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200"
                  >
                    Sign Out
                  </Link>
                </div>
              </>
            ) : (
              <AuthButton />
            )}
          </div>
        </nav>

        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Your AI Pair Programmer
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Understand every codebase, then get smart refactor suggestions, and then ship clean PRs faster than ever.
          </p>
          
          {/* Call to Action based on auth status */}
          {session ? (
            <div className="space-y-4">
              <p className="text-lg text-green-400 mb-4">
                🎉 You're all set! Ready to analyze your repositories?
              </p>
              <Link
                href="/dashboard"
                className="inline-block bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-4 rounded-lg font-bold text-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
              >
                Start Analyzing Code →
              </Link>
            </div>
          ) : (
            <div className="flex justify-center">
              <AuthButton />
            </div>
          )}
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16 feature-grid">
          <FeatureCard
            icon={<MessageSquare className="h-8 w-8 text-blue-400" />}
            title="Context-Aware Chat"
            description="Ask questions about your code and get smart answers based on your entire codebase."
          />
          <FeatureCard
            icon={<Code className="h-8 w-8 text-green-400" />}
            title="Smart Refactoring"
            description="Get AI-powered suggestions to improve code quality with detailed explanations."
          />
          <FeatureCard
            icon={<GitPullRequest className="h-8 w-8 text-purple-400" />}
            title="Auto PR Creation"
            description="Generate and submit pull requests automatically with AI-optimized changes."
          />
          <FeatureCard
            icon={<Zap className="h-8 w-8 text-yellow-400" />}
            title="Multi-Language"
            description="Support for JavaScript, TypeScript, Kotlin, Python, Java, and more languages."
          />
        </div>

        {/* Additional CTA Section for logged-in users */}
        {session && (
          <div className="text-center bg-slate-800/50 rounded-lg p-8 border border-slate-700">
            <h2 className="text-2xl font-bold text-white mb-4">
              Ready to Get Started?
            </h2>
            <p className="text-gray-300 mb-6">
              Connect your GitHub repositories and start getting AI-powered insights into your code.
            </p>
            <Link
              href="/dashboard"
              className="inline-block bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-3 rounded-lg font-semibold hover:shadow-xl transform hover:scale-105 transition-all duration-200"
            >
              Go to Dashboard →
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}

function FeatureCard({ icon, title, description }: {
  icon: React.ReactNode
  title: string
  description: string
}) {
  return (
    <Card className="bg-slate-800/50 border-slate-700 hover:bg-slate-800/70 transition-colors">
      <CardHeader>
        <div className="mb-2">{icon}</div>
        <CardTitle className="text-white">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <CardDescription className="text-gray-400">
          {description}
        </CardDescription>
      </CardContent>
    </Card>
  )
}