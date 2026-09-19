import type { BureauCentral } from "../api/types"

const ROWS: { label: string; value: (b: BureauCentral) => string }[] = [
  { label: "الجماعة", value: (b) => b.commune },
  { label: "رقم المكتب المركزي", value: (b) => b.numero_bureau_central },
  { label: "رئيس المكتب المركزي", value: (b) => b.president_bureau_central },
  { label: "رقم البطاقة الوطنية - الرئيس", value: (b) => b.president_cin || "—" },
  { label: "عنوان المكتب المركزي", value: (b) => b.adresse_bureau_central || "—" },
  { label: "نائب رئيس المكتب المركزي", value: (b) => b.vice_president_bureau_central || "—" },
  { label: "رقم البطاقة الوطنية - نائب الرئيس", value: (b) => b.vice_president_cin || "—" },
  { label: "عضو أول", value: (b) => b.membre_central_1 || "—" },
  { label: "رقم البطاقة الوطنية - عضو أول", value: (b) => b.membre_central_1_cin || "—" },
  { label: "عضو ثاني", value: (b) => b.membre_central_2 || "—" },
  { label: "رقم البطاقة الوطنية - عضو ثاني", value: (b) => b.membre_central_2_cin || "—" },
  { label: "كاتب", value: (b) => b.membre_central_3 || "—" },
  { label: "رقم البطاقة الوطنية - كاتب", value: (b) => b.membre_central_3_cin || "—" },
  { label: "نائب العضو الأول", value: (b) => b.suppleant_central_1 || "—" },
  { label: "رقم البطاقة الوطنية - نائب العضو الأول", value: (b) => b.suppleant_central_1_cin || "—" },
  { label: "نائب العضو الثاني", value: (b) => b.suppleant_central_2 || "—" },
  { label: "رقم البطاقة الوطنية - نائب العضو الثاني", value: (b) => b.suppleant_central_2_cin || "—" },
  { label: "نائب الكاتب", value: (b) => b.suppleant_central_3 || "—" },
  { label: "رقم البطاقة الوطنية - نائب الكاتب", value: (b) => b.suppleant_central_3_cin || "—" },
]

export function BureauCentralDetails({ bureau }: { bureau: BureauCentral }) {
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
