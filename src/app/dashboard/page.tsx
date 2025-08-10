import { redirect } from 'next/navigation'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { RepoGrid } from '@/components/repo-grid'

export default async function Dashboard() {
  const session = await getServerSession(authOptions)

  if (!session) {
    redirect('/api/auth/signin')
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Your Repositories</h1>
            <p className="text-slate-600 mt-2">Select a repository to start chatting with your code</p>
          </div>
        </div>
        <RepoGrid />
      </div>
    </div>
  )
}