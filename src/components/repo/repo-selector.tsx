'use client';

import React, { useState, useEffect } from 'react';
import { Search, GitFork, Star, Calendar, Code } from 'lucide-react';

interface Repository {
  id: number;
  name: string;
  full_name: string;
  description?: string;
  language?: string;
  stargazers_count: number;
  forks_count: number;
  updated_at: string;
  private: boolean;
}
const RepoSelector = () => {
  const [repos, setRepos] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRepo, setSelectedRepo] = useState<Repository | null>(null);
    useEffect(() => {
    // Simulate API call to fetch repositories
    setTimeout(() => {
      setRepos([
        {
          id: 1,
          name: "awesome-project",
          full_name: "johndoe/awesome-project",
          description: "A full-stack web application built with React and Node.js",
          language: "JavaScript",
          stargazers_count: 42,
          forks_count: 8,
          updated_at: "2024-08-15T10:30:00Z",
          private: false
        },
        {
          id: 2,
          name: "ml-pipeline",
          full_name: "johndoe/ml-pipeline",
          description: "Machine learning data processing pipeline",
          language: "Python",
          stargazers_count: 128,
          forks_count: 23,
          updated_at: "2024-08-10T14:20:00Z",
          private: true
        },
        {
          id: 3,
          name: "mobile-app",
          full_name: "johndoe/mobile-app",
          description: "Cross-platform mobile application using React Native",
          language: "TypeScript",
          stargazers_count: 67,
          forks_count: 12,
          updated_at: "2024-08-12T09:45:00Z",
          private: false
        }
      ]);
      setLoading(false);
    }, 1000);
  }, []);
   const filteredRepos = repos.filter(repo =>
    repo.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    repo.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );
    const handleRepoSelect = (repo: Repository) => {
    setSelectedRepo(repo);
    // TODO: Make API call to index the repository
    console.log(`Selected repository: ${repo.full_name}`);
  };
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };
   const getLanguageColor = (language: string) => {
    const colors: { [key: string]: string } = {
      JavaScript: 'bg-yellow-400',
      TypeScript: 'bg-blue-500',
      Python: 'bg-green-500',
      Java: 'bg-orange-500',
      'C++': 'bg-purple-500',
      Go: 'bg-cyan-500'
    };
    return colors[language] || 'bg-gray-400';
  };
   if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400 mx-auto mb-4"></div>
          <p className="text-purple-300">Loading your repositories...</p>
        </div>
      </div>
    );
  }
   return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Choose Your Repository
          </h1>
          <p className="text-purple-300 text-lg">
            Select a repository to start your AI-powered code analysis
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative mb-8 max-w-md mx-auto">
          <Search className="absolute left-3 top-3 h-5 w-5 text-purple-400" />
          <input
            type="text"
            placeholder="Search repositories..."
            className="w-full pl-10 pr-4 py-3 bg-slate-800 border border-purple-600 rounded-lg text-white placeholder-purple-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* Repository Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredRepos.map((repo) => (
            <div
              key={repo.id}
              className={`bg-slate-800 border border-slate-700 rounded-lg p-6 hover:border-purple-500 transition-all duration-300 cursor-pointer transform hover:scale-105 hover:shadow-xl hover:shadow-purple-500/20 ${
                selectedRepo?.id === repo.id ? 'border-purple-500 shadow-lg shadow-purple-500/30' : ''
              }`}
              onClick={() => handleRepoSelect(repo)}
            >
              {/* Repo Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1 min-w-0">
                  <h3 className="text-xl font-semibold text-white truncate">
                    {repo.name}
                  </h3>
                  <p className="text-purple-300 text-sm opacity-80">
                    {repo.full_name}
                  </p>
                </div>
                {repo.private && (
                  <span className="bg-orange-500 text-white text-xs px-2 py-1 rounded-full ml-2">
                    Private
                  </span>
                )}
              </div>

              {/* Description */}
              <p className="text-slate-300 text-sm mb-4 line-clamp-2">
                {repo.description || "No description available"}
              </p>

              {/* Language and Stats */}
              <div className="flex items-center justify-between mb-4">
                {repo.language && (
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full ${getLanguageColor(repo.language)} mr-2`}></div>
                    <span className="text-slate-300 text-sm">{repo.language}</span>
                  </div>
                )}
                <div className="flex items-center space-x-4 text-slate-400 text-sm">
                  <div className="flex items-center">
                    <Star className="h-4 w-4 mr-1" />
                    {repo.stargazers_count}
                  </div>
                  <div className="flex items-center">
                    <GitFork className="h-4 w-4 mr-1" />
                    {repo.forks_count}
                  </div>
                </div>
              </div>

              {/* Last Updated */}
              <div className="flex items-center text-slate-400 text-sm">
                <Calendar className="h-4 w-4 mr-1" />
                Updated {formatDate(repo.updated_at)}
              </div>

              {/* Select Button */}
              {selectedRepo?.id === repo.id ? (
                <button className="w-full mt-4 bg-purple-600 text-white py-2 px-4 rounded-lg font-medium">
                  Selected ✓
                </button>
              ) : (
                <button
                  className="w-full mt-4 bg-slate-700 hover:bg-purple-600 text-white py-2 px-4 rounded-lg font-medium transition-colors duration-200"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRepoSelect(repo);
                  }}
                >
                  <Code className="inline h-4 w-4 mr-2" />
                  Analyze Repository
                </button>
              )}
            </div>
          ))}
        </div>

        {/* No Results */}
        {filteredRepos.length === 0 && (
          <div className="text-center py-12">
            <Code className="h-16 w-16 text-purple-400 mx-auto mb-4 opacity-50" />
            <h3 className="text-xl font-semibold text-white mb-2">No repositories found</h3>
            <p className="text-purple-300">Try adjusting your search terms</p>
          </div>
        )}

        {/* Continue Button */}
        {selectedRepo && (
          <div className="fixed bottom-6 right-6">
            <button className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-3 rounded-lg font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200">
              Continue with {selectedRepo.name} →
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default RepoSelector;