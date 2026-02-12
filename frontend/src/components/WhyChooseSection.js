import { motion } from "framer-motion";
import { Target, Zap, MessageCircle, Heart, Layers } from "lucide-react";

const reasons = [
  {
    icon: Target,
    title: "Strategic Planning",
    description: "Every project begins with a detailed strategy. We align digital solutions with your business objectives for measurable impact."
  },
  {
    icon: Zap,
    title: "Fast Execution",
    description: "Agile workflows and dedicated teams ensure your project is delivered on time without compromising on quality."
  },
  {
    icon: MessageCircle,
    title: "Transparent Communication",
    description: "Regular updates, clear timelines, and open feedback loops. You always know where your project stands."
  },
  {
    icon: Heart,
    title: "Customer Satisfaction First",
    description: "We measure success by your satisfaction. Unlimited revisions and post-launch support come standard."
  },
  {
    icon: Layers,
    title: "Scalable Architecture",
    description: "Built to grow with your business. Our solutions use modern tech stacks designed for performance at scale."
  }
];

export default function WhyChooseSection() {
  return (
    <section id="why-choose" data-testid="why-choose-section" className="py-20 md:py-32 bg-slate-50 relative">
      <div className="container mx-auto px-4 md:px-6 lg:px-8 max-w-7xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-50px" }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <span className="text-sm font-semibold tracking-widest uppercase text-blue-600 mb-4 block">Why TIVROX</span>
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-slate-900 mb-4" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Why Leading Businesses Choose Us
          </h2>
          <p className="text-base md:text-lg text-slate-500 max-w-2xl mx-auto">
            We don't just build products — we engineer digital experiences that drive growth, retention, and revenue.
          </p>
        </motion.div>

        {/* Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {reasons.map((reason, idx) => (
            <motion.div
              key={reason.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.4, delay: idx * 0.08 }}
              data-testid={`reason-card-${idx}`}
              className={`group relative p-8 rounded-2xl bg-white border border-slate-200 transition-all duration-400 hover:border-blue-200 hover:shadow-lg hover:shadow-blue-600/5 ${
                idx === 0 ? "md:col-span-2 lg:col-span-2" : ""
              }`}
            >
              <div className="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center mb-6 group-hover:bg-blue-100 transition-colors duration-300">
                <reason.icon className="h-6 w-6 text-blue-600" />
              </div>
              <h3
                className="text-lg font-bold text-slate-900 mb-3"
                style={{ fontFamily: 'Manrope, sans-serif' }}
              >
                {reason.title}
              </h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                {reason.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
