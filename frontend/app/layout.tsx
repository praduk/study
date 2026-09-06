import type { Metadata } from 'next';
import './globals.css';

/* oxlint-disable next/no-css-tags -- the shipped offline vendor stylesheet has a stable URL */

export const metadata: Metadata = {
  title: 'Study — mathematical recall',
  description: 'A local-first library for learning and remembering mathematics.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="stylesheet" href="/vendor/excalidraw/index.css" />
      </head>
      <body>{children}</body>
    </html>
  );
}
