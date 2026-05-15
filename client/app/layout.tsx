import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Fantasy League Commissioner",
  description: "Neuro-symbolic governance layer for autonomous fantasy football agents"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
