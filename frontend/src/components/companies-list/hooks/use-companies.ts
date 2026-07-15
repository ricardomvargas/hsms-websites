import { useCallback, useEffect, useMemo, useState } from 'react';

import { type Company } from '../';

export function useCompanies() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [companiesLoading, setCompaniesLoading] = useState(false);
  const [importingCompanies, setImportingCompanies] = useState(false);
  const [fetchingWebsites, setFetchingWebsites] = useState(false);
  const [filteringCompanies, setFilteringCompanies] = useState(false);
  const [filterQuery, setFilterQuery] = useState('');
  const [selectedCompanyIds, setSelectedCompanyIds] = useState<Set<number>>(new Set());
  const [companiesPage, setCompaniesPage] = useState(1);
  const [companiesTotalPages, setCompaniesTotalPages] = useState(1);
  const [filterPage, setFilterPage] = useState(1);
  const [filterTotalPages, setFilterTotalPages] = useState(1);

  const fetchCompanies = useCallback(async (page: number) => {
    setCompaniesLoading(true);
    try {
      const res = await fetch(`/companies?page=${page}&per_page=20`);
      const data = await res.json();
      setCompanies(data.items);
      setCompaniesTotalPages(Math.ceil(data.total / data.per_page));
      setCompaniesPage(data.page);
    } finally {
      setCompaniesLoading(false);
    }
  }, []);

  const importCompanies = useCallback(async () => {
    setImportingCompanies(true);
    try {
      await fetch('/import', { method: 'POST' });
      setFilterQuery('');
      setSelectedCompanyIds(new Set());
      await fetchCompanies(1);
    } finally {
      setImportingCompanies(false);
    }
  }, [fetchCompanies]);

  const fetchFilteredPage = useCallback(async (query: string, page: number) => {
    const res = await fetch(
      `/companies/search?q=${encodeURIComponent(query)}&page=${page}&per_page=20`,
    );
    const data = await res.json();
    setCompanies(data.items);
    setFilterTotalPages(Math.ceil(data.total / data.per_page));
    setFilterPage(data.page);
  }, []);

  const fetchWebsites = useCallback(async () => {
    setFetchingWebsites(true);
    try {
      await fetch('/companies/fetch-websites', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company_ids: [...selectedCompanyIds] }),
      });
      if (filterQuery) {
        await fetchFilteredPage(filterQuery, filterPage);
      } else {
        await fetchCompanies(companiesPage);
      }
    } finally {
      setFetchingWebsites(false);
    }
  }, [selectedCompanyIds, fetchCompanies, companiesPage, filterQuery, fetchFilteredPage, filterPage]);

  const filterCompanies = useCallback(async (query: string) => {
    setFilteringCompanies(true);
    setSelectedCompanyIds(new Set());
    try {
      if (!query.trim()) {
        setFilterQuery('');
        setCompanies([]);
        setFilterTotalPages(1);
        setFilterPage(1);
        return;
      }
      setFilterQuery(query);
      await fetchFilteredPage(query, 1);
    } finally {
      setFilteringCompanies(false);
    }
  }, [fetchFilteredPage]);

  const goToFilterPage = useCallback(
    (page: number) => {
      setSelectedCompanyIds(new Set());
      if (filterQuery) {
        fetchFilteredPage(filterQuery, page);
      }
    },
    [filterQuery, fetchFilteredPage],
  );

  const clearFilter = useCallback(() => {
    setFilterQuery('');
    setFilterPage(1);
    setFilterTotalPages(1);
    setSelectedCompanyIds(new Set());
    fetchCompanies(1);
  }, [fetchCompanies]);

  const goToCompaniesPage = useCallback(
    (page: number) => {
      setSelectedCompanyIds(new Set());
      fetchCompanies(page);
    },
    [fetchCompanies],
  );

  const allCompaniesSelected = useMemo(
    () => companies.length > 0 && selectedCompanyIds.size === companies.length,
    [companies.length, selectedCompanyIds.size],
  );

  const toggleAllCompanies = useCallback(() => {
    if (allCompaniesSelected) {
      setSelectedCompanyIds(new Set());
    } else {
      setSelectedCompanyIds(new Set(companies.map((c) => c.id)));
    }
  }, [allCompaniesSelected, companies]);

  const toggleOneCompany = useCallback((id: number) => {
    setSelectedCompanyIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  useEffect(() => {
    fetchCompanies(1);
  }, [fetchCompanies]);

  return {
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
  };
}
