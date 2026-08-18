import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import { Toaster } from "@/components/ui/sonner"
import DashboardLayout from "@/layouts/DashboardLayout"
import Dashboard from "@/pages/Dashboard"
import Campaigns from "@/pages/Campaigns"
import CampaignEditor from "@/pages/CampaignEditor"
import Subscribers from "@/pages/Subscribers"

function App() {
  return (
    <Router>
      <Toaster />
      <Routes>
        <Route element={<DashboardLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/campaigns" element={<Campaigns />} />
          <Route path="/campaigns/new" element={<CampaignEditor />} />
          <Route path="/subscribers" element={<Subscribers />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App
