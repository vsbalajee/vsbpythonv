import React from 'react'
import ProgressIndicator from '../ProgressIndicator'

const Step2 = () => {
  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">📋 Step 2: Analysis & Plan</h1>
        <p className="text-gray-600">Analyze requirements and generate UI/UX plan.</p>
      </div>

      <ProgressIndicator currentStep={2} />

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📋</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Analysis & Plan Generation</h2>
          <p className="text-gray-600 mb-6">This step will analyze your requirements and create a comprehensive UI/UX plan.</p>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-left max-w-md mx-auto">
            <p className="text-sm text-blue-800">
              <strong>Coming Soon:</strong> AI-powered analysis of your requirements to generate:
            </p>
            <ul className="text-sm text-blue-700 mt-2 space-y-1">
              <li>• Site architecture and page structure</li>
              <li>• UI/UX recommendations</li>
              <li>• Technology stack selection</li>
              <li>• Brand tokens and design system</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Step2