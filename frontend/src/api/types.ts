export interface BureauVote {
  id: number
  numero_bureau: string
  commune: string
  adresse_bureau: string
  president: string
  vice_president: string
  numero_bureau_central: string
  president_bureau_central: string
  adresse_bureau_central: string | null
  membre_1: string
  membre_2: string
  membre_3: string
  suppleant_1: string
  suppleant_2: string
  suppleant_3: string
  numero_decision: string | null
  date_signature: string | null
  created_at: string
  updated_at: string
}

export type BureauVoteInput = Omit<BureauVote, "id" | "created_at" | "updated_at">

export interface BureauVotePage {
  items: BureauVote[]
  total: number
  page: number
  page_size: number
}

export interface BureauCentral {
  id: number
  numero_bureau_central: string
  commune: string
  president_bureau_central: string
  adresse_bureau_central: string | null
  vice_president_bureau_central: string | null
  membre_central_1: string | null
  membre_central_2: string | null
  membre_central_3: string | null
  suppleant_central_1: string | null
  suppleant_central_2: string | null
  suppleant_central_3: string | null
  numero_decision: string | null
  date_signature: string | null
  created_at: string
  updated_at: string
}

export type BureauCentralInput = Omit<BureauCentral, "id" | "created_at" | "updated_at">

export interface BureauCentralPage {
  items: BureauCentral[]
  total: number
  page: number
  page_size: number
}

export interface ImportRowError {
  row: number
  message: string
}

export interface ImportReport {
  total_rows: number
  created: number
  updated: number
  skipped_duplicates: number
  errors: ImportRowError[]
  bureaux_centraux_created: number
}
