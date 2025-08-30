@@ .. @@
 import React, { useState } from 'react'
-import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
+import { Routes, Route } from 'react-router-dom'
 import Sidebar from './components/Sidebar'
 import Step1 from './components/steps/Step1'
 import Step2 from './components/steps/Step2'
@@ .. @@
   }
 
   return (
-    <Router>
-      <div className="flex h-screen bg-gray-50">
-        <Sidebar currentStep={currentStep} onStepChange={setCurrentStep} />
-        
-        <main className="flex-1 overflow-auto">
-          <Routes>
-            <Route path="/" element={<Step1 />} />
-            <Route path="/step1" element={<Step1 />} />
-            <Route path="/step2" element={<Step2 />} />
-            <Route path="/step3" element={<Step3 />} />
-            <Route path="/step4" element={<Step4 />} />
-            <Route path="/step5" element={<Step5 />} />
-            <Route path="/admin" element={<AdminInterface />} />
-          </Routes>
-        </main>
-      </div>
-    </Router>
+    <div className="flex h-screen bg-gray-50">
+      <Sidebar currentStep={currentStep} onStepChange={setCurrentStep} />
+      
+      <main className="flex-1 overflow-auto">
+        <Routes>
+          <Route path="/" element={<Step1 />} />
+          <Route path="/step1" element={<Step1 />} />
+          <Route path="/step2" element={<Step2 />} />
+          <Route path="/step3" element={<Step3 />} />
+          <Route path="/step4" element={<Step4 />} />
+          <Route path="/step5" element={<Step5 />} />
+          <Route path="/admin" element={<AdminInterface />} />
+        </Routes>
+      </main>
+    </div>
   )
 }