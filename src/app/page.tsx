import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { AuthButton } from '@/components/auth-button'
import { Code, GitPullRequest, MessageSquare, Zap } from 'lucide-react'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <nav className="flex justify-between items-center mb-16">
          <div className="flex items-center space-x-2">
            <Code className="h-8 w-8 text-purple-400" />
            <span className="text-2xl font-bold text-white">PullPal</span>
          </div>
          <AuthButton />
        </nav>

        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Your AI Pair Programmer
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Understand your codebase, get smart refactor suggestions, and ship clean PRs faster than ever.
          </p>
          <AuthButton variant="hero" />
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          <FeatureCard
            icon={<MessageSquare className="h-8 w-8 text-blue-400" />}
            title="Context-Aware Chat"
            description="Ask questions about your code and get intelligent answers based on your entire codebase."
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
            description="Support for JavaScript, TypeScript, Python, Java, and more languages."
          />
        </div>
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