import { useEffect, useState } from "react"
import {
  createBureau,
  deleteBureau,
  downloadBureauDocument,
  generateBatch,
  listBureaux,
  listCommunes,
  updateBureau,
} from "../api/bureaux"
import { extractErrorMessage } from "../api/client"
import type { BureauVote, BureauVoteInput } from "../api/types"
import { BureauDetails } from "../components/BureauDetails"
import { BureauForm } from "../components/BureauForm"
import { ConfirmDialog } from "../components/ConfirmDialog"
import { ImportModal } from "../components/ImportModal"
import { Modal } from "../components/Modal"
import { Pagination } from "../components/Pagination"
import { useToast } from "../components/ToastProvider"

const PAGE_SIZE = 15

export function BureauxPage() {
  const { showToast } = useToast()

  const [items, setItems] = useState<BureauVote[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState("")
  const [commune, setCommune] = useState("")
  const [communes, setCommunes] = useState<string[]>([])
  const [sortBy, setSortBy] = useState("created_at")
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc")
  const [loading, setLoading] = useState(false)

  const [showImport, setShowImport] = useState(false)
  const [editing, setEditing] = useState<BureauVote | "new" | null>(null)
  const [viewing, setViewing] = useState<BureauVote | null>(null)
  const [deleting, setDeleting] = useState<BureauVote | null>(null)
  const [generating, setGenerating] = useState(false)

  async function load() {
    setLoading(true)
    try {
      const data = await listBureaux({
        page,
        page_size: PAGE_SIZE,
        search: search || undefined,
        commune: commune || undefined,
        sort_by: sortBy,
        sort_dir: sortDir,
      })
      setItems(data.items)
      setTotal(data.total)
    } catch (err) {
      showToast(extractErrorMessage(err), "error")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, search, commune, sortBy, sortDir])

  useEffect(() => {
    listCommunes().then(setCommunes).catch(() => undefined)
  }, [])

  function toggleSort(field: string) {
    if (sortBy === field) {
      setSortDir(sortDir === "asc" ? "desc" : "asc")
    } else {
      setSortBy(field)
      setSortDir("asc")
    }
  }

  async function handleSave(payload: BureauVoteInput) {
    if (editing === "new") {
      await createBureau(payload)
      showToast("Bureau de vote créé avec succès")
    } else if (editing) {
      await updateBureau(editing.id, payload)
      showToast("Bureau de vote mis à jour")
    }
    setEditing(null)
    setPage(1)
    load()
    listCommunes().then(setCommunes).catch(() => undefined)
  }

  async function handleDelete() {
    if (!deleting) return
    try {
      await deleteBureau(deleting.id)
      showToast("Bureau de vote supprimé")
      setDeleting(null)
      load()
    } catch (err) {
      showToast(extractErrorMessage(err), "error")
    }
  }

  async function handleDownload(bureau: BureauVote, format: "docx" | "pdf") {
    try {
      await downloadBureauDocument(bureau, format)
    } catch (err) {
      showToast(extractErrorMessage(err), "error")
    }
  }

  async function handleBatch(format: "docx" | "pdf") {
    setGenerating(true)
    try {
      await generateBatch(format)
      showToast("Archive générée avec succès")
    } catch (err) {
      showToast(extractErrorMessage(err), "error")
    } finally {
      setGenerating(false)
    }
  }

  const sortIndicator = (field: string) => (sortBy === field ? (sortDir === "asc" ? " ▲" : " ▼") : "")

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-semibold text-slate-800">Bureaux de vote</h2>
          <p className="text-sm text-slate-500">{total} bureau(x) enregistré(s)</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setShowImport(true)}
            className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50"
          >
            Importer Excel
          </button>
          <button
            onClick={() => handleBatch("docx")}
            disabled={generating}
            className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50 disabled:opacity-50"
          >
            Générer tout (Word)
          </button>
          <button
            onClick={() => handleBatch("pdf")}
            disabled={generating}
            className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50 disabled:opacity-50"
          >
            Générer tout (PDF)
          </button>
          <button
            onClick={() => setEditing("new")}
            className="rounded-md bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700"
          >
            + Ajouter un bureau
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 rounded-lg bg-white p-3 shadow-sm">
        <input
          type="text"
          placeholder="Rechercher (nom, adresse, numéro...)"
          value={search}
          onChange={(e) => {
            setPage(1)
            setSearch(e.target.value)
          }}
          className="min-w-64 flex-1 rounded-md border border-slate-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none"
        />
        <select
          value={commune}
          onChange={(e) => {
            setPage(1)
            setCommune(e.target.value)
          }}
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none"
        >
          <option value="">Toutes les communes</option>
          {communes.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>

      <div className="overflow-x-auto rounded-lg bg-white shadow-sm">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50 text-right text-slate-600">
              <th className="cursor-pointer px-3 py-2" onClick={() => toggleSort("numero_bureau")}>
                رقم المكتب{sortIndicator("numero_bureau")}
              </th>
              <th className="cursor-pointer px-3 py-2" onClick={() => toggleSort("commune")}>
                الجماعة{sortIndicator("commune")}
              </th>
              <th className="cursor-pointer px-3 py-2" onClick={() => toggleSort("president")}>
                الرئيس{sortIndicator("president")}
              </th>
              <th className="px-3 py-2">المكتب المركزي</th>
              <th className="px-3 py-2 text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={5} className="px-3 py-6 text-center text-slate-400">
                  Chargement...
                </td>
              </tr>
            )}
            {!loading && items.length === 0 && (
              <tr>
                <td colSpan={5} className="px-3 py-6 text-center text-slate-400">
                  Aucun bureau de vote. Importez un fichier Excel ou ajoutez-en un manuellement.
                </td>
              </tr>
            )}
            {!loading &&
              items.map((bureau) => (
                <tr key={bureau.id} className="border-b border-slate-100 text-right hover:bg-slate-50">
                  <td className="px-3 py-2 font-medium">{bureau.numero_bureau}</td>
                  <td className="px-3 py-2">{bureau.commune}</td>
                  <td className="px-3 py-2">{bureau.president}</td>
                  <td className="px-3 py-2">{bureau.numero_bureau_central}</td>
                  <td className="px-3 py-2 text-left">
                    <div className="flex flex-wrap justify-end gap-1 text-xs">
                      <button
                        onClick={() => setViewing(bureau)}
                        className="rounded border border-slate-300 px-2 py-1 hover:bg-slate-100"
                      >
                        Voir
                      </button>
                      <button
                        onClick={() => setEditing(bureau)}
                        className="rounded border border-slate-300 px-2 py-1 hover:bg-slate-100"
                      >
                        Modifier
                      </button>
                      <button
                        onClick={() => handleDownload(bureau, "docx")}
                        className="rounded border border-blue-300 px-2 py-1 text-blue-700 hover:bg-blue-50"
                      >
                        Word
                      </button>
                      <button
                        onClick={() => handleDownload(bureau, "pdf")}
                        className="rounded border border-blue-300 px-2 py-1 text-blue-700 hover:bg-blue-50"
                      >
                        PDF
                      </button>
                      <button
                        onClick={() => setDeleting(bureau)}
                        className="rounded border border-red-300 px-2 py-1 text-red-700 hover:bg-red-50"
                      >
                        Supprimer
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
        <Pagination page={page} pageSize={PAGE_SIZE} total={total} onPageChange={setPage} />
      </div>

      {showImport && (
        <ImportModal
          onClose={() => setShowImport(false)}
          onImported={() => {
            setPage(1)
            load()
            listCommunes().then(setCommunes).catch(() => undefined)
          }}
        />
      )}

      {editing && (
        <Modal title={editing === "new" ? "Ajouter un bureau de vote" : "Modifier le bureau de vote"} onClose={() => setEditing(null)} wide>
          <BureauForm
            initial={editing === "new" ? undefined : editing}
            onSubmit={handleSave}
            onCancel={() => setEditing(null)}
          />
        </Modal>
      )}

      {viewing && (
        <Modal title={`Bureau de vote n° ${viewing.numero_bureau}`} onClose={() => setViewing(null)} wide>
          <BureauDetails bureau={viewing} />
        </Modal>
      )}

      {deleting && (
        <ConfirmDialog
          message={`Supprimer le bureau de vote n° ${deleting.numero_bureau} (${deleting.commune}) ? Cette action est irréversible.`}
          onConfirm={handleDelete}
          onCancel={() => setDeleting(null)}
        />
      )}
    </div>
  )
}
