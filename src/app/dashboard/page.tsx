import { redirect } from 'next/navigation'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import RepoSelector from '@/components/repo/repo-selector'

export default async function Dashboard() {
  const session = await getServerSession(authOptions)

  if (!session) {
    redirect('/api/auth/signin')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Optional: Add a header with user info */}
      <div className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-bold text-white">PullPal</h1>
              <span className="text-purple-300">Dashboard</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-slate-300">
                Welcome, {session.user?.name || session.user?.email}
              </span>
              <img 
                src={session.user?.image || '/default-avatar.png'} 
                alt="Profile" 
                className="w-8 h-8 rounded-full"
              />
            </div>
          </div>
        </div>
      </div>
      
      {/* Main Content - Repository Selector */}
      <RepoSelector />
    </div>
  )
}