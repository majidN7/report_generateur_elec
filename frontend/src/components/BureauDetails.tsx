import type { BureauVote } from "../api/types"

const ROWS: { label: string; value: (b: BureauVote) => string }[] = [
  { label: "الجماعة", value: (b) => b.commune },
  { label: "رقم مكتب التصويت", value: (b) => b.numero_bureau },
  { label: "عنوان مكتب التصويت", value: (b) => b.adresse_bureau },
  { label: "الرئيس", value: (b) => b.president },
  { label: "نائب الرئيس", value: (b) => b.vice_president },
  { label: "رقم المكتب المركزي", value: (b) => b.numero_bureau_central },
  { label: "رئيس المكتب المركزي", value: (b) => b.president_bureau_central },
  { label: "عنوان المكتب المركزي", value: (b) => b.adresse_bureau_central || b.adresse_bureau },
  { label: "العضو الأول", value: (b) => b.membre_1 },
  { label: "العضو الثاني", value: (b) => b.membre_2 },
  { label: "العضو الثالث", value: (b) => b.membre_3 },
  { label: "نائب العضو الأول", value: (b) => b.suppleant_1 },
  { label: "نائب العضو الثاني", value: (b) => b.suppleant_2 },
  { label: "نائب العضو الثالث", value: (b) => b.suppleant_3 },
]

export function BureauDetails({ bureau }: { bureau: BureauVote }) {
  return (
    <div dir="rtl" className="divide-y divide-slate-100 text-sm">
      {ROWS.map((row) => (
        <div key={row.label} className="flex justify-between gap-4 py-1.5">
          <span className="text-slate-500">{row.label}</span>
          <span className="font-medium text-slate-800">{row.value(bureau)}</span>
        </div>
      ))}
    </div>
  )
}
