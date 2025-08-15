import Link from 'next/link'

export default function Footer() {
  return (
    <footer className="px-6 py-16 bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto">
        <div className="grid md:grid-cols-4 gap-12">
          <div className="md:col-span-1">
            <div className="flex items-center mb-6">
              <div className="text-3xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">PM33</div>
              <div className="ml-3 px-2 py-1 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 text-indigo-300 text-xs font-medium rounded-full border border-indigo-500/30">
                AI-Powered
              </div>
            </div>
            <p className="text-gray-400 leading-relaxed">
              Built by the PM community, for the PM community. Enhancing your existing tools with AI intelligence.
            </p>
            <div className="mt-6">
              <Link 
                href="/trial"
                className="inline-flex items-center bg-gradient-to-r from-indigo-500 to-purple-500 text-white px-6 py-3 rounded-xl font-semibold hover:from-indigo-600 hover:to-purple-600 transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                Start Free Trial
              </Link>
            </div>
          </div>
          
          <div>
            <h4 className="font-bold mb-6 text-white">Product</h4>
            <div className="space-y-4 text-gray-400">
              <Link href="/features" className="block hover:text-indigo-400 transition-colors">Features</Link>
              <Link href="/pricing" className="block hover:text-indigo-400 transition-colors">Pricing</Link>
              <Link href="/ai-product-management-tool" className="block hover:text-indigo-400 transition-colors">AI PM Tool</Link>
              <Link href="/product-management-software" className="block hover:text-indigo-400 transition-colors">PM Software</Link>
            </div>
          </div>
          
          <div>
            <h4 className="font-bold mb-6 text-white">Solutions</h4>
            <div className="space-y-4 text-gray-400">
              <Link href="/jira-alternative" className="block hover:text-indigo-400 transition-colors">Jira Alternative</Link>
              <Link href="/monday-alternative" className="block hover:text-indigo-400 transition-colors">Monday Alternative</Link>
              <Link href="/asana-competitor" className="block hover:text-indigo-400 transition-colors">Asana Alternative</Link>
              <Link href="/ai-powered-roadmap-tool" className="block hover:text-indigo-400 transition-colors">AI Roadmap Tool</Link>
            </div>
          </div>
          
          <div>
            <h4 className="font-bold mb-6 text-white">Community</h4>
            <div className="space-y-4 text-gray-400">
              <Link href="/templates" className="block hover:text-indigo-400 transition-colors">PM Templates</Link>
              <Link href="/about" className="block hover:text-indigo-400 transition-colors">About</Link>
              <Link href="/contact" className="block hover:text-indigo-400 transition-colors">Contact</Link>
              <Link href="/security" className="block hover:text-indigo-400 transition-colors">Security</Link>
              <Link href="/privacy" className="block hover:text-indigo-400 transition-colors">Privacy</Link>
            </div>
          </div>
        </div>
        
        <div className="border-t border-gray-800 mt-12 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-400 mb-4 md:mb-0">
              &copy; 2025 PM33. Built by the PM community, for the PM community.
            </p>
            <div className="flex items-center space-x-6 text-gray-400">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-emerald-400 rounded-full mr-2 animate-pulse"></div>
                <span className="text-sm">2,500+ PMs trust PM33</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}