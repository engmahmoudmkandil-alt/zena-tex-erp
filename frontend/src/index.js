import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";
import "@/i18n"; // Initialize i18n

// Set initial direction based on stored language
const storedLang = localStorage.getItem('i18nextLng') || 'en';
document.documentElement.dir = storedLang === 'ar' ? 'rtl' : 'ltr';
document.documentElement.lang = storedLang;

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
