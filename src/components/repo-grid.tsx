'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { GitBranch, Star, Eye } from 'lucide-react'
import Link from 'next/link'

interface Repository {
  id: string
  name: string
  fullName: string
  description?: string
  language?: string
  stargazersCount: number
  watchersCount: number
  private: boolean
  indexed: boolean
}

export function RepoGrid() {
  const [repos, setRepos] = useState<Repository[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchRepos()
  }, [])

  const fetchRepos = async () => {
    try {
      const response = await fetch('/api/repos')
      const data = await response.json()
      setRepos(data)
    } catch (error) {
      console.error('Failed to fetch repos:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleIndex = async (repoId: string) => {
    try {
      await fetch(`/api/repos/${repoId}/index`, { method: 'POST' })
      // Refresh repos to update indexed status
      fetchRepos()
    } catch (error) {
      console.error('Failed to index repo:', error)
    }
  }

  if (loading) {
    return <div className="text-center">Loading repositories...</div>
  }

  return (
    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
      {repos.map((repo) => (
        <Card key={repo.id} className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-lg font-semibold">{repo.name}</CardTitle>
                <p className="text-sm text-slate-600 mt-1">{repo.fullName}</p>
              </div>
              {repo.private && <Badge variant="secondary">Private</Badge>}
            </div>
            {repo.description && (
              <p className="text-sm text-slate-700 mt-2">{repo.description}</p>
            )}
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-4 text-sm text-slate-600">
                {repo.language && (
                  <span className="flex items-center">
                    <div className="w-3 h-3 rounded-full bg-blue-500 mr-1"></div>
                    {repo.language}
                  </span>
                )}
                <span className="flex items-center">
                  <Star className="w-4 h-4 mr-1" />
                  {repo.stargazersCount}
                </span>
                <span className="flex items-center">
                  <Eye className="w-4 h-4 mr-1" />
                  {repo.watchersCount}
                </span>
              </div>
            </div>
            
            <div className="flex space-x-2">
              {repo.indexed ? (
                <Button asChild className="flex-1">
                  <Link href={`/chat/${repo.id}`}>
                    <GitBranch className="w-4 h-4 mr-2" />
                    Chat
                  </Link>
                </Button>
              ) : (
                <Button
                  onClick={() => handleIndex(repo.id)}
                  variant="outline"
                  className="flex-1"
                >
                  Index Repository
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
