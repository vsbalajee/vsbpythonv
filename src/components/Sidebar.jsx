import React from 'react'
import { Link, useLocation } from 'react-router-dom'

const Sidebar = ({ currentStep, onStepChange }) => {
  const location = useLocation()
  
  const steps = [
    { number: 1, title: 'Project Setup', icon: '🚀', path: '/step1' },
    { number: 2, title: 'Analysis & Plan', icon: '📋', path: '/step2' },
    { number: 3, title: 'Generate Scaffold', icon: '🏗️', path: '/step3' },
    { number: 4, title: 'Content Import', icon: '📊', path: '/step4' },
    { number: 5, title: 'Data & Products', icon: '🛍️', path: '/step5' },
    { number: 6, title: 'AI Content', icon: '🤖', path: '/step6' },
    { number: 7, title: 'Design & Style', icon: '🎨', path: '/step7' },
    { number: 8, title: 'SEO & Performance', icon: '🔍', path: '/step8' },
    { number: 9, title: 'Test & Preview', icon: '🧪', path: '/step9' },
    { number: 10, title: 'Deploy & Publish', icon: '🚀', path: '/step10' }
  ]

  return (
    <div className="w-80 bg-white shadow-lg border-r border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-2xl font-bold text-gray-900">🚀 Vsbvibe</h1>
        <p className="text-sm text-gray-600 mt-1">Website Builder & Generator</p>
      </div>

      {/* Steps Navigation */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-2">
          {steps.map((step) => {
            const isActive = location.pathname === step.path
            const isCompleted = step.number < currentStep
            
            return (
              <Link
                key={step.number}
                to={step.path}
                onClick={() => onStepChange(step.number)}
                className={`
                  flex items-center p-3 rounded-lg transition-colors duration-200
                  ${isActive 
                    ? 'bg-blue-50 border-2 border-blue-200 text-blue-700' 
                    : isCompleted
                    ? 'bg-green-50 border border-green-200 text-green-700 hover:bg-green-100'
                    : 'border border-gray-200 text-gray-600 hover:bg-gray-50'
                  }
                `}
              >
                <span className="text-xl mr-3">{step.icon}</span>
                <div className="flex-1">
                  <div className="font-medium">{step.number}. {step.title}</div>
                </div>
                {isCompleted && (
                  <span className="text-green-500">✅</span>
                )}
                {isActive && (
                  <span className="text-blue-500">🔵</span>
                )}
              </Link>
            )
          })}
        </div>

        {/* Admin Interface */}
        <div className="mt-6 pt-4 border-t border-gray-200">
          <Link
            to="/admin"
            className="flex items-center p-3 rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50 transition-colors duration-200"
          >
            <span className="text-xl mr-3">🛠️</span>
            <span className="font-medium">Admin Interface</span>
          </Link>
        </div>

        {/* Help Section */}
        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-medium text-blue-900 mb-2">ℹ️ Help</h3>
          <div className="text-sm text-blue-700 space-y-1">
            <p><strong>Vsbvibe Workflow:</strong></p>
            <ol className="list-decimal list-inside space-y-1 text-xs">
              <li>Set up project basics</li>
              <li>Analyze requirements</li>
              <li>Generate site scaffold</li>
              <li>Import content</li>
              <li>Add products/data</li>
              <li>Generate AI content</li>
              <li>Customize design</li>
              <li>Optimize SEO</li>
              <li>Test everything</li>
              <li>Deploy live</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Sidebar