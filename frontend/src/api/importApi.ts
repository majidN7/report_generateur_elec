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

export async function importExcelBureauxCentraux(file: File): Promise<ImportReport> {
  const formData = new FormData()
  formData.append("file", file)
  const { data } = await api.post<ImportReport>("/bureaux-centraux/import", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  })
  return data
}
