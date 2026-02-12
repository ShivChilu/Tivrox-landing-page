import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import ServicesSection from "@/components/ServicesSection";
import WhyChooseSection from "@/components/WhyChooseSection";
import BookingForm from "@/components/BookingForm";
import Footer from "@/components/Footer";

export default function LandingPage() {
  return (
    <div className="min-h-screen" data-testid="landing-page">
      <Navbar />
      <main>
        <HeroSection />
        <ServicesSection />
        <WhyChooseSection />
        <BookingForm />
      </main>
      <Footer />
    </div>
  );
}
