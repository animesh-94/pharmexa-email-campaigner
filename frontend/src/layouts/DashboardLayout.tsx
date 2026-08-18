import { Link, Outlet } from "react-router-dom"
import { Mail, Users, LayoutDashboard, Settings } from "lucide-react"

export default function DashboardLayout() {
  return (
    <div className="flex h-screen bg-slate-100">
      <aside className="w-64 bg-slate-900 text-white flex flex-col h-full shadow-lg">
        <div className="h-16 flex items-center px-6 font-bold text-xl tracking-wide border-b border-slate-800">
          <Mail className="mr-2" /> EmailCamp
        </div>
        <nav className="flex-1 px-4 py-6 space-y-2">
          <Link to="/" className="flex items-center px-4 py-2 rounded transition hover:bg-slate-800">
            <LayoutDashboard className="mr-3 h-5 w-5" /> Dashboard
          </Link>
          <Link to="/campaigns" className="flex items-center px-4 py-2 rounded transition hover:bg-slate-800">
            <Mail className="mr-3 h-5 w-5" /> Campaigns
          </Link>
          <Link to="/subscribers" className="flex items-center px-4 py-2 rounded transition hover:bg-slate-800">
            <Users className="mr-3 h-5 w-5" /> Subscribers
          </Link>
        </nav>
        <div className="p-4 text-xs text-slate-500 border-t border-slate-800 flex items-center">
          <Settings className="mr-2 h-4 w-4" /> v1.0.0 Internal
        </div>
      </aside>

      <main className="flex-1 flex flex-col h-full overflow-hidden">
        <div className="flex-1 overflow-y-auto p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
