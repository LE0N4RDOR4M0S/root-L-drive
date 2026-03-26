export default function FolderBreadcrumbs({ path, onGoRoot, onGoToIndex }) {
  return (
    <div className="breadcrumbs">
      <button className="link" onClick={onGoRoot}>
        Home
      </button>

      {path.map((folder, index) => (
        <span key={folder.id} className="crumb-item">
          <span>/</span>
          <button className="link" onClick={() => onGoToIndex(index)}>
            {folder.name}
          </button>
        </span>
      ))}
    </div>
  );
}
