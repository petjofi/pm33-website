import { ArrowRight, CheckCircle, Zap, Brain, Clock, TrendingUp, Sparkles, Target, Users, Lightbulb } from 'lucide-react'
import Link from 'next/link'
import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />

      {/* Hero Section */}
      <section className="relative px-6 py-24 overflow-hidden bg-gradient-to-br from-indigo-50 via-white to-purple-50">
        {/* Background Elements */}
        <div className="absolute inset-0">
          <div className="absolute top-0 -left-40 w-80 h-80 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
          <div className="absolute top-0 -right-40 w-80 h-80 bg-gradient-to-r from-cyan-400 to-blue-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
          <div className="absolute -bottom-8 left-20 w-80 h-80 bg-gradient-to-r from-indigo-400 to-purple-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
        </div>
        
        <div className="max-w-7xl mx-auto relative">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Column - Main Content */}
            <div className="text-left">
              <div className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-indigo-100 to-purple-100 text-indigo-700 text-sm font-semibold rounded-full mb-6">
                <Sparkles className="w-4 h-4 mr-2" />
                Join 2,500+ Product Managers
              </div>
              
              <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-8 leading-tight">
                Don't Replace Your PM Tools—
                <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-cyan-600 bg-clip-text text-transparent block mt-2">
                  Make Them 10x Smarter
                </span>
              </h1>
              
              <p className="text-xl text-gray-700 mb-10 leading-relaxed max-w-lg">
                Transform Jira, Monday.com, and Asana into AI-powered strategic engines. 
                <span className="font-semibold text-indigo-600">No migration headaches.</span> Immediate productivity gains.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 mb-10">
                <Link 
                  href="/trial"
                  className="group bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-8 py-4 rounded-2xl text-lg font-semibold hover:from-indigo-700 hover:to-purple-700 transition-all duration-200 shadow-xl hover:shadow-2xl flex items-center justify-center transform hover:scale-105"
                >
                  Start Free 14-Day Trial
                  <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </Link>
                <Link 
                  href="/demo"
                  className="group border-2 border-indigo-300 text-indigo-700 px-8 py-4 rounded-2xl text-lg font-semibold hover:bg-indigo-50 hover:border-indigo-400 transition-all duration-200 flex items-center justify-center"
                >
                  <Lightbulb className="mr-2 h-5 w-5" />
                  See Live Demo
                </Link>
              </div>
              
              <div className="flex items-center space-x-6 text-sm text-gray-600">
                <div className="flex items-center">
                  <CheckCircle className="w-4 h-4 text-emerald-500 mr-2" />
                  <span>No credit card required</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-4 h-4 text-emerald-500 mr-2" />
                  <span>Setup in 5 minutes</span>
                </div>
              </div>
            </div>
            
            {/* Right Column - Visual Element */}
            <div className="relative lg:ml-8">
              <div className="relative bg-white p-8 rounded-3xl shadow-2xl border border-gray-200">
                <div className="flex items-center mb-6">
                  <div className="w-8 h-8 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-lg mr-3"></div>
                  <h3 className="text-lg font-semibold text-gray-900">AI Strategy Assistant</h3>
                </div>
                <div className="space-y-4">
                  <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-4 rounded-xl border border-indigo-200">
                    <div className="text-sm text-indigo-600 font-medium mb-1">Analysis Complete ✨</div>
                    <div className="text-sm text-gray-700">Based on 847 support tickets, mobile performance optimization should be your #1 priority</div>
                  </div>
                  <div className="bg-gradient-to-r from-emerald-50 to-teal-50 p-4 rounded-xl border border-emerald-200">
                    <div className="text-sm text-emerald-600 font-medium mb-1">Impact Prediction</div>
                    <div className="text-sm text-gray-700">Projected 34% reduction in churn rate</div>
                  </div>
                  <div className="bg-gradient-to-r from-amber-50 to-orange-50 p-4 rounded-xl border border-amber-200">
                    <div className="text-sm text-amber-600 font-medium mb-1">PRD Generated</div>
                    <div className="text-sm text-gray-700">Complete requirements doc ready for review</div>
                  </div>
                </div>
              </div>
              
              {/* Floating Elements */}
              <div className="absolute -top-6 -right-6 bg-gradient-to-r from-cyan-400 to-blue-500 text-white p-4 rounded-2xl shadow-xl">
                <Target className="w-6 h-6" />
              </div>
              <div className="absolute -bottom-6 -left-6 bg-gradient-to-r from-emerald-400 to-teal-500 text-white p-4 rounded-2xl shadow-xl">
                <Brain className="w-6 h-6" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Problem Section */}
      <section className="px-6 py-24 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <div className="inline-flex items-center px-4 py-2 bg-red-100 text-red-700 text-sm font-semibold rounded-full mb-6">
              ⚠️ The Reality Check
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              The Problem Every Product Manager Faces
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              You're drowning in admin work. <span className="font-semibold text-red-600">60-80% of your time</span> goes to busywork instead of strategy.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 mb-16">
            {[
              { 
                icon: Clock, 
                title: "Writing PRDs manually", 
                description: "4 hours per document",
                stat: "32 hours/month"
              },
              { 
                icon: TrendingUp, 
                title: "Synthesizing feedback", 
                description: "Scattered across tools",
                stat: "24 hours/month"
              },
              { 
                icon: Brain, 
                title: "Creating presentations", 
                description: "From scratch every time",
                stat: "16 hours/month"
              }
            ].map((item, index) => (
              <div key={index} className="group relative bg-gradient-to-br from-red-50 to-orange-50 p-8 rounded-2xl border border-red-200 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                <div className="absolute top-4 right-4 bg-red-100 text-red-600 text-xs font-bold px-3 py-1 rounded-full">
                  {item.stat}
                </div>
                <item.icon className="h-10 w-10 text-red-600 mb-6" />
                <h3 className="text-xl font-bold text-gray-900 mb-3">{item.title}</h3>
                <p className="text-gray-600 leading-relaxed">{item.description}</p>
              </div>
            ))}
          </div>

          <div className="relative text-center">
            <div className="bg-gradient-to-r from-amber-50 to-orange-50 p-10 rounded-3xl border-2 border-amber-200 shadow-xl">
              <div className="text-6xl mb-6">⏰</div>
              <p className="text-2xl text-gray-900 font-bold mb-4">
                Meanwhile, your competitors are shipping <span className="text-indigo-600">40% faster</span> because their PMs focus on strategy, not busywork.
              </p>
              <p className="text-gray-600 text-lg">
                While you're writing docs, they're analyzing market opportunities.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Solution Section */}
      <section className="px-6 py-24 bg-gradient-to-br from-gray-50 to-indigo-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <div className="inline-flex items-center px-4 py-2 bg-indigo-100 text-indigo-700 text-sm font-semibold rounded-full mb-6">
              ✨ The PM33 Difference
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Enhancement, Not Replacement
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Stop forcing your team to abandon tools they love. Start making them smarter.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 mb-16">
            {/* Traditional Approach */}
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-red-400 to-pink-400 rounded-3xl transform rotate-1 group-hover:rotate-2 transition-transform"></div>
              <div className="relative bg-white p-10 rounded-3xl shadow-xl border border-gray-200">
                <div className="flex items-center mb-6">
                  <div className="text-3xl mr-4">❌</div>
                  <div>
                    <div className="text-red-600 text-lg font-bold">Traditional Approach</div>
                    <div className="text-gray-500 text-sm">The painful way everyone else does it</div>
                  </div>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-6">Replace Everything</h3>
                <div className="space-y-4">
                  {[
                    { icon: "📦", text: "Migrate all your data and workflows", pain: "3-6 months" },
                    { icon: "📚", text: "Re-train your entire team on new tools", pain: "Weeks of training" },
                    { icon: "📉", text: "Lose months of productivity during transition", pain: "40% productivity drop" },
                    { icon: "💸", text: "Pay $25-74/user/month for 'comprehensive' platforms", pain: "$50K+ annually" }
                  ].map((item, index) => (
                    <div key={index} className="flex items-start p-4 bg-red-50 rounded-xl border border-red-200">
                      <div className="text-xl mr-3 mt-0.5">{item.icon}</div>
                      <div className="flex-1">
                        <div className="text-gray-700 font-medium">{item.text}</div>
                        <div className="text-red-600 text-sm font-semibold">{item.pain}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* PM33 Approach */}
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-emerald-400 to-cyan-400 rounded-3xl transform -rotate-1 group-hover:-rotate-2 transition-transform"></div>
              <div className="relative bg-white p-10 rounded-3xl shadow-xl border border-gray-200">
                <div className="flex items-center mb-6">
                  <div className="text-3xl mr-4">✨</div>
                  <div>
                    <div className="text-emerald-600 text-lg font-bold">PM33 Approach</div>
                    <div className="text-gray-500 text-sm">The smart way that actually works</div>
                  </div>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-6">Supercharge What Works</h3>
                <div className="space-y-4">
                  {[
                    { icon: "🔗", text: "Plug into your existing tools (Jira, Monday, Asana)", benefit: "5-minute setup" },
                    { icon: "🤖", text: "AI brain analyzes everything across your current stack", benefit: "Instant insights" },
                    { icon: "⚡", text: "Automate strategic work while keeping familiar workflows", benefit: "Zero disruption" },
                    { icon: "🎯", text: "Pay for results, not seats - starting at $20/user", benefit: "60% cost savings" }
                  ].map((item, index) => (
                    <div key={index} className="flex items-start p-4 bg-emerald-50 rounded-xl border border-emerald-200">
                      <div className="text-xl mr-3 mt-0.5">{item.icon}</div>
                      <div className="flex-1">
                        <div className="text-gray-700 font-medium">{item.text}</div>
                        <div className="text-emerald-600 text-sm font-semibold">{item.benefit}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
          
          {/* Results Comparison */}
          <div className="bg-white p-10 rounded-3xl shadow-xl border border-gray-200">
            <div className="text-center mb-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-4">The Results Speak for Themselves</h3>
              <p className="text-gray-600">Real data from 2,500+ product managers using PM33</p>
            </div>
            <div className="grid md:grid-cols-3 gap-8">
              {[
                { metric: "40%", label: "More Features Shipped", description: "Without adding headcount" },
                { metric: "72h", label: "Time Saved Monthly", description: "Per product manager" },
                { metric: "<5min", label: "Average Setup Time", description: "From signup to insights" }
              ].map((stat, index) => (
                <div key={index} className="text-center p-6 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl border border-indigo-200">
                  <div className="text-4xl font-bold text-indigo-600 mb-2">{stat.metric}</div>
                  <div className="text-lg font-semibold text-gray-900 mb-1">{stat.label}</div>
                  <div className="text-gray-600 text-sm">{stat.description}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="px-6 py-24 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <div className="inline-flex items-center px-4 py-2 bg-purple-100 text-purple-700 text-sm font-semibold rounded-full mb-6">
              🤖 AI-Powered Features
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              How PM33's AI Transforms Your PM Work
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              See exactly how AI eliminates the busywork that's keeping you from strategic thinking.
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-12">
            {[
              {
                icon: Brain,
                color: "from-purple-400 to-pink-400",
                bgColor: "from-purple-50 to-pink-50",
                borderColor: "border-purple-200",
                iconBg: "bg-gradient-to-r from-purple-500 to-pink-500",
                title: "Strategic Intelligence Layer",
                subtitle: "Turn scattered data into strategic insights",
                problem: "You have data scattered across tools but no unified insights",
                solution: "AI analyzes patterns across Jira tickets, Slack discussions, customer feedback, and market research to generate strategic recommendations",
                example: "Based on 847 support tickets and 23 customer interviews, AI recommends prioritizing mobile performance optimization - projected 34% reduction in churn",
                features: ["Cross-platform data analysis", "Predictive impact scoring", "Strategic recommendations", "Competitive intelligence"]
              },
              {
                icon: Zap,
                color: "from-cyan-400 to-blue-400",
                bgColor: "from-cyan-50 to-blue-50",
                borderColor: "border-cyan-200",
                iconBg: "bg-gradient-to-r from-cyan-500 to-blue-500",
                title: "Automated Documentation",
                subtitle: "From idea to complete PRD in minutes",
                problem: "Writing PRDs, user stories, and requirements takes hours",
                solution: "AI generates comprehensive documentation from brief descriptions, automatically formatted for your team's standards",
                example: "Input: 'Improve checkout flow' → Output: Complete PRD with user stories, acceptance criteria, technical requirements, and success metrics",
                features: ["Smart PRD generation", "User story creation", "Acceptance criteria", "Technical specifications"]
              }
            ].map((feature, index) => (
              <div key={index} className="group relative">
                <div className={`absolute inset-0 bg-gradient-to-r ${feature.color} rounded-3xl transform ${index % 2 === 0 ? 'rotate-1' : '-rotate-1'} group-hover:${index % 2 === 0 ? 'rotate-2' : '-rotate-2'} transition-transform opacity-20`}></div>
                <div className="relative bg-white p-10 rounded-3xl shadow-xl border border-gray-200 h-full">
                  {/* Icon and Title */}
                  <div className="flex items-start mb-8">
                    <div className={`${feature.iconBg} p-4 rounded-2xl mr-6 shadow-lg`}>
                      <feature.icon className="h-8 w-8 text-white" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-2xl font-bold text-gray-900 mb-2">{feature.title}</h3>
                      <p className="text-lg text-gray-600">{feature.subtitle}</p>
                    </div>
                  </div>
                  
                  {/* Problem/Solution Flow */}
                  <div className="space-y-6 mb-8">
                    <div className="bg-red-50 p-6 rounded-2xl border border-red-200">
                      <div className="text-red-600 font-bold text-sm mb-2 uppercase tracking-wide">The Problem</div>
                      <p className="text-gray-700 font-medium">{feature.problem}</p>
                    </div>
                    
                    <div className={`bg-gradient-to-r ${feature.bgColor} p-6 rounded-2xl border ${feature.borderColor}`}>
                      <div className="text-indigo-600 font-bold text-sm mb-2 uppercase tracking-wide">PM33 Solution</div>
                      <p className="text-gray-700 font-medium mb-4">{feature.solution}</p>
                      
                      <div className="grid grid-cols-2 gap-3">
                        {feature.features.map((feat, idx) => (
                          <div key={idx} className="flex items-center text-sm text-gray-600">
                            <CheckCircle className="w-4 h-4 text-emerald-500 mr-2 flex-shrink-0" />
                            <span>{feat}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                  
                  {/* Example */}
                  <div className="bg-gray-900 p-6 rounded-2xl">
                    <div className="text-emerald-400 font-bold text-xs mb-2 uppercase tracking-wide">Real Example</div>
                    <p className="text-gray-300 text-sm font-mono leading-relaxed">{feature.example}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {/* Additional Features Grid */}
          <div className="mt-20">
            <h3 className="text-3xl font-bold text-gray-900 text-center mb-12">Plus Everything Else You Need</h3>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                { icon: Users, title: "Team Collaboration", description: "Real-time commenting and feedback" },
                { icon: Target, title: "Impact Scoring", description: "AI-powered feature prioritization" },
                { icon: TrendingUp, title: "Performance Analytics", description: "Track what's actually working" },
                { icon: Lightbulb, title: "Smart Insights", description: "Proactive recommendations" }
              ].map((item, index) => (
                <div key={index} className="group p-6 bg-gradient-to-br from-gray-50 to-indigo-50 rounded-2xl border border-gray-200 hover:shadow-xl transition-all duration-300 hover:-translate-y-1 text-center">
                  <div className="bg-white p-3 rounded-xl shadow-lg inline-block mb-4 group-hover:scale-110 transition-transform">
                    <item.icon className="h-6 w-6 text-indigo-600" />
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-2">{item.title}</h4>
                  <p className="text-gray-600 text-sm">{item.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Social Proof Section */}
      <section className="px-6 py-24 bg-gradient-to-br from-gray-50 to-purple-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <div className="inline-flex items-center px-4 py-2 bg-emerald-100 text-emerald-700 text-sm font-semibold rounded-full mb-6">
              🏆 Customer Success Stories
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Real Results from PM Teams Using PM33
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Don't take our word for it. Here's what product teams are saying about their results.
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8 mb-16">
            {[
              {
                quote: "We shipped 40% more features without hiring additional PMs",
                detail: "PM33's AI handles all our routine documentation and analysis. Our PMs now spend 3x more time on customer research and strategic planning. Game-changer for our product velocity.",
                author: "Sarah Chen",
                title: "Head of Product at TechFlow",
                company: "Series B SaaS",
                avatar: "SC",
                bgColor: "from-purple-400 to-pink-400",
                metric: "40% more features",
                timeframe: "Without adding headcount"
              },
              {
                quote: "ROI paid for itself in the first month",
                detail: "The AI insights helped us identify our #1 churn driver within weeks. Fixing it reduced churn by 28%. PM33's cost became irrelevant compared to the revenue impact.",
                author: "Marcus Rodriguez",
                title: "VP Product at DataSync",
                company: "Growth-stage startup",
                avatar: "MR",
                bgColor: "from-cyan-400 to-blue-400",
                metric: "28% churn reduction",
                timeframe: "First month ROI"
              },
              {
                quote: "Finally, a tool that makes our existing stack smarter",
                detail: "We've tried 5 different PM platforms. PM33 is the first that enhanced our Jira workflow instead of forcing us to abandon it. Team adoption was instant.",
                author: "Jennifer Liu",
                title: "Senior PM at CloudOps",
                company: "Enterprise SaaS",
                avatar: "JL",
                bgColor: "from-emerald-400 to-teal-400",
                metric: "100% team adoption",
                timeframe: "Day one"
              }
            ].map((testimonial, index) => (
              <div key={index} className="group relative">
                <div className={`absolute inset-0 bg-gradient-to-r ${testimonial.bgColor} rounded-3xl transform ${index % 2 === 0 ? 'rotate-1' : '-rotate-1'} group-hover:${index % 2 === 0 ? 'rotate-2' : '-rotate-2'} transition-transform opacity-10`}></div>
                <div className="relative bg-white p-8 rounded-3xl shadow-xl border border-gray-200 h-full">
                  {/* Quote Mark */}
                  <div className="text-4xl text-indigo-600 mb-4 font-serif">“</div>
                  
                  {/* Main Quote */}
                  <h3 className="text-xl font-bold text-gray-900 mb-4 leading-tight">{testimonial.quote}</h3>
                  
                  {/* Detail */}
                  <p className="text-gray-600 mb-6 leading-relaxed">{testimonial.detail}</p>
                  
                  {/* Metrics */}
                  <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-4 rounded-2xl border border-indigo-200 mb-6">
                    <div className="text-2xl font-bold text-indigo-600">{testimonial.metric}</div>
                    <div className="text-sm text-gray-600">{testimonial.timeframe}</div>
                  </div>
                  
                  {/* Author */}
                  <div className="flex items-center pt-4 border-t border-gray-200">
                    <div className={`w-12 h-12 bg-gradient-to-r ${testimonial.bgColor} rounded-full flex items-center justify-center text-white font-bold mr-4`}>
                      {testimonial.avatar}
                    </div>
                    <div>
                      <div className="font-semibold text-gray-900">{testimonial.author}</div>
                      <div className="text-gray-600 text-sm">{testimonial.title}</div>
                      <div className="text-gray-500 text-xs">{testimonial.company}</div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {/* Company Logos */}
          <div className="text-center">
            <p className="text-gray-600 mb-8">Trusted by product teams at companies like:</p>
            <div className="flex flex-wrap justify-center items-center gap-8 grayscale opacity-60">
              {['TechFlow', 'DataSync', 'CloudOps', 'StartupX', 'ScaleUp', 'GrowthCo'].map((company, index) => (
                <div key={index} className="bg-white px-6 py-3 rounded-lg shadow-md border border-gray-200">
                  <div className="text-gray-800 font-semibold text-lg">{company}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative px-6 py-24 overflow-hidden">
        {/* Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-600 via-purple-700 to-cyan-600"></div>
        <div className="absolute inset-0">
          <div className="absolute top-0 left-0 w-72 h-72 bg-white rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob"></div>
          <div className="absolute top-0 right-0 w-72 h-72 bg-cyan-300 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob animation-delay-2000"></div>
          <div className="absolute bottom-0 left-1/2 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob animation-delay-4000"></div>
        </div>
        
        <div className="max-w-4xl mx-auto text-center relative">
          {/* Badge */}
          <div className="inline-flex items-center px-4 py-2 bg-white/20 backdrop-blur-md text-white text-sm font-semibold rounded-full mb-8">
            ✨ Transform Your PM Work Today
          </div>
          
          {/* Main Heading */}
          <h2 className="text-4xl md:text-6xl font-bold text-white mb-8 leading-tight">
            Ready to <span className="bg-gradient-to-r from-cyan-300 to-emerald-300 bg-clip-text text-transparent">10x Your PM Productivity</span>?
          </h2>
          
          {/* Subheading */}
          <p className="text-xl md:text-2xl text-indigo-100 mb-12 leading-relaxed max-w-3xl mx-auto">
            Join <span className="font-bold text-cyan-300">2,500+ product teams</span> using PM33 to focus on strategy, not busywork.
          </p>
          
          {/* CTAs */}
          <div className="flex flex-col sm:flex-row gap-6 justify-center mb-12">
            <Link 
              href="/trial"
              className="group bg-white text-indigo-600 px-10 py-5 rounded-2xl text-xl font-bold hover:bg-indigo-50 transition-all duration-300 shadow-2xl hover:shadow-white/25 transform hover:scale-105 flex items-center justify-center"
            >
              Start Your Free 14-Day Trial
              <ArrowRight className="ml-3 h-6 w-6 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link 
              href="/demo"
              className="group border-2 border-white/30 backdrop-blur-md text-white px-10 py-5 rounded-2xl text-xl font-bold hover:bg-white/10 hover:border-white/50 transition-all duration-300 flex items-center justify-center"
            >
              <Lightbulb className="mr-3 h-6 w-6" />
              Book a Live Demo
            </Link>
          </div>
          
          {/* Trust Signals */}
          <div className="grid md:grid-cols-3 gap-8 mb-8">
            {[
              { icon: CheckCircle, text: "No credit card required" },
              { icon: Zap, text: "5-minute setup" },
              { icon: Users, text: "Cancel anytime" }
            ].map((item, index) => (
              <div key={index} className="flex items-center justify-center text-indigo-100">
                <item.icon className="w-5 h-5 mr-3 text-emerald-300" />
                <span className="font-medium">{item.text}</span>
              </div>
            ))}
          </div>
          
          {/* Final Message */}
          <p className="text-indigo-200 text-lg">
            Stop doing busywork. <span className="font-bold text-white">Start doing strategy.</span>
          </p>
        </div>
      </section>

      <Footer />
    </div>
  )
}