import React from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

const Home = () => {
  return (
    <div className="home">
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">건강한 운동 생활의 시작</h1>
          <p className="hero-description">
            FitC와 함께 운동 칼로리를 정확하게 계산하고 <br />
            건강한 라이프스타일을 시작하세요
          </p>
          <Link to="/calculator" className="hero-button">
            칼로리 계산하기
          </Link>
        </div>
      </section>

      <section className="features-section">
        <h2 className="section-title">왜 FitC를 선택해야 할까요?</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>정확한 계산</h3>
            <p>MET 기반의 과학적인 칼로리 계산으로 정확한 결과를 제공합니다</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🏃</div>
            <h3>다양한 운동</h3>
            <p>10개 이상의 다양한 운동 유형을 지원합니다</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <h3>빠른 사용</h3>
            <p>간단한 입력만으로 즉시 결과를 확인할 수 있습니다</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📱</div>
            <h3>반응형 디자인</h3>
            <p>모바일, 태블릿, PC 모든 기기에서 완벽하게 작동합니다</p>
          </div>
        </div>
      </section>

      <section className="cta-section">
        <div className="cta-content">
          <h2>지금 바로 시작하세요</h2>
          <p>건강한 운동 습관을 만들어보세요</p>
          <Link to="/calculator" className="cta-button">
            시작하기
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Home;
