import type { BureauVote } from "../api/types"

const ROWS: { label: string; value: (b: BureauVote) => string }[] = [
  { label: "الجماعة", value: (b) => b.commune },
  { label: "رقم مكتب التصويت", value: (b) => b.numero_bureau },
  { label: "عنوان مكتب التصويت", value: (b) => b.adresse_bureau },
  { label: "الرئيس", value: (b) => b.president },
  { label: "رقم البطاقة الوطنية - الرئيس", value: (b) => b.president_cin || "—" },
  { label: "نائب الرئيس", value: (b) => b.vice_president },
  { label: "رقم البطاقة الوطنية - نائب الرئيس", value: (b) => b.vice_president_cin || "—" },
  { label: "رئيس المكتب المركزي", value: (b) => b.president_bureau_central || "—" },
  { label: "عضو أول", value: (b) => b.membre_1 },
  { label: "رقم البطاقة الوطنية - عضو أول", value: (b) => b.membre_1_cin || "—" },
  { label: "عضو ثاني", value: (b) => b.membre_2 },
  { label: "رقم البطاقة الوطنية - عضو ثاني", value: (b) => b.membre_2_cin || "—" },
  { label: "كاتب", value: (b) => b.membre_3 },
  { label: "رقم البطاقة الوطنية - كاتب", value: (b) => b.membre_3_cin || "—" },
  { label: "نائب العضو الأول", value: (b) => b.suppleant_1 },
  { label: "رقم البطاقة الوطنية - نائب العضو الأول", value: (b) => b.suppleant_1_cin || "—" },
  { label: "نائب العضو الثاني", value: (b) => b.suppleant_2 },
  { label: "رقم البطاقة الوطنية - نائب العضو الثاني", value: (b) => b.suppleant_2_cin || "—" },
  { label: "نائب الكاتب", value: (b) => b.suppleant_3 },
  { label: "رقم البطاقة الوطنية - نائب الكاتب", value: (b) => b.suppleant_3_cin || "—" },
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
