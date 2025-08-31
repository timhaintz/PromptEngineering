import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import TopNav from "@/components/navigation/TopNav";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Prompt Pattern Dictionary",
  description: "A searchable library of prompt patterns, papers, and examples organized by logic and category.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {/* Global, consistent top-left navigation with Back and Home */}
        <TopNav />
        {/* Offset main content to clear the fixed nav height */}
        <div className="pt-14">
          {children}
        </div>
      </body>
    </html>
  );
}
