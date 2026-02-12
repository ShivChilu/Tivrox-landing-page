import { Mail, Phone, MapPin } from "lucide-react";

const LOGO_URL = "https://customer-assets.emergentagent.com/job_tivrox-agency-1/artifacts/2hmmk4xa_logo%20final.png";

export default function Footer() {
  const scrollTo = (href) => {
    const el = document.querySelector(href);
    if (el) el.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <footer data-testid="footer" className="bg-slate-900 text-white">
      <div className="container mx-auto px-4 md:px-6 lg:px-8 max-w-7xl py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12">
          {/* Brand */}
          <div className="lg:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <img src={LOGO_URL} alt="TIVROX" className="h-8 w-auto" />
              <span className="text-xl font-bold tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
                TIVROX
              </span>
            </div>
            <p className="text-slate-400 text-sm leading-relaxed max-w-sm mb-6">
              We build scalable digital systems for modern businesses. From web development to branding — we engineer solutions that drive growth.
            </p>
            <div className="flex flex-col gap-3">
              <a href="mailto:chiluverushivaprasad02@gmail.com" className="flex items-center gap-2 text-sm text-slate-400 hover:text-blue-400 transition-colors" data-testid="footer-email">
                <Mail className="h-4 w-4" />
                chiluverushivaprasad02@gmail.com
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-sm font-semibold tracking-wider uppercase text-slate-300 mb-4" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Quick Links
            </h4>
            <ul className="space-y-3">
              {[
                { label: "Services", href: "#services" },
                { label: "About Us", href: "#why-choose" },
                { label: "Contact", href: "#booking" },
              ].map(link => (
                <li key={link.label}>
                  <button
                    onClick={() => scrollTo(link.href)}
                    className="text-sm text-slate-400 hover:text-white transition-colors"
                    data-testid={`footer-link-${link.label.toLowerCase().replace(/\s/g, '-')}`}
                  >
                    {link.label}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          {/* Services */}
          <div>
            <h4 className="text-sm font-semibold tracking-wider uppercase text-slate-300 mb-4" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Services
            </h4>
            <ul className="space-y-3">
              {["Web Development", "App Development", "Video Editing", "Logo & Poster Design"].map(s => (
                <li key={s} className="text-sm text-slate-400">{s}</li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-12 pt-8 border-t border-slate-800 flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="text-xs text-slate-500">
            &copy; {new Date().getFullYear()} TIVROX. All rights reserved.
          </p>
          <p className="text-xs text-slate-500">
            Built with precision. Delivered with purpose.
          </p>
        </div>
      </div>
    </footer>
  );
}
