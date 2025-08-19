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
export default function RepoSelector() {
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
}