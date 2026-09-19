import { api, downloadBlob, filenameFromContentDisposition } from "./client"
import type { BureauVote, BureauVoteInput, BureauVotePage } from "./types"

export interface ListParams {
  page?: number
  page_size?: number
  search?: string
  commune?: string
  sort_by?: string
  sort_dir?: "asc" | "desc"
}

export async function listBureaux(params: ListParams): Promise<BureauVotePage> {
  const { data } = await api.get<BureauVotePage>("/bureaux", { params })
  return data
}

export async function listCommunes(): Promise<string[]> {
  const { data } = await api.get<string[]>("/bureaux/communes")
  return data
}

export async function getBureau(id: number): Promise<BureauVote> {
  const { data } = await api.get<BureauVote>(`/bureaux/${id}`)
  return data
}

export async function createBureau(payload: BureauVoteInput): Promise<BureauVote> {
  const { data } = await api.post<BureauVote>("/bureaux", payload)
  return data
}

export async function updateBureau(id: number, payload: Partial<BureauVoteInput>): Promise<BureauVote> {
  const { data } = await api.put<BureauVote>(`/bureaux/${id}`, payload)
  return data
}

export async function deleteBureau(id: number): Promise<void> {
  await api.delete(`/bureaux/${id}`)
}

export async function deleteAllBureaux(): Promise<number> {
  const { data } = await api.delete<{ deleted: number }>("/bureaux/all")
  return data.deleted
}

export async function downloadBureauDocument(bureau: BureauVote, format: "docx" | "pdf") {
  const response = await api.get(`/bureaux/${bureau.id}/document`, {
    params: { format },
    responseType: "blob",
  })
  const filename = filenameFromContentDisposition(
    response.headers["content-disposition"],
    `arrete_${bureau.numero_bureau}.${format}`
  )
  downloadBlob(response.data, filename)
}

export async function generateBatch(format: "docx" | "pdf", ids?: number[]) {
  const response = await api.post(
    "/bureaux/generate-batch",
    null,
    {
      params: { format, ids: ids && ids.length ? ids.join(",") : undefined },
      responseType: "blob",
    }
  )
  const filename = filenameFromContentDisposition(
    response.headers["content-disposition"],
    "arretes_bureaux_vote.zip"
  )
  downloadBlob(response.data, filename)
}
