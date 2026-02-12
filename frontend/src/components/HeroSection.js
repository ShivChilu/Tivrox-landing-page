import { motion } from "framer-motion";
import { ArrowRight, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";

const services = ["Web Development", "App Development", "Branding", "Video Editing"];

export default function HeroSection() {
  const scrollTo = (id) => {
    const el = document.querySelector(id);
    if (el) el.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section
      data-testid="hero-section"
      className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20"
    >
      {/* Background glow */}
      <div className="hero-glow top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
      <div className="hero-glow top-0 right-0 opacity-50" style={{ width: 400, height: 400 }} />
      <div className="grid-pattern absolute inset-0" />

      <div className="container mx-auto px-4 md:px-6 lg:px-8 max-w-7xl relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          {/* Tag */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-50 border border-blue-100 mb-8"
          >
            <span className="w-2 h-2 rounded-full bg-blue-600 animate-pulse" />
            <span className="text-sm font-medium text-blue-700">Digital Systems That Scale</span>
          </motion.div>

          {/* Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-4xl sm:text-5xl lg:text-7xl font-bold tracking-tight text-slate-900 leading-[1.1] mb-6"
            style={{ fontFamily: 'Manrope, sans-serif' }}
          >
            We Build Scalable
            <br />
            <span className="gradient-text">Digital Systems.</span>
          </motion.h1>

          {/* Services tags */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="flex flex-wrap justify-center gap-3 mb-10"
          >
            {services.map((service, i) => (
              <motion.span
                key={service}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: 0.5 + i * 0.1 }}
                className="px-4 py-2 rounded-full bg-slate-50 border border-slate-200 text-sm font-medium text-slate-600"
              >
                {service}
              </motion.span>
            ))}
          </motion.div>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <Button
              data-testid="hero-cta-booking"
              onClick={() => scrollTo("#booking")}
              className="bg-blue-600 hover:bg-blue-700 text-white rounded-full px-8 py-6 text-base font-medium transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-blue-600/25"
            >
              Book Free Consultation
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
            <Button
              data-testid="hero-cta-services"
              onClick={() => scrollTo("#services")}
              variant="outline"
              className="border-2 border-slate-200 bg-white hover:bg-slate-50 text-slate-800 rounded-full px-8 py-6 text-base font-medium transition-all duration-300"
            >
              Explore Services
            </Button>
          </motion.div>

          {/* Scroll indicator */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.2 }}
            className="mt-20 flex justify-center"
          >
            <button
              data-testid="scroll-down-indicator"
              onClick={() => scrollTo("#services")}
              className="flex flex-col items-center gap-1 text-slate-400 hover:text-blue-600 transition-colors"
            >
              <span className="text-xs font-medium tracking-wider uppercase">Explore</span>
              <ChevronDown className="h-5 w-5 animate-bounce" />
            </button>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
