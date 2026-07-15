import { type Company } from './';

import './styles/styles.css';

interface CompaniesListProps {
  companies: Company[];
  companiesLoading: boolean;
  selectedCompanyIds: Set<number>;
  allCompaniesSelected: boolean;
  onToggleAllCompanies: () => void;
  onToggleOneCompany: (id: number) => void;
}

const CompaniesList = ({
  companies,
  companiesLoading,
  selectedCompanyIds,
  allCompaniesSelected,
  onToggleAllCompanies,
  onToggleOneCompany,
}: CompaniesListProps) => (
  <>
    {companiesLoading ? (
      <p className="app__loading">Loading companies...</p>
    ) : (
      <ul className="company-list">
        <li className="company-list__header">
          <label className="company-list__checkbox-label">
            <input
              type="checkbox"
              className="company-list__checkbox"
              checked={allCompaniesSelected}
              onChange={onToggleAllCompanies}
            />
          </label>
          <div className="company-list__info">
            <span className="company-list__col-company">Company</span>
            <span className="company-list__col-website">Website</span>
            <span className="company-list__col-kvk">KvK</span>
          </div>
        </li>
        {companies.map((company) => (
          <li key={company.id} className="company-list__item">
            <label className="company-list__checkbox-label">
              <input
                type="checkbox"
                className="company-list__checkbox"
                checked={selectedCompanyIds.has(company.id)}
                onChange={() => onToggleOneCompany(company.id)}
              />
            </label>
            <div className="company-list__info">
              <span className="company-list__name">{company.name}</span>
              {company.website_url ? (
                <a
                  className="company-list__url"
                  href={company.website_url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {company.website_url}
                </a>
              ) : (
                <span className="company-list__no-url">No website</span>
              )}
              <span className="company-list__kvk">{company.kvk_number}</span>
            </div>
          </li>
        ))}
      </ul>
    )}
  </>
);

export default CompaniesList;
