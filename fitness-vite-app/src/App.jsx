import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import MainLayout from "./components/layout/MainLayout";
import Home from "./components/pages/Home";
import CalorieCalculator from "./components/pages/CalorieCalculator";
import FoodAnalyzer from "./components/pages/FoodAnalyzer";
import "./App.css";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Home />} />
          <Route path="calculator" element={<CalorieCalculator />} />
          <Route path="food-analyzer" element={<FoodAnalyzer />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
