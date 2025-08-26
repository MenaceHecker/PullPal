'use client';

import { SessionProvider } from 'next-auth/react';
import { Session } from 'next-auth';
import RepoSelector from './repo-selector';

interface RepoSelectorWrapperProps {
  session: Session;
}

export default function RepoSelectorWrapper({ session }: RepoSelectorWrapperProps) {
  return (
    <SessionProvider session={session}>
      <RepoSelector />
    </SessionProvider>
  );
}