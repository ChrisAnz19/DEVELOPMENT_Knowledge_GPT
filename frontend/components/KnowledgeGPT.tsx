import React, { useState, useEffect } from 'react';
import axios from 'axios';

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

interface KnowledgeGPTProps {
  apiUrl?: string;
  onSearchComplete?: (results: SearchResponse) => void;
  className?: string;
}

const KnowledgeGPT: React.FC<KnowledgeGPTProps> = ({
  apiUrl = 'http://localhost:8000',
  onSearchComplete,
  className = ''
}) => {
  const [prompt, setPrompt] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [currentSearch, setCurrentSearch] = useState<SearchResponse | null>(null);
  const [searchHistory, setSearchHistory] = useState<SearchResponse[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Polling for search updates
  useEffect(() => {
    if (!currentSearch || currentSearch.status !== 'processing') return;

    const pollInterval = setInterval(async () => {
      try {
        const response = await axios.get(`${apiUrl}/api/search/${currentSearch.request_id}`);
        const updatedSearch = response.data;
        
        setCurrentSearch(updatedSearch);
        
        if (updatedSearch.status === 'completed') {
          setIsSearching(false);
          setSearchHistory(prev => [updatedSearch, ...prev.slice(0, 9)]); // Keep last 10
          onSearchComplete?.(updatedSearch);
        } else if (updatedSearch.status === 'failed') {
          setIsSearching(false);
          setError(updatedSearch.error || 'Search failed');
        }
      } catch (err) {
        console.error('Error polling search status:', err);
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(pollInterval);
  }, [currentSearch, apiUrl, onSearchComplete]);

  const handleSearch = async () => {
    if (!prompt.trim()) return;

    setIsSearching(true);
    setError(null);

    try {
      const searchRequest: SearchRequest = {
        prompt: prompt.trim(),
        max_candidates: 2,
        include_linkedin: true,
        include_posts: true
      };

      const response = await axios.post(`${apiUrl}/api/search`, searchRequest);
      const searchResponse = response.data;
      
      setCurrentSearch(searchResponse);
    } catch (err: any) {
      setIsSearching(false);
      setError(err.response?.data?.detail || err.message || 'Failed to start search');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isSearching) {
      handleSearch();
    }
  };

  return (
    <div className={`knowledge-gpt ${className}`}>
      {/* Search Input */}
      <div className="search-section mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter your search prompt (e.g., 'Find CEOs at large software companies in San Francisco')"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isSearching}
          />
          <button
            onClick={handleSearch}
            disabled={isSearching || !prompt.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSearching ? 'Searching...' : 'Search'}
          </button>
        </div>
        
        {error && (
          <div className="mt-2 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}
      </div>

      {/* Current Search Progress */}
      {currentSearch && currentSearch.status === 'processing' && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            <span className="font-medium">Processing search...</span>
          </div>
          <p className="text-sm text-gray-600">Request ID: {currentSearch.request_id}</p>
        </div>
      )}

      {/* Search Results */}
      {currentSearch && currentSearch.status === 'completed' && currentSearch.candidates && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-4">Top Candidates</h3>
          <div className="grid gap-4">
            {currentSearch.candidates.map((candidate, index) => (
              <div key={index} className="p-4 border border-gray-200 rounded-lg">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h4 className="font-medium text-lg">{candidate.name}</h4>
                    <p className="text-gray-600">{candidate.title}</p>
                    <p className="text-gray-500">{candidate.company}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-500">Accuracy</div>
                    <div className="text-lg font-semibold text-green-600">{candidate.accuracy}%</div>
                  </div>
                </div>
                
                <div className="mb-3">
                  <span className="text-sm text-gray-500">Email: </span>
                  <span className="text-sm">{candidate.email}</span>
                </div>
                
                <div>
                  <h5 className="font-medium text-sm mb-2">Selection Reasons:</h5>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {candidate.reasons.map((reason, reasonIndex) => (
                      <li key={reasonIndex} className="flex items-start gap-2">
                        <span className="text-blue-500 mt-1">•</span>
                        <span>{reason}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Behavioral Data */}
      {currentSearch && currentSearch.status === 'completed' && currentSearch.behavioral_data && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-4">Behavioral Insights</h3>
          <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
            <pre className="text-sm overflow-auto">
              {JSON.stringify(currentSearch.behavioral_data, null, 2)}
            </pre>
          </div>
        </div>
      )}

      {/* Search History */}
      {searchHistory.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Recent Searches</h3>
          <div className="space-y-2">
            {searchHistory.map((search) => (
              <div key={search.request_id} className="p-3 border border-gray-200 rounded-lg">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="font-medium">{search.prompt}</p>
                    <p className="text-sm text-gray-500">
                      {new Date(search.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 text-xs rounded ${
                      search.status === 'completed' ? 'bg-green-100 text-green-800' :
                      search.status === 'failed' ? 'bg-red-100 text-red-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {search.status}
                    </span>
                    {search.candidates && (
                      <span className="text-sm text-gray-500">
                        {search.candidates.length} candidates
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default KnowledgeGPT; 