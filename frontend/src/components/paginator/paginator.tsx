import './styles.css';

interface PaginatorProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

const PAGINATOR_SIZE = 10;
const PAGINATOR_SECTION_CALCULATOR = 9;

function Paginator({ currentPage, totalPages, onPageChange }: PaginatorProps) {
  const sectionStart =
    Math.floor((currentPage - 1) / PAGINATOR_SIZE) * PAGINATOR_SIZE + 1;
  const sectionEnd = Math.min(
    sectionStart + PAGINATOR_SECTION_CALCULATOR,
    totalPages,
  );

  const prevPage = sectionStart - PAGINATOR_SIZE;
  const nextPage = sectionStart + PAGINATOR_SIZE;

  const pages: number[] = [];
  for (let i = sectionStart; i <= sectionEnd; i++) {
    pages.push(i);
  }

  return (
    <div className="paginator">
      <button
        className="paginator__btn"
        disabled={prevPage < 1}
        onClick={() => onPageChange(prevPage)}
      >
        Previous
      </button>
      {pages.map((p) => (
        <button
          key={p}
          className={`paginator__btn ${p === currentPage ? 'paginator__btn--active' : ''}`}
          onClick={() => onPageChange(p)}
        >
          {p}
        </button>
      ))}
      <button
        className="paginator__btn"
        disabled={nextPage > totalPages}
        onClick={() => onPageChange(nextPage)}
      >
        Next
      </button>
    </div>
  );
}

export default Paginator;
