import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import TopNav from "@/components/navigation/TopNav";
import { ThemeProvider } from "@/components/ThemeProvider";

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
  // We render a placeholder data-theme that will be immediately updated by the inline script.
  // suppressHydrationWarning avoids React flagging the server/client mismatch once script sets the final value.
  return (
    <html lang="en" data-theme="light" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <script
          dangerouslySetInnerHTML={{
            __html: `(() => {try {const K='pe-theme';const stored=localStorage.getItem(K)||'system';const prefersDark=window.matchMedia('(prefers-color-scheme: dark)').matches;const eff=stored==='system'?(prefersDark?'dark':'light'):stored;document.documentElement.setAttribute('data-theme', eff);document.documentElement.setAttribute('data-theme-mode', stored);}catch(e){}})();`
          }} />
        <ThemeProvider>
          <TopNav />
          <div className="pt-14">
            {children}
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
