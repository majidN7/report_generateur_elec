import { api } from "./client"
import type { ImportReport } from "./types"

export async function importExcelFile(file: File): Promise<ImportReport> {
  const formData = new FormData()
  formData.append("file", file)
  const { data } = await api.post<ImportReport>("/import/excel", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  })
  return data
}
