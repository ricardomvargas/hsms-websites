import { useCompanies, CompaniesList } from './components/companies-list';
import { FilterInput } from './components/filter-input';
import { Loader } from './components/loader';
import { Paginator } from './components/paginator';

import './App.css';

function App() {
  const {
    companies,
    companiesLoading,
    importingCompanies,
    importCompanies,
    fetchingWebsites,
    fetchWebsites,
    filteringCompanies,
    filterQuery,
    filterCompanies,
    clearFilter,
    filterPage,
    filterTotalPages,
    goToFilterPage,
    selectedCompanyIds,
    allCompaniesSelected,
    toggleAllCompanies,
    toggleOneCompany,
    companiesPage,
    companiesTotalPages,
    goToCompaniesPage,
  } = useCompanies();

  return (
    <div className="app">
      <header className="app__header">
        <h1 className="app__title">HSM Sponsors website search</h1>
      </header>
      <div className="app__content">
        <div className="app__section-header">
            <div className="app__section-header-left">
              <FilterInput
                onFilter={(query) => {
                  if (query) {
                    filterCompanies(query);
                  } else {
                    clearFilter();
                  }
                }}
                filterActive={filterQuery !== ''}
              />
            </div>
            <div className="app__section-header-right">
              <button
                className="app__import-btn"
                onClick={importCompanies}
                disabled={importingCompanies}
              >
                {importingCompanies ? 'Importing...' : 'Import from IND'}
              </button>
              <button
                className="app__fetch-btn"
                disabled={selectedCompanyIds.size === 0 || fetchingWebsites}
                onClick={fetchWebsites}
              >
                {fetchingWebsites ? 'Fetching...' : 'Get website info'}
              </button>
            </div>
          </div>
          <div className="app__companies-scroll">
            <CompaniesList
              companies={companies}
              companiesLoading={companiesLoading}
              selectedCompanyIds={selectedCompanyIds}
              allCompaniesSelected={allCompaniesSelected}
              onToggleAllCompanies={toggleAllCompanies}
              onToggleOneCompany={toggleOneCompany}
            />
          </div>
          {filterQuery
            ? filterTotalPages > 1 && (
                <div className="app__paginator">
                  <Paginator
                    currentPage={filterPage}
                    totalPages={filterTotalPages}
                    onPageChange={goToFilterPage}
                  />
                </div>
              )
            : companiesTotalPages > 1 && (
                <div className="app__paginator">
                  <Paginator
                    currentPage={companiesPage}
                    totalPages={companiesTotalPages}
                    onPageChange={goToCompaniesPage}
                  />
                </div>
              )}
      </div>
      <Loader visible={filteringCompanies} text="Filtering..." />
      <Loader visible={importingCompanies} text="Importing companies..." />
      <Loader
        visible={fetchingWebsites}
        text={
          selectedCompanyIds.size <= 5
            ? 'Loading...'
            : selectedCompanyIds.size <= 12
              ? 'Getting data, the process can take a minute'
              : 'Getting data, the process can take a while'
        }
      />
    </div>
  );
}

export default App;
