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