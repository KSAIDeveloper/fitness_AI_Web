import React from "react";
import { Link } from "react-router-dom";
import "./Header.css";
import logoImage from "../../assets/FitC_로고.png"; // 이미지 경로는 프로젝트 구조에 맞게 조정하세요

const Header = () => {
  return (
    <header className="header">
      <div className="header-container">
        <Link to="/" className="logo">
          <img src={logoImage} alt="FitC Logo" className="logo-image" />
        </Link>

        <nav className="nav-menu">
          <Link to="/calculator" className="nav-item active">
            계산기
          </Link>
          <Link to="/food-analyzer" className="nav-item">
            음식 이미지 분석
          </Link>
          <Link to="/workout" className="nav-item">
            운동
          </Link>
          <Link to="/diet" className="nav-item">
            식단
          </Link>
          <Link to="/faq" className="nav-item">
            자주 묻는 질문
          </Link>
        </nav>

        <button className="cta-button">지금 시작하기</button>
      </div>
    </header>
  );
};

export default Header;
