import React, { useState } from 'react'
import ProgressIndicator from '../ProgressIndicator'

const Step1 = () => {
  const [formData, setFormData] = useState({
    projectName: '',
    companyName: '',
    localFolder: '~/vsbvibe-projects',
    referenceUrl: '',
    contentMode: 'AI Generated',
    requirements: ''
  })

  const [showAIPanel, setShowAIPanel] = useState(false)

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    // Validate required fields
    if (!formData.projectName || !formData.companyName || !formData.requirements) {
      alert('Please fill in all required fields marked with *')
      return
    }

    // Process form submission
    console.log('Creating project with data:', formData)
    alert('Project created successfully! Moving to Step 2...')
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">🚀 Step 1: Project Setup & Requirements</h1>
        <p className="text-gray-600">Set up your project basics and define your requirements.</p>
      </div>

      <ProgressIndicator currentStep={1} />

      {/* AI Connect & Error Logs Panel */}
      <div className="mb-8">
        <button
          onClick={() => setShowAIPanel(!showAIPanel)}
          className="flex items-center justify-between w-full p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <span className="font-medium text-gray-900">🔐 AI Connect & Error Logs</span>
          <span className="text-gray-500">{showAIPanel ? '▼' : '▶'}</span>
        </button>
        
        {showAIPanel && (
          <div className="mt-4 p-4 bg-white border border-gray-200 rounded-lg">
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <span className="w-3 h-3 bg-green-500 rounded-full"></span>
                <span className="text-sm text-gray-700">OpenAI key loaded. Default model: <strong>gpt-5-mini</strong></span>
              </div>
              
              <div className="pt-2 border-t border-gray-200">
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm">
                  ⬇️ Download Error Report (Excel)
                </button>
                <p className="text-xs text-gray-500 mt-1">No error report yet. It will appear here after the first captured error.</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Project Setup Form */}
      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Project Information</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Project Name *
            </label>
            <input
              type="text"
              name="projectName"
              value={formData.projectName}
              onChange={handleInputChange}
              placeholder="My Awesome Website"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Reference URL (Optional)
            </label>
            <input
              type="url"
              name="referenceUrl"
              value={formData.referenceUrl}
              onChange={handleInputChange}
              placeholder="https://example.com"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Company/Brand Name *
            </label>
            <input
              type="text"
              name="companyName"
              value={formData.companyName}
              onChange={handleInputChange}
              placeholder="Your Company Name"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Content Mode *
            </label>
            <select
              name="contentMode"
              value={formData.contentMode}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="AI Generated">AI Generated</option>
              <option value="User Provided">User Provided</option>
              <option value="Hybrid">Hybrid</option>
            </select>
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Local Folder Path *
            </label>
            <input
              type="text"
              name="localFolder"
              value={formData.localFolder}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
            <p className="text-xs text-gray-500 mt-1">Where to save your project files</p>
          </div>
        </div>

        {/* Assets Section */}
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Assets (Optional)</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Logo Upload
            </label>
            <input
              type="file"
              accept=".png,.jpg,.jpeg,.svg"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">Upload your company logo</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Screenshots (5-10 images)
            </label>
            <input
              type="file"
              accept=".png,.jpg,.jpeg"
              multiple
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">Upload reference screenshots for inspiration</p>
          </div>
        </div>

        {/* Requirements Section */}
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Requirements</h3>
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Project Requirements *
          </label>
          <textarea
            name="requirements"
            value={formData.requirements}
            onChange={handleInputChange}
            rows={8}
            placeholder={`Describe your website requirements in detail:

• What type of website do you need? (e-commerce, portfolio, blog, etc.)
• Who is your target audience?
• What features do you want? (contact forms, product catalog, blog, etc.)
• What is your business about?
• Any specific design preferences?
• Integration requirements? (payment, CRM, analytics, etc.)

Example: "I need an e-commerce website for selling handmade jewelry. Target audience is women aged 25-45. Need product catalog, shopping cart, customer reviews, blog section, and contact form. Modern, elegant design with focus on product photography."`}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>

        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
          >
            Create Project
          </button>
        </div>
      </form>
    </div>
  )
}

export default Step1