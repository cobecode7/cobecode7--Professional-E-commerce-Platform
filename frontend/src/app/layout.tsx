import type { Metadata } from 'next'
import { Providers } from '../providers'
import Navigation from '../components/Navigation'

export const metadata: Metadata = {
  title: 'Professional E-commerce Platform',
  description: 'Modern e-commerce platform built with Next.js and Django',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link 
          href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" 
          rel="stylesheet"
        />
        <script 
          src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"
          async
        />
      </head>
      <body style={{ backgroundColor: '#f8f9fa' }}>
        <Providers>
          <Navigation />
          <main>
            {children}
          </main>
        </Providers>
      </body>
    </html>
  )
}