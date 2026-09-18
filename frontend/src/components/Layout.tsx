import { NavLink, Outlet } from "react-router-dom"

const linkClass = ({ isActive }: { isActive: boolean }) =>
  `rounded-md px-3 py-2 text-sm font-medium ${
    isActive ? "bg-blue-600 text-white" : "text-slate-600 hover:bg-slate-100"
  }`

export function Layout() {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
          <h1 className="text-lg font-semibold text-slate-800">
            Gestion des Bureaux de Vote — Élections 2026
          </h1>
          <nav className="flex gap-1">
            <NavLink to="/bureaux" className={linkClass}>
              Bureaux de vote
            </NavLink>
            <NavLink to="/bureaux-centraux" className={linkClass}>
              Bureaux centraux
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  )
}
