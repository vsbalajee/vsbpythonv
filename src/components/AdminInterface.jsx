import React, { useState } from 'react'

const AdminInterface = () => {
  const [activeTab, setActiveTab] = useState('requirements')

  const tabs = [
    { id: 'requirements', label: 'Requirements', icon: '📋' },
    { id: 'models', label: 'Models & Keys', icon: '🔑' },
    { id: 'products', label: 'Products', icon: '🛍️' },
    { id: 'errors', label: 'Errors', icon: '🚨' },
    { id: 'tests', label: 'Tests', icon: '🧪' }
  ]

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">🛠️ Admin Interface</h1>
        <p className="text-gray-600">Manage your Vsbvibe project settings and configuration.</p>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  py-4 px-1 border-b-2 font-medium text-sm transition-colors
                  ${activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === 'requirements' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Requirements Management</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Current Requirements
                  </label>
                  <textarea
                    rows={6}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
                    disabled
                    placeholder="No requirements loaded..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Update Requirements
                  </label>
                  <textarea
                    rows={6}
                    placeholder="Enter new or updated requirements..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Version Note
                  </label>
                  <input
                    type="text"
                    placeholder="What changed?"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  Update Requirements
                </button>
              </div>
            </div>
          )}

          {activeTab === 'models' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">AI Models & API Keys</h2>
              <div className="space-y-6">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                    <span className="text-green-800">OpenAI key loaded. Default model: <strong>gpt-5-mini</strong></span>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      OpenAI API Key
                    </label>
                    <input
                      type="password"
                      placeholder="sk-..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Anthropic API Key
                    </label>
                    <input
                      type="password"
                      placeholder="sk-ant-..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Supabase URL
                    </label>
                    <input
                      type="url"
                      placeholder="https://your-project.supabase.co"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Supabase Anon Key
                    </label>
                    <input
                      type="password"
                      placeholder="eyJ..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
                
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  Save Settings
                </button>
              </div>
            </div>
          )}

          {activeTab === 'products' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">🛍️ Products Management</h2>
              <div className="text-center py-8">
                <p className="text-gray-600">Products management interface will be implemented here.</p>
              </div>
            </div>
          )}

          {activeTab === 'errors' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">🚨 Error Management</h2>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-green-800">✅ No errors found!</p>
                <p className="text-sm text-green-600 mt-1">Errors will appear here when they occur.</p>
              </div>
            </div>
          )}

          {activeTab === 'tests' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">🧪 Testing Dashboard</h2>
              <div className="text-center py-8">
                <p className="text-gray-600">Testing interface will be implemented here.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default AdminInterface