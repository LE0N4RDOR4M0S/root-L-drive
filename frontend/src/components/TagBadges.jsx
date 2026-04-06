/**
 * Componente para exibir tags de imagens/arquivos
 */
export default function TagBadges({ tags = [] }) {
  if (!tags || tags.length === 0) {
    return null;
  }

  return (
    <div className="tag-badges">
      {tags.slice(0, 5).map((tag, idx) => (
        <span key={idx} className="tag-badge" title={`Confiança: ${(tag.confidence * 100).toFixed(0)}%`}>
          {tag.name}
          <span className="tag-confidence">({(tag.confidence * 100).toFixed(0)}%)</span>
        </span>
      ))}
      {tags.length > 5 && <span className="tag-more">+{tags.length - 5}</span>}
    </div>
  );
}
