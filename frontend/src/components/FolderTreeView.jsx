import { useEffect, useMemo, useState } from "react";

function collectExpandableIds(nodes, ids = new Set()) {
  for (const node of nodes) {
    if (node.children.length > 0) {
      ids.add(node.folder.id);
      collectExpandableIds(node.children, ids);
    }
  }
  return ids;
}

function TreeNode({ node, level, expandedIds, onToggle, onSelect, selectedFolderId }) {
  const hasChildren = node.children.length > 0;
  const isExpanded = expandedIds.has(node.folder.id);
  const isSelected = selectedFolderId === node.folder.id;

  return (
    <li className="tree-node-item">
      <div className="tree-node-row" style={{ paddingLeft: `${level * 14}px` }}>
        {hasChildren ? (
          <button
            type="button"
            className="tree-toggle"
            onClick={() => onToggle(node.folder.id)}
            aria-label={isExpanded ? "Recolher pasta" : "Expandir pasta"}
          >
            {isExpanded ? "▾" : "▸"}
          </button>
        ) : (
          <span className="tree-toggle tree-toggle-empty">•</span>
        )}

        <button
          type="button"
          className={`tree-node-link ${isSelected ? "selected" : ""}`}
          onClick={() => onSelect(node.path)}
        >
          {node.folder.name}
        </button>
      </div>

      {hasChildren && isExpanded && (
        <ul className="tree-node-list">
          {node.children.map((child) => (
            <TreeNode
              key={child.folder.id}
              node={child}
              level={level + 1}
              expandedIds={expandedIds}
              onToggle={onToggle}
              onSelect={onSelect}
              selectedFolderId={selectedFolderId}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

export default function FolderTreeView({ nodes, selectedFolderId, onSelect }) {
  const [expandedIds, setExpandedIds] = useState(new Set());

  const allExpandableIds = useMemo(() => collectExpandableIds(nodes), [nodes]);

  useEffect(() => {
    setExpandedIds(new Set(allExpandableIds));
  }, [allExpandableIds]);

  const toggleNode = (folderId) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(folderId)) {
        next.delete(folderId);
      } else {
        next.add(folderId);
      }
      return next;
    });
  };

  if (nodes.length === 0) {
    return <p className="tree-empty">Sem pastas para exibir.</p>;
  }

  return (
    <ul className="tree-node-list">
      {nodes.map((node) => (
        <TreeNode
          key={node.folder.id}
          node={node}
          level={0}
          expandedIds={expandedIds}
          onToggle={toggleNode}
          onSelect={onSelect}
          selectedFolderId={selectedFolderId}
        />
      ))}
    </ul>
  );
}
