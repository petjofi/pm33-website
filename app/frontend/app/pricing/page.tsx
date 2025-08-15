import { Check, ArrowRight } from 'lucide-react'
import Link from 'next/link'
import Navigation from '@/components/Navigation'

export default function PricingPage() {
  const plans = [
    {
      name: "Starter",
      price: "$20",
      period: "per user/month",
      description: "Perfect for small PM teams getting started with AI",
      features: [
        "Connect up to 3 tools (Jira, Slack, Monday)",
        "100 AI-generated documents per month",
        "Basic strategic insights dashboard",
        "Email support",
        "14-day free trial",
        "No setup fees"
      ],
      cta: "Start Free Trial",
      popular: false
    },
    {
      name: "Professional",
      price: "$30",
      period: "per user/month", 
      description: "For growing teams ready to scale AI-powered PM workflows",
      features: [
        "Unlimited tool integrations",
        "Unlimited AI documentation and analysis",
        "Advanced predictive insights and recommendations",
        "Priority support + dedicated onboarding",
        "Custom AI training on your data",
        "Advanced analytics and reporting"
      ],
      cta: "Start Free Trial",
      popular: true
    },
    {
      name: "Enterprise",
      price: "Custom",
      period: "pricing",
      description: "For large organizations with advanced security and customization needs",
      features: [
        "White-label AI assistant",
        "Custom AI training on your historical data",
        "Advanced security and compliance features",
        "Dedicated customer success manager",
        "Custom integrations and API access",
        "SLA guarantees and premium support"
      ],
      cta: "Contact Sales",
      popular: false
    }
  ]

  return (
    <div className="min-h-screen bg-white">
      <Navigation />

      {/* Hero Section */}
      <section className="px-6 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Pricing That Scales with Value, Not Seats
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Usage-based pricing means you pay for results, not team size. All plans include our 10x Time Saved guarantee.
          </p>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="px-6 py-12">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8">
            {plans.map((plan, index) => (
              <div 
                key={index} 
                className={`relative p-8 rounded-xl border-2 ${
                  plan.popular 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200 bg-white'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-semibold">
                      Most Popular
                    </span>
                  </div>
                )}
                
                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  <div className="mb-4">
                    <span className="text-4xl font-bold text-gray-900">{plan.price}</span>
                    <span className="text-gray-600 ml-2">{plan.period}</span>
                  </div>
                  <p className="text-gray-600">{plan.description}</p>
                </div>

                <div className="space-y-4 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <div key={featureIndex} className="flex items-start">
                      <Check className="h-5 w-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
                      <span className="text-gray-700">{feature}</span>
                    </div>
                  ))}
                </div>

                <Link
                  href={plan.name === 'Enterprise' ? '/contact' : '/trial'}
                  className={`block w-full text-center py-3 px-4 rounded-lg font-semibold transition-colors ${
                    plan.popular
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ROI Calculator Section */}
      <section className="px-6 py-20 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Calculate Your ROI
            </h2>
            <p className="text-gray-600">
              See how much time and money PM33 can save your team
            </p>
          </div>

          <div className="bg-white p-8 rounded-lg shadow-lg">
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-xl font-semibold mb-4">Your Current Costs</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Number of PMs on your team
                    </label>
                    <input 
                      type="number" 
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                      placeholder="10"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Average PM salary
                    </label>
                    <input 
                      type="number" 
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                      placeholder="140000"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Hours per week spent on admin work
                    </label>
                    <input 
                      type="number" 
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                      placeholder="25"
                    />
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-4">With PM33</h3>
                <div className="bg-blue-50 p-6 rounded-lg">
                  <div className="text-3xl font-bold text-blue-600 mb-2">$840K</div>
                  <div className="text-sm text-gray-600 mb-4">Annual cost avoidance</div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>PM33 cost (10 users):</span>
                      <span>$3,600/year</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Time savings value:</span>
                      <span>$843,600/year</span>
                    </div>
                    <div className="border-t pt-2 font-semibold flex justify-between">
                      <span>Net ROI:</span>
                      <span className="text-green-600">2,343%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="px-6 py-20">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Frequently Asked Questions
            </h2>
          </div>

          <div className="space-y-8">
            {[
              {
                question: "How is this different from ChatGPT for product management?",
                answer: "PM33 is trained specifically on product management workflows and integrates directly with your tools. While ChatGPT requires you to copy/paste data and lacks context, PM33 continuously analyzes your entire product ecosystem to provide strategic insights you can't get elsewhere."
              },
              {
                question: "What if my team is already using Productboard/Aha?",
                answer: "PM33 enhances these tools rather than replacing them. Many customers use PM33 as their 'AI brain' while keeping Productboard for roadmap visualization or Aha for feature tracking. You get the best of both worlds."
              },
              {
                question: "How long does implementation take?",
                answer: "Most teams are productive within hours. PM33 connects to your existing tools via secure APIs - no data migration, no workflow changes, no training required. Your team keeps using familiar tools but with AI superpowers."
              },
              {
                question: "Is our data secure?",
                answer: "PM33 uses enterprise-grade security (SOC2 Type II, GDPR compliant) and never trains AI models on customer data. Your information stays private and secure while the AI provides insights based on patterns, not data sharing."
              }
            ].map((faq, index) => (
              <div key={index} className="border-b border-gray-200 pb-8">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  {faq.question}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {faq.answer}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-6 py-20 bg-blue-600">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to 10x Your PM Productivity?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            All plans come with our 10x Time Saved guarantee. Cancel anytime.
          </p>
          <Link 
            href="/trial"
            className="bg-white text-blue-600 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-50 transition-colors inline-flex items-center"
          >
            Start Your Free 14-Day Trial
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
          <div className="text-blue-100 text-sm mt-4">
            No credit card required. Full access to all features.
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-6 py-12 bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="text-2xl font-bold text-blue-400 mb-4">PM33</div>
              <p className="text-gray-400">
                The AI brain that supercharges your existing PM tools without migration headaches.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <div className="space-y-2 text-gray-400">
                <Link href="/demo" className="block hover:text-white">Demo</Link>
                <Link href="/pricing" className="block hover:text-white">Pricing</Link>
                <Link href="/integrations" className="block hover:text-white">Integrations</Link>
              </div>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Community</h4>
              <div className="space-y-2 text-gray-400">
                <Link href="/blog" className="block hover:text-white">Blog</Link>
                <Link href="/community" className="block hover:text-white">PM Community</Link>
                <Link href="/resources" className="block hover:text-white">Resources</Link>
              </div>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <div className="space-y-2 text-gray-400">
                <Link href="/about" className="block hover:text-white">About</Link>
                <Link href="/contact" className="block hover:text-white">Contact</Link>
                <Link href="/privacy" className="block hover:text-white">Privacy</Link>
              </div>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 PM33. Don't replace your PM tools - make them 10x smarter.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}