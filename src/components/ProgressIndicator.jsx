import React from 'react'

const ProgressIndicator = ({ currentStep }) => {
  const totalSteps = 10

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between">
        {Array.from({ length: totalSteps }, (_, i) => {
          const stepNumber = i + 1
          const isCompleted = stepNumber < currentStep
          const isCurrent = stepNumber === currentStep
          
          return (
            <div key={stepNumber} className="flex items-center">
              <div
                className={`
                  w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
                  ${isCurrent 
                    ? 'bg-blue-600 text-white' 
                    : isCompleted 
                    ? 'bg-green-500 text-white' 
                    : 'bg-gray-200 text-gray-600'
                  }
                `}
              >
                {isCompleted ? '✓' : stepNumber}
              </div>
              
              {stepNumber < totalSteps && (
                <div 
                  className={`
                    w-12 h-1 mx-2
                    ${stepNumber < currentStep ? 'bg-green-500' : 'bg-gray-200'}
                  `}
                />
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default ProgressIndicator