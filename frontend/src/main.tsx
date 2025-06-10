import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css"; // Certifique-se que este arquivo tem as diretivas do Tailwind

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
