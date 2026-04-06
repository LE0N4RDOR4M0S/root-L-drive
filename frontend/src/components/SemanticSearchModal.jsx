/**
 * Componente para busca semântica em documentos
 */
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { semanticSearch } from "../api/search";

export default function SemanticSearchModal({ isOpen, onClose }) {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    try {
      setLoading(true);
      setError("");
      const results = await semanticSearch(query, 10);
      
      // Navega para página de resultados com dados em state
      navigate("/search-results", { 
        state: { 
          query: query,
          results: results.results,
          totalResults: results.total_results,
        } 
      });
      
      setQuery("");
    } catch (err) {
      setError(err.response?.data?.detail || "Erro na busca semântica");
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>Busca Semântica de Documentos</h2>
        
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="Ex: Contrato que fala sobre multa..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading}
            autoFocus
          />
          <button type="submit" disabled={loading || !query.trim()}>
            {loading ? "Buscando..." : "Buscar"}
          </button>
        </form>

        {error && <div className="error-message">{error}</div>}

        <div className="search-tips">
          <h3>💡 Dicas:</h3>
          <ul>
            <li>Use linguagem natural: "contrato de serviço"</li>
            <li>Busque por tema: "multa", "atraso", "desconto"</li>
            <li>Encontra documentos pelo conteúdo, não só pelo nome</li>
          </ul>
        </div>

        <button className="secondary" onClick={onClose}>
          Cancelar
        </button>
      </div>
    </div>
  );
}
