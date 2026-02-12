import { useState } from "react";
import { motion } from "framer-motion";
import { Globe, Smartphone, Video, Palette, ArrowRight, CheckCircle2, Clock, Package } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const servicesData = [
  {
    icon: Globe,
    title: "Web Development",
    subtitle: "Custom websites that convert",
    description: "We build high-performance, responsive websites tailored to your business needs. From landing pages to complex web applications, our solutions are built to scale.",
    benefits: ["Custom UI/UX Design", "SEO Optimized Architecture", "Mobile-First Responsive", "Lightning Fast Performance", "CMS Integration"],
    deliverables: ["Fully responsive website", "Admin dashboard", "SEO optimization", "Analytics integration", "6-month support"],
    timeline: "4-8 weeks",
    image: "https://images.unsplash.com/photo-1554306274-f23873d9a26c?w=600&q=80"
  },
  {
    icon: Smartphone,
    title: "App Development",
    subtitle: "Native & cross-platform apps",
    description: "Transform your ideas into powerful mobile applications. We develop for both iOS and Android, ensuring a seamless user experience across all devices.",
    benefits: ["Cross-Platform Development", "Intuitive User Interfaces", "Offline Capabilities", "Push Notifications", "App Store Optimization"],
    deliverables: ["iOS & Android apps", "Backend API", "Admin panel", "App store submission", "3-month support"],
    timeline: "8-16 weeks",
    image: "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=600&q=80"
  },
  {
    icon: Video,
    title: "Video Editing",
    subtitle: "Cinematic content creation",
    description: "Professional video editing services that tell your brand story. From promotional videos to social media content, we craft visuals that engage and inspire.",
    benefits: ["Professional Color Grading", "Motion Graphics", "Sound Design", "Multi-Format Output", "Quick Turnaround"],
    deliverables: ["Edited video files", "Multiple format exports", "Thumbnail designs", "Revision rounds", "Source files"],
    timeline: "1-3 weeks",
    image: "https://images.unsplash.com/photo-1574717024653-61fd2cf4d44d?w=600&q=80"
  },
  {
    icon: Palette,
    title: "Logo & Poster Design",
    subtitle: "Visual identity that stands out",
    description: "Create a powerful brand identity with our design expertise. We craft logos, posters, and brand guidelines that leave a lasting impression on your audience.",
    benefits: ["Unique Concepts", "Brand Consistency", "Print & Digital Ready", "Unlimited Revisions", "Full Brand Guidelines"],
    deliverables: ["Logo files (all formats)", "Brand style guide", "Business card design", "Social media kit", "Letterhead design"],
    timeline: "2-4 weeks",
    image: "https://images.unsplash.com/photo-1626785774573-4b799315345d?w=600&q=80"
  }
];

const fadeInUp = {
  initial: { opacity: 0, y: 40 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-50px" },
  transition: { duration: 0.5 }
};

export default function ServicesSection() {
  const [selectedService, setSelectedService] = useState(null);

  return (
    <section id="services" data-testid="services-section" className="py-20 md:py-32 relative">
      <div className="container mx-auto px-4 md:px-6 lg:px-8 max-w-7xl">
        {/* Header */}
        <motion.div {...fadeInUp} className="text-center mb-16">
          <span className="text-sm font-semibold tracking-widest uppercase text-blue-600 mb-4 block">What We Do</span>
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-slate-900 mb-4" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Services Built for Growth
          </h2>
          <p className="text-base md:text-lg text-slate-500 max-w-2xl mx-auto">
            End-to-end digital solutions that transform your business. Every project is crafted with precision and purpose.
          </p>
        </motion.div>

        {/* Service Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {servicesData.map((service, idx) => (
            <motion.div
              key={service.title}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.5, delay: idx * 0.1 }}
            >
              <button
                data-testid={`service-card-${service.title.toLowerCase().replace(/\s+/g, '-')}`}
                onClick={() => setSelectedService(service)}
                className="group w-full text-left relative overflow-hidden rounded-2xl bg-white border border-slate-200 p-8 transition-all duration-500 hover:border-blue-200 hover:shadow-xl hover:shadow-blue-600/5"
              >
                <div className="service-card-glow" />
                <div className="relative z-10">
                  <div className="flex items-start justify-between mb-6">
                    <div className="w-14 h-14 rounded-2xl bg-blue-50 flex items-center justify-center group-hover:bg-blue-100 transition-colors duration-300">
                      <service.icon className="h-7 w-7 text-blue-600" />
                    </div>
                    <ArrowRight className="h-5 w-5 text-slate-300 group-hover:text-blue-600 group-hover:translate-x-1 transition-all duration-300" />
                  </div>
                  <h3 className="text-xl font-bold text-slate-900 mb-2" style={{ fontFamily: 'Manrope, sans-serif' }}>
                    {service.title}
                  </h3>
                  <p className="text-sm text-slate-500 mb-4">{service.subtitle}</p>
                  <div className="flex items-center gap-2 text-xs text-slate-400">
                    <Clock className="h-3.5 w-3.5" />
                    <span>{service.timeline}</span>
                  </div>
                </div>
              </button>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Service Detail Modal */}
      <Dialog open={!!selectedService} onOpenChange={() => setSelectedService(null)}>
        <DialogContent
          className="sm:max-w-2xl max-h-[85vh] overflow-y-auto bg-white border-slate-200"
          data-testid="service-modal"
        >
          {selectedService && (
            <>
              <DialogHeader>
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center">
                    <selectedService.icon className="h-5 w-5 text-blue-600" />
                  </div>
                  <Badge className="bg-blue-50 text-blue-700 border-blue-100 hover:bg-blue-100">
                    {selectedService.timeline}
                  </Badge>
                </div>
                <DialogTitle className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
                  {selectedService.title}
                </DialogTitle>
                <DialogDescription className="text-slate-500 text-base leading-relaxed">
                  {selectedService.description}
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-6 mt-4">
                {/* Benefits */}
                <div>
                  <h4 className="text-sm font-semibold tracking-wider uppercase text-slate-400 mb-3 flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-blue-600" />
                    Benefits
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {selectedService.benefits.map((b) => (
                      <div key={b} className="flex items-center gap-2 text-sm text-slate-700 py-1.5">
                        <div className="w-1.5 h-1.5 rounded-full bg-blue-600 flex-shrink-0" />
                        {b}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Deliverables */}
                <div>
                  <h4 className="text-sm font-semibold tracking-wider uppercase text-slate-400 mb-3 flex items-center gap-2">
                    <Package className="h-4 w-4 text-blue-600" />
                    Deliverables
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {selectedService.deliverables.map((d) => (
                      <div key={d} className="flex items-center gap-2 text-sm text-slate-700 py-1.5">
                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 flex-shrink-0" />
                        {d}
                      </div>
                    ))}
                  </div>
                </div>

                {/* CTA */}
                <Button
                  data-testid="service-modal-cta"
                  onClick={() => {
                    setSelectedService(null);
                    setTimeout(() => {
                      const el = document.querySelector("#booking");
                      if (el) el.scrollIntoView({ behavior: "smooth" });
                    }, 300);
                  }}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white rounded-full py-6 text-base font-medium transition-all duration-300 hover:scale-[1.01] active:scale-[0.99] shadow-lg shadow-blue-600/20"
                >
                  Get Started with {selectedService.title}
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </section>
  );
}
