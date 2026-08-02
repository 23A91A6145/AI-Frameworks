import Link from "next/link";
import { Building2, Users } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-border py-10">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-4 sm:flex-row sm:px-6">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 text-white">
            <Building2 className="h-3.5 w-3.5" />
          </div>
          <span className="text-sm font-semibold">TenantDesk AI</span>
        </div>
        <div className="flex items-center gap-5 text-sm text-muted-foreground">
          <Link href="/features" className="hover:text-foreground">
            Features
          </Link>
          <Link href="/pricing" className="hover:text-foreground">
            Pricing
          </Link>
          <Link href="/docs" className="hover:text-foreground">
            Docs
          </Link>
          <Link href="/contact" className="hover:text-foreground">
            Contact
          </Link>
          <Link href="/login" className="hover:text-foreground">
            Login
          </Link>
          <Link href="/register" className="hover:text-foreground">
            Register
          </Link>
        </div>
        <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Users className="h-3.5 w-3.5" />
          © {new Date().getFullYear()} TenantDesk AI
        </p>
      </div>
    </footer>
  );
}
