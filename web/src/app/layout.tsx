import type { Metadata } from "next";
import { Fraunces, IBM_Plex_Sans, IBM_Plex_Mono } from "next/font/google";
import Link from "next/link";
import { Ticker } from "@/components/ticker";
import "./globals.css";

const fraunces = Fraunces({
  variable: "--font-fraunces",
  subsets: ["latin"],
  style: ["normal", "italic"],
  axes: ["opsz", "SOFT", "WONK"],
});

const plexSans = IBM_Plex_Sans({
  variable: "--font-plex-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

const plexMono = IBM_Plex_Mono({
  variable: "--font-plex-mono",
  subsets: ["latin"],
  weight: ["400", "500"],
});

export const metadata: Metadata = {
  title: "Apen Inteligência",
  description: "Plataforma interna do time de inteligência da Apen Capital",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="pt-BR"
      className={`${fraunces.variable} ${plexSans.variable} ${plexMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-background text-foreground">
        <header className="border-b border-border">
          <div className="mx-auto flex max-w-6xl items-center gap-8 px-6 py-5">
            <span className="font-display text-lg tracking-tight text-foreground">
              Apen <em className="not-italic text-primary">Inteligência</em>
            </span>
            <nav className="flex gap-6 font-mono text-xs uppercase tracking-widest">
              <Link
                href="/relatorios"
                className="text-muted-foreground transition-colors hover:text-primary"
              >
                Relatórios
              </Link>
              <Link
                href="/chat"
                className="text-muted-foreground transition-colors hover:text-primary"
              >
                Chat
              </Link>
            </nav>
          </div>
        </header>
        <Ticker />
        <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-10">
          {children}
        </main>
        <footer className="border-t border-border py-4">
          <p className="mx-auto max-w-6xl px-6 font-mono text-[11px] tracking-wide text-muted-foreground">
            Apen Capital · time de inteligência · uso interno
          </p>
        </footer>
      </body>
    </html>
  );
}
