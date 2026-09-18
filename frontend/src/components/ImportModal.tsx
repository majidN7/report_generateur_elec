import { useRef, useState } from "react"
import { importExcelFile } from "../api/importApi"
import { extractErrorMessage } from "../api/client"
import type { ImportReport } from "../api/types"
import { Modal } from "./Modal"

interface ImportModalProps {
  onClose: () => void
  onImported: () => void
}

export function ImportModal({ onClose, onImported }: ImportModalProps) {
  const fileInput = useRef<HTMLInputElement>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [report, setReport] = useState<ImportReport | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const file = fileInput.current?.files?.[0]
    if (!file) {
      setError("Veuillez choisir un fichier Excel (.xlsx)")
      return
    }
    setLoading(true)
    setError(null)
    try {
      const result = await importExcelFile(file)
      setReport(result)
      onImported()
    } catch (err) {
      setError(extractErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal title="Importer le fichier Excel" onClose={onClose}>
      {!report ? (
        <form onSubmit={handleSubmit} className="space-y-4">
          <p className="text-sm text-slate-600">
            Sélectionnez le fichier Excel contenant la feuille "Donnees_Fusion" avec les colonnes
            الرئيس, نائب الرئيس, رقم مكتب التصويت, الجماعة, عنوان مكتب التصويت, رقم المكتب المركزي,
            رئيس المكتب المركزي, أعضاء et نواب.
          </p>
          <input
            ref={fileInput}
            type="file"
            accept=".xlsx,.xlsm"
            className="block w-full text-sm text-slate-600 file:mr-3 file:rounded-md file:border-0 file:bg-blue-50 file:px-3 file:py-2 file:text-sm file:font-medium file:text-blue-700 hover:file:bg-blue-100"
          />
          {error && <p className="text-sm text-red-600">{error}</p>}
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={loading}
              className="rounded-md bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? "Importation..." : "Importer"}
            </button>
          </div>
        </form>
      ) : (
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="rounded-md bg-slate-50 p-2">
              Lignes lues : <strong>{report.total_rows}</strong>
            </div>
            <div className="rounded-md bg-emerald-50 p-2">
              Créés : <strong>{report.created}</strong>
            </div>
            <div className="rounded-md bg-blue-50 p-2">
              Mis à jour : <strong>{report.updated}</strong>
            </div>
            <div className="rounded-md bg-amber-50 p-2">
              Doublons ignorés : <strong>{report.skipped_duplicates}</strong>
            </div>
            <div className="col-span-2 rounded-md bg-slate-50 p-2">
              Bureaux centraux créés (à compléter) : <strong>{report.bureaux_centraux_created}</strong>
            </div>
          </div>
          {report.errors.length > 0 && (
            <div className="max-h-40 overflow-y-auto rounded-md border border-red-200 bg-red-50 p-2 text-sm text-red-700">
              <p className="mb-1 font-medium">{report.errors.length} ligne(s) en erreur :</p>
              <ul className="list-disc space-y-0.5 pl-5">
                {report.errors.map((e) => (
                  <li key={e.row}>
                    Ligne {e.row} : {e.message}
                  </li>
                ))}
              </ul>
            </div>
          )}
          <div className="flex justify-end">
            <button
              onClick={onClose}
              className="rounded-md bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700"
            >
              Fermer
            </button>
          </div>
        </div>
      )}
    </Modal>
  )
}
