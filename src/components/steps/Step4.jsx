import React from 'react'
import ProgressIndicator from '../ProgressIndicator'

const Step4 = () => {
  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">📊 Step 4: Content Templates</h1>
        <p className="text-gray-600">Generate Excel templates for offline content preparation.</p>
      </div>

      <ProgressIndicator currentStep={4} />

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📊</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Excel Template Generation</h2>
          <p className="text-gray-600 mb-6">Create structured templates for content preparation.</p>
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 text-left max-w-md mx-auto">
            <p className="text-sm text-purple-800">
              <strong>Templates Include:</strong>
            </p>
            <ul className="text-sm text-purple-700 mt-2 space-y-1">
              <li>• Products catalog template</li>
              <li>• Pages content template</li>
              <li>• Image mapping guide</li>
              <li>• Validation rules</li>
              <li>• Import documentation</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Step4