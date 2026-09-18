import { useState } from "react"
import { extractErrorMessage } from "../api/client"
import type { BureauCentral, BureauCentralInput } from "../api/types"

interface BureauCentralFormProps {
  initial?: BureauCentral
  onSubmit: (payload: BureauCentralInput) => Promise<void>
  onCancel: () => void
}

const FIELDS: { name: keyof BureauCentralInput; label: string; required: boolean }[] = [
  { name: "commune", label: "الجماعة (Commune)", required: true },
  { name: "numero_bureau_central", label: "رقم المكتب المركزي (N° bureau central)", required: true },
  { name: "president_bureau_central", label: "رئيس المكتب المركزي (Président)", required: true },
  { name: "adresse_bureau_central", label: "عنوان المكتب المركزي (Adresse)", required: false },
  { name: "vice_president_bureau_central", label: "نائب رئيس المكتب المركزي (Vice-président)", required: false },
  { name: "membre_central_1", label: "العضو الأول (Membre 1)", required: false },
  { name: "membre_central_2", label: "العضو الثاني (Membre 2)", required: false },
  { name: "membre_central_3", label: "العضو الثالث (Membre 3)", required: false },
  { name: "suppleant_central_1", label: "نائب العضو الأول (Suppléant 1)", required: false },
  { name: "suppleant_central_2", label: "نائب العضو الثاني (Suppléant 2)", required: false },
  { name: "suppleant_central_3", label: "نائب العضو الثالث (Suppléant 3)", required: false },
  { name: "numero_decision", label: "رقم القرار (optionnel)", required: false },
  { name: "date_signature", label: "تاريخ التوقيع (optionnel)", required: false },
]

const EMPTY: BureauCentralInput = {
  numero_bureau_central: "",
  commune: "",
  president_bureau_central: "",
  adresse_bureau_central: "",
  vice_president_bureau_central: "",
  membre_central_1: "",
  membre_central_2: "",
  membre_central_3: "",
  suppleant_central_1: "",
  suppleant_central_2: "",
  suppleant_central_3: "",
  numero_decision: "",
  date_signature: "",
}

export function BureauCentralForm({ initial, onSubmit, onCancel }: BureauCentralFormProps) {
  const [values, setValues] = useState<BureauCentralInput>(
    initial
      ? {
          numero_bureau_central: initial.numero_bureau_central,
          commune: initial.commune,
          president_bureau_central: initial.president_bureau_central,
          adresse_bureau_central: initial.adresse_bureau_central ?? "",
          vice_president_bureau_central: initial.vice_president_bureau_central ?? "",
          membre_central_1: initial.membre_central_1 ?? "",
          membre_central_2: initial.membre_central_2 ?? "",
          membre_central_3: initial.membre_central_3 ?? "",
          suppleant_central_1: initial.suppleant_central_1 ?? "",
          suppleant_central_2: initial.suppleant_central_2 ?? "",
          suppleant_central_3: initial.suppleant_central_3 ?? "",
          numero_decision: initial.numero_decision ?? "",
          date_signature: initial.date_signature ?? "",
        }
      : EMPTY
  )
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function update(name: keyof BureauCentralInput, value: string) {
    setValues((prev) => ({ ...prev, [name]: value }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      const payload: BureauCentralInput = { ...values }
      for (const key of Object.keys(payload) as (keyof BureauCentralInput)[]) {
        if (payload[key] === "") payload[key] = null as never
      }
      await onSubmit(payload)
    } catch (err) {
      setError(extractErrorMessage(err))
      setSaving(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3" dir="rtl">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {FIELDS.map((field) => (
          <label key={field.name} className="block text-sm">
            <span className="mb-1 block text-slate-600">{field.label}</span>
            <input
              type="text"
              value={values[field.name] ?? ""}
              required={field.required}
              onChange={(e) => update(field.name, e.target.value)}
              className="w-full rounded-md border border-slate-300 px-2.5 py-1.5 text-right focus:border-blue-500 focus:outline-none"
            />
          </label>
        ))}
      </div>
      {error && (
        <p className="text-sm text-red-600" dir="ltr">
          {error}
        </p>
      )}
      <div className="flex justify-end gap-2" dir="ltr">
        <button
          type="button"
          onClick={onCancel}
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50"
        >
          Annuler
        </button>
        <button
          type="submit"
          disabled={saving}
          className="rounded-md bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {saving ? "Enregistrement..." : "Enregistrer"}
        </button>
      </div>
    </form>
  )
}
