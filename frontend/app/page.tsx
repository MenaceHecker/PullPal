export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-24">
      <h1 className="text-4xl font-bold">Sentra</h1>
      <p className="max-w-xl text-center text-slate-500">
        Connect your system&apos;s logs, metrics, and runbooks. When something
        breaks, Sentra tells you what&apos;s likely wrong, shows its evidence,
        and — with your approval — takes the safe next step.
      </p>
    </main>
  );
}