import CompanyInput from '@/components/CompanyInput'
import OnboardingHero from '@/components/OnboardingHero'
import TopNav from '@/components/TopNav'

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-100 relative">
      {/* Top Navigation */}
      <TopNav />

      {/* Main Content */}
      <div className="flex items-center justify-center min-h-screen">
        <OnboardingHero>
          <CompanyInput />
        </OnboardingHero>
      </div>
    </div>
  )
}
