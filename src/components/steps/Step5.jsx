import React from 'react'
import ProgressIndicator from '../ProgressIndicator'

const Step5 = () => {
  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">🛍️ Step 5: Data & Products</h1>
        <p className="text-gray-600">Import content from Excel templates with automatic image mapping.</p>
      </div>

      <ProgressIndicator currentStep={5} />

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🛍️</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Data Import & Image Mapping</h2>
          <p className="text-gray-600 mb-6">Import your prepared content with intelligent image auto-mapping.</p>
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 text-left max-w-md mx-auto">
            <p className="text-sm text-orange-800">
              <strong>Import Features:</strong>
            </p>
            <ul className="text-sm text-orange-700 mt-2 space-y-1">
              <li>• Dry-run validation</li>
              <li>• Automatic image mapping</li>
              <li>• Data validation & cleanup</li>
              <li>• Backup & undo support</li>
              <li>• Error reporting</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Step5