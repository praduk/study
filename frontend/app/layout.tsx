import type { Metadata } from 'next';
import './globals.css';

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
      <body>{children}</body>
    </html>
  );
}
