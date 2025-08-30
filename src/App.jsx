import React, { useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Step1 from './components/steps/Step1'
import Step2 from './components/steps/Step2'
import Step3 from './components/steps/Step3'
import Step4 from './components/steps/Step4'
import Step5 from './components/steps/Step5'
import AdminInterface from './components/AdminInterface'

function App() {
  const [currentStep, setCurrentStep] = useState(1)

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar currentStep={currentStep} onStepChange={setCurrentStep} />
      
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<Step1 />} />
          <Route path="/step1" element={<Step1 />} />
          <Route path="/step2" element={<Step2 />} />
          <Route path="/step3" element={<Step3 />} />
          <Route path="/step4" element={<Step4 />} />
          <Route path="/step5" element={<Step5 />} />
          <Route path="/admin" element={<AdminInterface />} />
        </Routes>
      </main>
    </div>
  )
}

export default App