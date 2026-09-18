import { api, downloadBlob, filenameFromContentDisposition } from "./client"
import type { BureauCentral, BureauCentralInput, BureauCentralPage } from "./types"
import type { ListParams } from "./bureaux"

export async function listBureauxCentraux(params: ListParams): Promise<BureauCentralPage> {
  const { data } = await api.get<BureauCentralPage>("/bureaux-centraux", { params })
  return data
}

export async function getBureauCentral(id: number): Promise<BureauCentral> {
  const { data } = await api.get<BureauCentral>(`/bureaux-centraux/${id}`)
  return data
}

export async function createBureauCentral(payload: BureauCentralInput): Promise<BureauCentral> {
  const { data } = await api.post<BureauCentral>("/bureaux-centraux", payload)
  return data
}

export async function updateBureauCentral(
  id: number,
  payload: Partial<BureauCentralInput>
): Promise<BureauCentral> {
  const { data } = await api.put<BureauCentral>(`/bureaux-centraux/${id}`, payload)
  return data
}

export async function deleteBureauCentral(id: number): Promise<void> {
  await api.delete(`/bureaux-centraux/${id}`)
}

export async function downloadBureauCentralDocument(bureau: BureauCentral, format: "docx" | "pdf") {
  const response = await api.get(`/bureaux-centraux/${bureau.id}/document`, {
    params: { format },
    responseType: "blob",
  })
  const filename = filenameFromContentDisposition(
    response.headers["content-disposition"],
    `arrete_central_${bureau.numero_bureau_central}.${format}`
  )
  downloadBlob(response.data, filename)
}

export async function generateBatchCentraux(format: "docx" | "pdf", ids?: number[]) {
  const response = await api.post(
    "/bureaux-centraux/generate-batch",
    null,
    {
      params: { format, ids: ids && ids.length ? ids.join(",") : undefined },
      responseType: "blob",
    }
  )
  const filename = filenameFromContentDisposition(
    response.headers["content-disposition"],
    "arretes_bureaux_centraux.zip"
  )
  downloadBlob(response.data, filename)
}
