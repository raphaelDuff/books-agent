import React from "react";
import ReactDOM from "react-dom/client";
// Fraunces (literary serif) carries the "voice of the books"; Inter (sans) is the
// "voice of the tool". Optical-sizing axis lets display titles use the high-contrast
// cut while body prose stays readable.
import "@fontsource-variable/fraunces/opsz.css";
import "@fontsource-variable/fraunces/opsz-italic.css";
import "@fontsource-variable/inter/wght.css";
import App from "./App.jsx";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
