interface PaginationProps {
  page: number
  pageSize: number
  total: number
  onPageChange: (page: number) => void
}

export function Pagination({ page, pageSize, total, onPageChange }: PaginationProps) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize))

  return (
    <div className="flex items-center justify-between border-t border-slate-200 px-4 py-3 text-sm text-slate-600">
      <span>
        {total === 0 ? "Aucun résultat" : `${(page - 1) * pageSize + 1}–${Math.min(page * pageSize, total)} sur ${total}`}
      </span>
      <div className="flex gap-1">
        <button
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
          className="rounded-md border border-slate-300 px-2.5 py-1 disabled:cursor-not-allowed disabled:opacity-40 hover:not-disabled:bg-slate-50"
        >
          Précédent
        </button>
        <span className="px-2 py-1">
          Page {page} / {totalPages}
        </span>
        <button
          disabled={page >= totalPages}
          onClick={() => onPageChange(page + 1)}
          className="rounded-md border border-slate-300 px-2.5 py-1 disabled:cursor-not-allowed disabled:opacity-40 hover:not-disabled:bg-slate-50"
        >
          Suivant
        </button>
      </div>
    </div>
  )
}
