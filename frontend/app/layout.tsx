import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'TactiVision AI — Professional Soccer Tactical Intelligence',
  description: 'AI-powered tactical analysis, explainable xG prediction, and player similarity embeddings.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  )
}
