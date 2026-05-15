import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Tangram — Visual System Designer",
  description:
    "Open source visual editor for system architecture, with an AI copilot that teaches as you build.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-page text-ink-body antialiased">
        {children}
      </body>
    </html>
  );
}
