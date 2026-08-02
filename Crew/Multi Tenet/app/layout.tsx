import type { Metadata } from "next";

import "./globals.css";
import { ThemeProvider, themeInitScript } from "@/components/theme";
import { ToastProvider } from "@/components/ui/toast";

export const metadata: Metadata = {
  title: {
    default: "TenantDesk AI — Multi-tenant AI support platform",
    template: "%s · TenantDesk AI",
  },
  description:
    "Every company gets its own AI support crew, isolated knowledge base and workspace. Built on CrewAI, FastAPI and Next.js.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
      </head>
      <body className="min-h-screen bg-background font-sans text-foreground antialiased">
        <ThemeProvider>
          <ToastProvider>{children}</ToastProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
