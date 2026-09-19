import { useEffect, useState } from "react"
import {
  createBureauCentral,
  deleteBureauCentral,
  downloadBureauCentralDocument,
  generateBatchCentraux,
  listBureauxCentraux,
  updateBureauCentral,
} from "../api/bureauxCentraux"
import { extractErrorMessage } from "../api/client"
import { importExcelBureauxCentraux } from "../api/importApi"
import type { BureauCentral, BureauCentralInput } from "../api/types"
import { BureauCentralDetails } from "../components/BureauCentralDetails"
import { BureauCentralForm } from "../components/BureauCentralForm"
import { ConfirmDialog } from "../components/ConfirmDialog"
import { ImportModal } from "../components/ImportModal"
import { Modal } from "../components/Modal"
import { Pagination } from "../components/Pagination"
import { useToast } from "../components/ToastProvider"

const PAGE_SIZE = 15

function isComplete(b: BureauCentral): boolean {
  return Boolean(
    b.adresse_bureau_central &&
      b.vice_president_bureau_central &&
      b.membre_central_1 &&
      b.membre_central_2 &&
      b.membre_central_3 &&
      b.suppleant_central_1 &&
      b.suppleant_central_2 &&
      b.suppleant_central_3 &&
      b.president_cin &&
      b.vice_president_cin &&
      b.membre_central_1_cin &&
      b.membre_central_2_cin &&
      b.membre_central_3_cin &&
      b.suppleant_central_1_cin &&
      b.suppleant_central_2_cin &&
      b.suppleant_central_3_cin
  )
}

export function BureauxCentrauxPage() {
  const { showToast } = useToast()

  const [items, setItems] = useState<BureauCentral[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState("")
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [showImport, setShowImport] = useState(false)

  const [editing, setEditing] = useState<BureauCentral | "new" | null>(null)
  const [viewing, setViewing] = useState<BureauCentral | null>(null)
  const [deleting, setDeleting] = useState<BureauCentral | null>(null)

  async function load() {
    setLoading(true)
    try {
      const data = await listBureauxCentraux({ page, page_size: PAGE_SIZE, search: search || undefined })
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
  }, [page, search])

  async function handleSave(payload: BureauCentralInput) {
    if (editing === "new") {
      await createBureauCentral(payload)
      showToast("Bureau central créé avec succès")
    } else if (editing) {
      await updateBureauCentral(editing.id, payload)
      showToast("Bureau central mis à jour")
    }
    setEditing(null)
    setPage(1)
    load()
  }

  async function handleDelete() {
    if (!deleting) return
    try {
      await deleteBureauCentral(deleting.id)
      showToast("Bureau central supprimé")
      setDeleting(null)
      load()
    } catch (err) {
      showToast(extractErrorMessage(err), "error")
    }
  }

  async function handleDownload(bureau: BureauCentral, format: "docx" | "pdf") {
    try {
      await downloadBureauCentralDocument(bureau, format)
    } catch (err) {
      showToast(extractErrorMessage(err), "error")
    }
  }

  async function handleBatch(format: "docx" | "pdf") {
    setGenerating(true)
    try {
      await generateBatchCentraux(format)
      showToast("Archive générée (les bureaux incomplets sont ignorés)")
    } catch (err) {
      showToast(extractErrorMessage(err), "error")
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-semibold text-slate-800">Bureaux centraux</h2>
          <p className="text-sm text-slate-500">
            {total} bureau(x) central(aux) — importés ou créés automatiquement lors de l'import des bureaux de
            vote, à compléter avant génération
          </p>
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
            + Ajouter un bureau central
          </button>
        </div>
      </div>

      <div className="rounded-lg bg-white p-3 shadow-sm">
        <input
          type="text"
          placeholder="Rechercher (commune, président, numéro...)"
          value={search}
          onChange={(e) => {
            setPage(1)
            setSearch(e.target.value)
          }}
          className="w-full max-w-md rounded-md border border-slate-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none"
        />
      </div>

      <div className="overflow-x-auto rounded-lg bg-white shadow-sm">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50 text-right text-slate-600">
              <th className="px-3 py-2">رقم المكتب المركزي</th>
              <th className="px-3 py-2">الجماعة</th>
              <th className="px-3 py-2">رئيس المكتب المركزي</th>
              <th className="px-3 py-2">Statut</th>
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
                  Aucun bureau central. Importez d'abord un fichier Excel de bureaux de vote.
                </td>
              </tr>
            )}
            {!loading &&
              items.map((bureau) => (
                <tr key={bureau.id} className="border-b border-slate-100 text-right hover:bg-slate-50">
                  <td className="px-3 py-2 font-medium">{bureau.numero_bureau_central}</td>
                  <td className="px-3 py-2">{bureau.commune}</td>
                  <td className="px-3 py-2">{bureau.president_bureau_central}</td>
                  <td className="px-3 py-2">
                    {isComplete(bureau) ? (
                      <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs text-emerald-700">
                        Complet
                      </span>
                    ) : (
                      <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs text-amber-700">
                        À compléter
                      </span>
                    )}
                  </td>
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
                        disabled={!isComplete(bureau)}
                        className="rounded border border-blue-300 px-2 py-1 text-blue-700 hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-40"
                      >
                        Word
                      </button>
                      <button
                        onClick={() => handleDownload(bureau, "pdf")}
                        disabled={!isComplete(bureau)}
                        className="rounded border border-blue-300 px-2 py-1 text-blue-700 hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-40"
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
          title="Importer le fichier Excel des bureaux centraux"
          description={
            'Sélectionnez le fichier Excel dédié aux bureaux centraux (feuille "Bureaux_Centraux"), avec ' +
            "les colonnes : الجماعة, رقم المكتب المركزي, رئيس المكتب المركزي, عنوان المكتب المركزي, " +
            "نائب رئيس المكتب المركزي, أعضاء et نواب. Les 3 premières colonnes sont obligatoires ; les " +
            "autres complètent ou mettent à jour une fiche existante."
          }
          importFn={importExcelBureauxCentraux}
          onClose={() => setShowImport(false)}
          onImported={() => {
            setPage(1)
            load()
          }}
        />
      )}

      {editing && (
        <Modal
          title={editing === "new" ? "Ajouter un bureau central" : "Compléter le bureau central"}
          onClose={() => setEditing(null)}
          wide
        >
          <BureauCentralForm
            initial={editing === "new" ? undefined : editing}
            onSubmit={handleSave}
            onCancel={() => setEditing(null)}
          />
        </Modal>
      )}

      {viewing && (
        <Modal title={`Bureau central n° ${viewing.numero_bureau_central}`} onClose={() => setViewing(null)} wide>
          <BureauCentralDetails bureau={viewing} />
        </Modal>
      )}

      {deleting && (
        <ConfirmDialog
          message={`Supprimer le bureau central n° ${deleting.numero_bureau_central} (${deleting.commune}) ? Cette action est irréversible.`}
          onConfirm={handleDelete}
          onCancel={() => setDeleting(null)}
        />
      )}
    </div>
  )
}
