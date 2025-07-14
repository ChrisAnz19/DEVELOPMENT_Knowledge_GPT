import { useState, useEffect, useCallback } from 'react';

interface SearchRequest {
  prompt: string;
  max_candidates?: number;
  include_linkedin?: boolean;
  include_posts?: boolean;
}

interface SearchResponse {
  request_id: string;
  status: 'processing' | 'completed' | 'failed';
  prompt: string;
  filters?: any;
  candidates?: Candidate[];
  behavioral_data?: any;
  error?: string;
  created_at: string;
  completed_at?: string;
}

interface Candidate {
  name: string;
  title: string;
  company: string;
  email: string;
  accuracy: number;
  reasons: string[];
}

interface UseKnowledgeGPTOptions {
  apiUrl?: string;
  pollingInterval?: number;
  onSearchComplete?: (results: SearchResponse) => void;
  onError?: (error: string) => void;
}

export const useKnowledgeGPT = (options: UseKnowledgeGPTOptions = {}) => {
  const {
    apiUrl = 'http://localhost:8000',
    pollingInterval = 2000,
    onSearchComplete,
    onError
  } = options;

  const [isSearching, setIsSearching] = useState(false);
  const [currentSearch, setCurrentSearch] = useState<SearchResponse | null>(null);
  const [searchHistory, setSearchHistory] = useState<SearchResponse[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Polling for search updates
  useEffect(() => {
    if (!currentSearch || currentSearch.status !== 'processing') return;

    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`${apiUrl}/api/search/${currentSearch.request_id}`);
        if (!response.ok) throw new Error('Failed to fetch search status');
        
        const updatedSearch: SearchResponse = await response.json();
        setCurrentSearch(updatedSearch);
        
        if (updatedSearch.status === 'completed') {
          setIsSearching(false);
          setSearchHistory(prev => [updatedSearch, ...prev.slice(0, 9)]); // Keep last 10
          onSearchComplete?.(updatedSearch);
        } else if (updatedSearch.status === 'failed') {
          setIsSearching(false);
          const errorMessage = updatedSearch.error || 'Search failed';
          setError(errorMessage);
          onError?.(errorMessage);
        }
      } catch (err) {
        console.error('Error polling search status:', err);
      }
    }, pollingInterval);

    return () => clearInterval(pollInterval);
  }, [currentSearch, apiUrl, pollingInterval, onSearchComplete, onError]);

  const search = useCallback(async (prompt: string, options: Partial<SearchRequest> = {}) => {
    if (!prompt.trim()) return;

    setIsSearching(true);
    setError(null);

    try {
      const searchRequest: SearchRequest = {
        prompt: prompt.trim(),
        max_candidates: 2,
        include_linkedin: true,
        include_posts: true,
        ...options
      };

      const response = await fetch(`${apiUrl}/api/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchRequest),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to start search');
      }

      const searchResponse: SearchResponse = await response.json();
      setCurrentSearch(searchResponse);
    } catch (err: any) {
      setIsSearching(false);
      const errorMessage = err.message || 'Failed to start search';
      setError(errorMessage);
      onError?.(errorMessage);
    }
  }, [apiUrl, onError]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const clearHistory = useCallback(() => {
    setSearchHistory([]);
  }, []);

  return {
    search,
    isSearching,
    currentSearch,
    searchHistory,
    error,
    clearError,
    clearHistory
  };
}; 