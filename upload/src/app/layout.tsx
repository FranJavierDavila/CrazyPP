import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Ping Pong XR — Tenis de mesa inmersivo para Meta Quest 3",
  description:
    "Videojuego de ping pong en WebXR: juega de forma totalmente inmersiva con los mandos de las Meta Quest 3. Física realista, IA rival y vibración háptica.",
  keywords: ["WebXR", "Quest 3", "ping pong", "tenis de mesa", "VR", "Three.js", "videojuego"],
  authors: [{ name: "Z.ai" }],
  icons: {
    icon: "https://z-cdn.chatglm.cn/z-ai/static/logo.svg",
  },
  openGraph: {
    title: "Ping Pong XR — WebXR para Meta Quest 3",
    description: "Ping pong totalmente inmersivo con tracking 1:1 de mandos en WebXR",
    siteName: "Ping Pong XR",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground`}
      >
        {children}
        <Toaster />
      </body>
    </html>
  );
}
