import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Study — mathematical recall',
  description: 'A local-first library for learning and remembering mathematics.',
  metadataBase: new URL('http://127.0.0.1:8765'),
  openGraph: {
    title: 'Study',
    description: 'Learn deeply. Recall deliberately.',
    images: [{ url: '/og.png', width: 1731, height: 909, alt: 'Study — Learn deeply. Recall deliberately.' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Study',
    description: 'Learn deeply. Recall deliberately.',
    images: ['/og.png'],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
