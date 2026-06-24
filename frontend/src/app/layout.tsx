import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "WM Prognose Engine",
  description: "KI-gestützte Fußball-WM-Prognosen mit Value Bet Analyse",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de">
      <body>{children}</body>
    </html>
  );
}
