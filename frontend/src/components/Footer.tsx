import Link from 'next/link'
import { Github, Linkedin, Mail } from 'lucide-react'

export default function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="border-t bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* About */}
          <div className="col-span-1 md:col-span-2">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              XAI Finance Platform
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              A research initiative to evaluate the performance and interpretability 
              of AI models in finance using real-world datasets and open-source 
              explainability methods.
            </p>
            <div className="flex space-x-4">
              <a
                href="https://github.com/Jakolo6/XAI_Platform_Master_Thesis"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-600 hover:text-gray-900 transition-colors"
                aria-label="GitHub"
              >
                <Github className="h-5 w-5" />
              </a>
              <a
                href="https://www.linkedin.com/in/jakob-lindner"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-600 hover:text-gray-900 transition-colors"
                aria-label="LinkedIn"
              >
                <Linkedin className="h-5 w-5" />
              </a>
              <a
                href="mailto:jakob.lindner@example.com"
                className="text-gray-600 hover:text-gray-900 transition-colors"
                aria-label="Email"
              >
                <Mail className="h-5 w-5" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-4">
              Quick Links
            </h3>
            <ul className="space-y-2">
              <li>
                <Link href="/" className="text-sm text-gray-600 hover:text-gray-900">
                  Home
                </Link>
              </li>
              <li>
                <Link href="/datasets" className="text-sm text-gray-600 hover:text-gray-900">
                  Datasets
                </Link>
              </li>
              <li>
                <Link href="/benchmarks" className="text-sm text-gray-600 hover:text-gray-900">
                  Benchmarks
                </Link>
              </li>
              <li>
                <a
                  href="https://github.com/Jakolo6/XAI_Platform_Master_Thesis"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-gray-600 hover:text-gray-900"
                >
                  Documentation
                </a>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-4">
              Resources
            </h3>
            <ul className="space-y-2">
              <li>
                <a
                  href="https://github.com/Jakolo6/XAI_Platform_Master_Thesis"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-gray-600 hover:text-gray-900"
                >
                  GitHub Repository
                </a>
              </li>
              <li>
                <a
                  href="https://supabase.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-gray-600 hover:text-gray-900"
                >
                  Supabase
                </a>
              </li>
              <li>
                <a
                  href="https://www.novasbe.unl.pt/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-gray-600 hover:text-gray-900"
                >
                  Nova SBE
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-8 pt-8 border-t border-gray-200">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <p className="text-sm text-gray-600 text-center md:text-left">
              Created by{' '}
              <span className="font-semibold text-gray-900">Jakob Lindner</span>
              {' '}| Nova SBE Master Thesis Project
            </p>
            <p className="text-sm text-gray-600">
              © {currentYear} XAI Finance Platform. Open Source on{' '}
              <a
                href="https://github.com/Jakolo6/XAI_Platform_Master_Thesis"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                GitHub
              </a>
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}
