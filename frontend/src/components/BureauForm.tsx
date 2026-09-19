import { useState } from "react"
import { extractErrorMessage } from "../api/client"
import type { BureauVote, BureauVoteInput } from "../api/types"

interface BureauFormProps {
  initial?: BureauVote
  onSubmit: (payload: BureauVoteInput) => Promise<void>
  onCancel: () => void
}

const CIN_HINT = "(CIN — requis pour générer le document)"

const FIELDS: { name: keyof BureauVoteInput; label: string; required: boolean }[] = [
  { name: "commune", label: "الجماعة (Commune)", required: true },
  { name: "numero_bureau", label: "رقم مكتب التصويت (N° bureau)", required: true },
  { name: "adresse_bureau", label: "عنوان مكتب التصويت (Adresse)", required: true },
  { name: "president", label: "الرئيس (Président)", required: true },
  { name: "president_cin", label: `رقم البطاقة الوطنية - الرئيس ${CIN_HINT}`, required: false },
  { name: "vice_president", label: "نائب الرئيس (Vice-président)", required: true },
  { name: "vice_president_cin", label: `رقم البطاقة الوطنية - نائب الرئيس ${CIN_HINT}`, required: false },
  { name: "numero_bureau_central", label: "رقم المكتب المركزي (N° bureau central)", required: true },
  { name: "president_bureau_central", label: "رئيس المكتب المركزي (Président bureau central)", required: true },
  { name: "adresse_bureau_central", label: "عنوان المكتب المركزي (optionnel, sinon = adresse du bureau)", required: false },
  { name: "membre_1", label: "عضو أول (Membre 1)", required: true },
  { name: "membre_1_cin", label: `رقم البطاقة الوطنية - العضو الأول ${CIN_HINT}`, required: false },
  { name: "membre_2", label: "عضو ثاني (Membre 2)", required: true },
  { name: "membre_2_cin", label: `رقم البطاقة الوطنية - العضو الثاني ${CIN_HINT}`, required: false },
  { name: "membre_3", label: "كاتب (Membre 3 / Clerc)", required: true },
  { name: "membre_3_cin", label: `رقم البطاقة الوطنية - كاتب ${CIN_HINT}`, required: false },
  { name: "suppleant_1", label: "نائب العضو الأول (Suppléant 1)", required: true },
  { name: "suppleant_1_cin", label: `رقم البطاقة الوطنية - نائب العضو الأول ${CIN_HINT}`, required: false },
  { name: "suppleant_2", label: "نائب العضو الثاني (Suppléant 2)", required: true },
  { name: "suppleant_2_cin", label: `رقم البطاقة الوطنية - نائب العضو الثاني ${CIN_HINT}`, required: false },
  { name: "suppleant_3", label: "نائب الكاتب (Suppléant 3 / Clerc)", required: true },
  { name: "suppleant_3_cin", label: `رقم البطاقة الوطنية - نائب الكاتب ${CIN_HINT}`, required: false },
  { name: "numero_decision", label: "رقم القرار (optionnel)", required: false },
  { name: "date_signature", label: "تاريخ التوقيع (optionnel)", required: false },
]

const NULLABLE_FIELDS: (keyof BureauVoteInput)[] = [
  "adresse_bureau_central",
  "numero_decision",
  "date_signature",
  "president_cin",
  "vice_president_cin",
  "membre_1_cin",
  "membre_2_cin",
  "membre_3_cin",
  "suppleant_1_cin",
  "suppleant_2_cin",
  "suppleant_3_cin",
]

const EMPTY: BureauVoteInput = {
  numero_bureau: "",
  commune: "",
  adresse_bureau: "",
  president: "",
  president_cin: "",
  vice_president: "",
  vice_president_cin: "",
  numero_bureau_central: "",
  president_bureau_central: "",
  adresse_bureau_central: "",
  membre_1: "",
  membre_1_cin: "",
  membre_2: "",
  membre_2_cin: "",
  membre_3: "",
  membre_3_cin: "",
  suppleant_1: "",
  suppleant_1_cin: "",
  suppleant_2: "",
  suppleant_2_cin: "",
  suppleant_3: "",
  suppleant_3_cin: "",
  numero_decision: "",
  date_signature: "",
}

export function BureauForm({ initial, onSubmit, onCancel }: BureauFormProps) {
  const [values, setValues] = useState<BureauVoteInput>(
    initial
      ? {
          numero_bureau: initial.numero_bureau,
          commune: initial.commune,
          adresse_bureau: initial.adresse_bureau,
          president: initial.president,
          president_cin: initial.president_cin ?? "",
          vice_president: initial.vice_president,
          vice_president_cin: initial.vice_president_cin ?? "",
          numero_bureau_central: initial.numero_bureau_central,
          president_bureau_central: initial.president_bureau_central,
          adresse_bureau_central: initial.adresse_bureau_central ?? "",
          membre_1: initial.membre_1,
          membre_1_cin: initial.membre_1_cin ?? "",
          membre_2: initial.membre_2,
          membre_2_cin: initial.membre_2_cin ?? "",
          membre_3: initial.membre_3,
          membre_3_cin: initial.membre_3_cin ?? "",
          suppleant_1: initial.suppleant_1,
          suppleant_1_cin: initial.suppleant_1_cin ?? "",
          suppleant_2: initial.suppleant_2,
          suppleant_2_cin: initial.suppleant_2_cin ?? "",
          suppleant_3: initial.suppleant_3,
          suppleant_3_cin: initial.suppleant_3_cin ?? "",
          numero_decision: initial.numero_decision ?? "",
          date_signature: initial.date_signature ?? "",
        }
      : EMPTY
  )
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function update(name: keyof BureauVoteInput, value: string) {
    setValues((prev) => ({ ...prev, [name]: value }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      const payload = { ...values }
      for (const field of NULLABLE_FIELDS) {
        if (payload[field] === "") payload[field] = null as never
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
