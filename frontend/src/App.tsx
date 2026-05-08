import { useEffect } from "react";
import Home from "./pages/Home";

export default function App() {
  useEffect(() => {
    document.documentElement.classList.add("dark");
  }, []);

  return <Home />;
}
