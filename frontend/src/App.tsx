import { Navigate, Route, Routes } from "react-router-dom"
import { Layout } from "./components/Layout"
import { ToastProvider } from "./components/ToastProvider"
import { BureauxPage } from "./pages/BureauxPage"
import { BureauxCentrauxPage } from "./pages/BureauxCentrauxPage"

export default function App() {
  return (
    <ToastProvider>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Navigate to="/bureaux" replace />} />
          <Route path="/bureaux" element={<BureauxPage />} />
          <Route path="/bureaux-centraux" element={<BureauxCentrauxPage />} />
        </Route>
      </Routes>
    </ToastProvider>
  )
}
