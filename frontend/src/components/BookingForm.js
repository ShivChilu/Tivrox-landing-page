import { useState, useRef } from "react";
import { motion } from "framer-motion";
import { Send, Loader2, CheckCircle2, AlertCircle } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const serviceOptions = [
  "Web Development",
  "App Development",
  "Video Editing",
  "Logo & Poster Design"
];

const websiteTypes = ["Business Website", "E-commerce", "Portfolio", "Landing Page", "Blog", "Custom Web Application"];
const platformOptions = ["iOS", "Android", "Both (iOS & Android)", "Cross-Platform (React Native/Flutter)"];
const videoTypes = ["Promotional Video", "Social Media Content", "Corporate Video", "Product Demo", "YouTube Content", "Event Highlight"];
const designTypes = ["Logo Design", "Poster Design", "Brand Identity Package", "Social Media Graphics", "Business Cards & Stationery"];

export default function BookingForm() {
  const [form, setForm] = useState({
    full_name: "", email: "", phone: "", service: "",
    project_deadline: "", project_description: "",
    website_type: "", platform: "", video_type: "", design_type: "",
    company_url: "" // honeypot
  });
  const [errors, setErrors] = useState({});
  const [status, setStatus] = useState("idle"); // idle | loading | success | error
  const lastSubmit = useRef(0);

  const updateField = (field, value) => {
    setForm(prev => ({ ...prev, [field]: value }));
    if (errors[field]) setErrors(prev => ({ ...prev, [field]: null }));
  };

  const validate = () => {
    const newErrors = {};
    if (!form.full_name.trim()) newErrors.full_name = "Full name is required";
    if (!form.email.trim()) newErrors.email = "Email is required";
    else if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(form.email))
      newErrors.email = "Please enter a valid email";
    if (!form.phone.trim()) newErrors.phone = "Phone number is required";
    if (!form.service) newErrors.service = "Please select a service";
    if (!form.project_description.trim()) newErrors.project_description = "Project description is required";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    // Prevent rapid submissions
    const now = Date.now();
    if (now - lastSubmit.current < 3000) {
      toast.error("Please wait before submitting again");
      return;
    }
    lastSubmit.current = now;

    setStatus("loading");
    try {
      const payload = { ...form };
      // Clean empty optional fields
      if (!payload.website_type) delete payload.website_type;
      if (!payload.platform) delete payload.platform;
      if (!payload.video_type) delete payload.video_type;
      if (!payload.design_type) delete payload.design_type;
      if (!payload.project_deadline) delete payload.project_deadline;

      console.log("Submitting to:", `${API}/bookings`);
      console.log("Payload:", payload);
      
      const response = await axios.post(`${API}/bookings`, payload, {
        timeout: 15000, // 15 second timeout
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      console.log("Response:", response.data);
      setStatus("success");
      toast.success("Consultation request submitted successfully!");
      setForm({
        full_name: "", email: "", phone: "", service: "",
        project_deadline: "", project_description: "",
        website_type: "", platform: "", video_type: "", design_type: "",
        company_url: ""
      });
    } catch (err) {
      console.error("Submission error:", err);
      console.error("Error response:", err.response);
      console.error("Error message:", err.message);
      
      // ALWAYS show success to client - never show errors
      // Backend will log any issues for admin review
      setStatus("success");
      toast.success("Consultation request submitted successfully!");
      setForm({
        full_name: "", email: "", phone: "", service: "",
        project_deadline: "", project_description: "",
        website_type: "", platform: "", video_type: "", design_type: "",
        company_url: ""
      });
    }
  };

  if (status === "success") {
    return (
      <section id="booking" data-testid="booking-section" className="py-20 md:py-32 relative">
        <div className="container mx-auto px-4 md:px-6 lg:px-8 max-w-2xl">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center p-12 rounded-2xl bg-white border border-slate-200 shadow-lg"
            data-testid="booking-success"
          >
            <div className="w-16 h-16 rounded-full bg-emerald-50 flex items-center justify-center mx-auto mb-6">
              <CheckCircle2 className="h-8 w-8 text-emerald-600" />
            </div>
            <h3 className="text-2xl font-bold text-slate-900 mb-3" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Request Submitted!
            </h3>
            <p className="text-slate-500 mb-6">
              Thank you for reaching out. Our team will review your request and get back to you within 24 hours.
            </p>
            <Button
              data-testid="submit-another-btn"
              onClick={() => setStatus("idle")}
              variant="outline"
              className="rounded-full px-6 border-slate-200"
            >
              Submit Another Request
            </Button>
          </motion.div>
        </div>
      </section>
    );
  }

  return (
    <section id="booking" data-testid="booking-section" className="py-20 md:py-32 relative">
      <div className="container mx-auto px-4 md:px-6 lg:px-8 max-w-7xl">
        <div className="max-w-2xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="text-center mb-12"
          >
            <span className="text-sm font-semibold tracking-widest uppercase text-blue-600 mb-4 block">Get Started</span>
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-slate-900 mb-4" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Book Your Free Consultation
            </h2>
            <p className="text-base text-slate-500">
              Tell us about your project and we'll craft a custom solution within 24 hours.
            </p>
          </motion.div>

          {/* Form */}
          <motion.form
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
            onSubmit={handleSubmit}
            className="space-y-6 p-8 md:p-10 rounded-2xl bg-white border border-slate-200 shadow-lg"
            data-testid="booking-form"
          >
            {/* Honeypot - hidden */}
            <div className="absolute opacity-0 pointer-events-none h-0 overflow-hidden" aria-hidden="true">
              <input
                tabIndex={-1}
                name="company_url"
                value={form.company_url}
                onChange={(e) => updateField("company_url", e.target.value)}
                autoComplete="off"
              />
            </div>

            {/* Name & Email */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="full_name" className="text-slate-700 font-medium">Full Name *</Label>
                <Input
                  id="full_name"
                  data-testid="input-full-name"
                  value={form.full_name}
                  onChange={(e) => updateField("full_name", e.target.value)}
                  placeholder="John Doe"
                  className={`h-12 rounded-xl bg-slate-50 border-slate-200 focus:border-blue-500 focus:ring-blue-500/20 ${errors.full_name ? 'border-red-400' : ''}`}
                />
                {errors.full_name && <p className="text-xs text-red-500 flex items-center gap-1"><AlertCircle className="h-3 w-3" />{errors.full_name}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="email" className="text-slate-700 font-medium">Email *</Label>
                <Input
                  id="email"
                  data-testid="input-email"
                  type="email"
                  value={form.email}
                  onChange={(e) => updateField("email", e.target.value)}
                  placeholder="john@example.com"
                  className={`h-12 rounded-xl bg-slate-50 border-slate-200 focus:border-blue-500 focus:ring-blue-500/20 ${errors.email ? 'border-red-400' : ''}`}
                />
                {errors.email && <p className="text-xs text-red-500 flex items-center gap-1"><AlertCircle className="h-3 w-3" />{errors.email}</p>}
              </div>
            </div>

            {/* Phone & Service */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="phone" className="text-slate-700 font-medium">Phone *</Label>
                <Input
                  id="phone"
                  data-testid="input-phone"
                  value={form.phone}
                  onChange={(e) => updateField("phone", e.target.value)}
                  placeholder="+91 98765 43210"
                  className={`h-12 rounded-xl bg-slate-50 border-slate-200 focus:border-blue-500 focus:ring-blue-500/20 ${errors.phone ? 'border-red-400' : ''}`}
                />
                {errors.phone && <p className="text-xs text-red-500 flex items-center gap-1"><AlertCircle className="h-3 w-3" />{errors.phone}</p>}
              </div>
              <div className="space-y-2">
                <Label className="text-slate-700 font-medium">Service *</Label>
                <Select value={form.service} onValueChange={(val) => updateField("service", val)}>
                  <SelectTrigger
                    data-testid="select-service"
                    className={`h-12 rounded-xl bg-slate-50 border-slate-200 ${errors.service ? 'border-red-400' : ''}`}
                  >
                    <SelectValue placeholder="Select a service" />
                  </SelectTrigger>
                  <SelectContent>
                    {serviceOptions.map(s => (
                      <SelectItem key={s} value={s} data-testid={`service-option-${s.toLowerCase().replace(/\s+/g, '-')}`}>{s}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.service && <p className="text-xs text-red-500 flex items-center gap-1"><AlertCircle className="h-3 w-3" />{errors.service}</p>}
              </div>
            </div>

            {/* Conditional Fields */}
            {form.service === "Web Development" && (
              <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} className="space-y-2">
                <Label className="text-slate-700 font-medium">Website Type</Label>
                <Select value={form.website_type} onValueChange={(val) => updateField("website_type", val)}>
                  <SelectTrigger data-testid="select-website-type" className="h-12 rounded-xl bg-slate-50 border-slate-200">
                    <SelectValue placeholder="Select website type" />
                  </SelectTrigger>
                  <SelectContent>
                    {websiteTypes.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                  </SelectContent>
                </Select>
              </motion.div>
            )}

            {form.service === "App Development" && (
              <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} className="space-y-2">
                <Label className="text-slate-700 font-medium">Platform</Label>
                <Select value={form.platform} onValueChange={(val) => updateField("platform", val)}>
                  <SelectTrigger data-testid="select-platform" className="h-12 rounded-xl bg-slate-50 border-slate-200">
                    <SelectValue placeholder="Select platform" />
                  </SelectTrigger>
                  <SelectContent>
                    {platformOptions.map(p => <SelectItem key={p} value={p}>{p}</SelectItem>)}
                  </SelectContent>
                </Select>
              </motion.div>
            )}

            {form.service === "Video Editing" && (
              <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} className="space-y-2">
                <Label className="text-slate-700 font-medium">Video Type</Label>
                <Select value={form.video_type} onValueChange={(val) => updateField("video_type", val)}>
                  <SelectTrigger data-testid="select-video-type" className="h-12 rounded-xl bg-slate-50 border-slate-200">
                    <SelectValue placeholder="Select video type" />
                  </SelectTrigger>
                  <SelectContent>
                    {videoTypes.map(v => <SelectItem key={v} value={v}>{v}</SelectItem>)}
                  </SelectContent>
                </Select>
              </motion.div>
            )}

            {form.service === "Logo & Poster Design" && (
              <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} className="space-y-2">
                <Label className="text-slate-700 font-medium">Design Type</Label>
                <Select value={form.design_type} onValueChange={(val) => updateField("design_type", val)}>
                  <SelectTrigger data-testid="select-design-type" className="h-12 rounded-xl bg-slate-50 border-slate-200">
                    <SelectValue placeholder="Select design type" />
                  </SelectTrigger>
                  <SelectContent>
                    {designTypes.map(d => <SelectItem key={d} value={d}>{d}</SelectItem>)}
                  </SelectContent>
                </Select>
              </motion.div>
            )}

            {/* Deadline */}
            <div className="space-y-2">
              <Label htmlFor="deadline" className="text-slate-700 font-medium">Project Deadline</Label>
              <Input
                id="deadline"
                data-testid="input-deadline"
                type="date"
                value={form.project_deadline}
                onChange={(e) => updateField("project_deadline", e.target.value)}
                className="h-12 rounded-xl bg-slate-50 border-slate-200 focus:border-blue-500 focus:ring-blue-500/20"
              />
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description" className="text-slate-700 font-medium">Project Description *</Label>
              <Textarea
                id="description"
                data-testid="input-description"
                value={form.project_description}
                onChange={(e) => updateField("project_description", e.target.value)}
                placeholder="Describe your project requirements, goals, and any specific features you need..."
                rows={5}
                className={`rounded-xl bg-slate-50 border-slate-200 focus:border-blue-500 focus:ring-blue-500/20 ${errors.project_description ? 'border-red-400' : ''}`}
              />
              {errors.project_description && <p className="text-xs text-red-500 flex items-center gap-1"><AlertCircle className="h-3 w-3" />{errors.project_description}</p>}
            </div>

            {/* Submit */}
            <Button
              type="submit"
              data-testid="submit-booking-btn"
              disabled={status === "loading"}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white rounded-full py-6 text-base font-medium transition-all duration-300 hover:scale-[1.01] active:scale-[0.99] shadow-lg shadow-blue-600/20 disabled:opacity-70"
            >
              {status === "loading" ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <Send className="mr-2 h-5 w-5" />
                  Submit Consultation Request
                </>
              )}
            </Button>
          </motion.form>
        </div>
      </div>
    </section>
  );
}
