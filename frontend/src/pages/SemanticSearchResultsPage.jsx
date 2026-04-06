/**
 * Página de resultados da busca semântica
 */
import { useLocation, useNavigate } from "react-router-dom";
import { downloadFile } from "../api/files";

export default function SemanticSearchResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { query = "", results = [], totalResults = 0 } = location.state || {};

  const handleDownload = async (file) => {
    try {
      await downloadFile(file.file_id);
    } catch (error) {
      alert("Erro ao baixar arquivo: " + error.message);
    }
  };

  const handleOpenFile = (fileId) => {
    // Passe para visualização (implementar se needed)
    console.log("Abrir arquivo:", fileId);
  };

  return (
    <div className="search-results-page">
      <div className="search-header">
        <button className="back-button" onClick={() => navigate(-1)}>
          ← Voltar
        </button>
        <div className="search-info">
          <h1>Resultados da Busca Semântica</h1>
          <p className="search-query">
            Query: <strong>"{query}"</strong>
          </p>
          <p className="results-count">
            {totalResults === 0
              ? "Nenhum resultado encontrado"
              : `${totalResults} documento(s) encontrado(s)`}
          </p>
        </div>
      </div>

      {results.length === 0 ? (
        <div className="no-results">
          <p>Nenhum documento encontrado para sua busca.</p>
          <p>Tente buscar por outros termos ou verifique se os documentos foram processados.</p>
        </div>
      ) : (
        <div className="results-list">
          {results.map((result, idx) => (
            <div key={idx} className="result-card">
              <div className="result-header">
                <h3 className="result-filename">{result.file_name}</h3>
                <span className="result-type">{result.mime_type}</span>
              </div>

              <div className="result-similarity">
                <span className="label">Similaridade:</span>
                <div className="similarity-bar">
                  <div
                    className="similarity-fill"
                    style={{
                      width: `${result.similarity_score * 100}%`,
                    }}
                  ></div>
                </div>
                <span className="similarity-text">
                  {(result.similarity_score * 100).toFixed(1)}%
                </span>
              </div>

              {result.extracted_text_snippet && (
                <div className="result-snippet">
                  <span className="label">Trecho relevante:</span>
                  <p className="snippet-text">
                    "{result.extracted_text_snippet}..."
                  </p>
                  <span className="text-length">
                    {result.extracted_text_length} caracteres extraídos
                  </span>
                </div>
              )}

              <div className="result-actions">
                <button
                  className="primary"
                  onClick={() => handleOpenFile(result.file_id)}
                >
                  Visualizar
                </button>
                <button
                  className="secondary"
                  onClick={() => handleDownload(result.file_id)}
                >
                  Baixar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
