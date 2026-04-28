import { Navigate, Route, Routes } from "react-router-dom";

import AppLayout from "./layouts/AppLayout";
import FilesPage from "./pages/FilesPage";
import FoldersPage from "./pages/FoldersPage";
import LoginPage from "./pages/LoginPage";
import OverviewPage from "./pages/OverviewPage";
import FavoritesPage from "./pages/FavoritesPage";
import TrashPage from "./pages/TrashPage";
import PublicSharePage from "./pages/PublicSharePage";
import SemanticSearchResultsPage from "./pages/SemanticSearchResultsPage";

function ProtectedRoute({ children }) {
  const token = localStorage.getItem("auth_token");
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/share/:token" element={<PublicSharePage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<OverviewPage />} />
        <Route path="folders" element={<FoldersPage />} />
        <Route path="files" element={<FilesPage />} />
        <Route path="favorites" element={<FavoritesPage />} />
        <Route path="trash" element={<TrashPage />} />
        <Route path="search-results" element={<SemanticSearchResultsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
