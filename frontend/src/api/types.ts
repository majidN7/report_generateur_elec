export interface BureauVote {
  id: number
  numero_bureau: string
  commune: string
  adresse_bureau: string
  president: string
  president_cin: string | null
  vice_president: string
  vice_president_cin: string | null
  numero_bureau_central: string | null
  president_bureau_central: string | null
  adresse_bureau_central: string | null
  membre_1: string
  membre_1_cin: string | null
  membre_2: string
  membre_2_cin: string | null
  membre_3: string
  membre_3_cin: string | null
  suppleant_1: string
  suppleant_1_cin: string | null
  suppleant_2: string
  suppleant_2_cin: string | null
  suppleant_3: string
  suppleant_3_cin: string | null
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
  president_cin: string | null
  adresse_bureau_central: string | null
  vice_president_bureau_central: string | null
  vice_president_cin: string | null
  membre_central_1: string | null
  membre_central_1_cin: string | null
  membre_central_2: string | null
  membre_central_2_cin: string | null
  membre_central_3: string | null
  membre_central_3_cin: string | null
  suppleant_central_1: string | null
  suppleant_central_1_cin: string | null
  suppleant_central_2: string | null
  suppleant_central_2_cin: string | null
  suppleant_central_3: string | null
  suppleant_central_3_cin: string | null
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
