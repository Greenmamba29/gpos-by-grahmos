import "@/App.css";
import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AppProvider } from "@/context/AppContext";
import { Shell } from "@/components/Shell";
import { Toaster } from "@/components/ui/sonner";
import Today from "@/pages/Today";
import DecisionRoom from "@/pages/DecisionRoom";
import ApprovalCenter from "@/pages/ApprovalCenter";
import Supplier360 from "@/pages/Supplier360";
import CampusMemory from "@/pages/CampusMemory";
import OperatorWorkspace from "@/pages/OperatorWorkspace";
import StudentWorkBoard from "@/pages/StudentWorkBoard";
import SkillsPassport from "@/pages/SkillsPassport";
import ImpactCenter from "@/pages/ImpactCenter";

function App() {
  return (
    <div className="App">
      <AppProvider>
        <BrowserRouter>
          <Shell>
            <Routes>
              <Route path="/" element={<Today />} />
              <Route path="/decisions" element={<DecisionRoom />} />
              <Route path="/decisions/:caseId" element={<DecisionRoom />} />
              <Route path="/approvals" element={<ApprovalCenter />} />
              <Route path="/suppliers" element={<Supplier360 />} />
              <Route path="/memory" element={<CampusMemory />} />
              <Route path="/operator" element={<OperatorWorkspace />} />
              <Route path="/students" element={<StudentWorkBoard />} />
              <Route path="/passport" element={<SkillsPassport />} />
              <Route path="/impact" element={<ImpactCenter />} />
            </Routes>
          </Shell>
          <Toaster position="top-right" richColors />
        </BrowserRouter>
      </AppProvider>
    </div>
  );
}

export default App;
