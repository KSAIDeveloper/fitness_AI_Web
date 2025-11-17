import React from 'react';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-content">
          <div className="footer-section">
            <h3>FitC</h3>
            <p>건강한 운동 생활을 위한 최고의 파트너</p>
          </div>
          <div className="footer-section">
            <h4>제품</h4>
            <ul>
              <li><a href="#">칼로리 계산기</a></li>
              <li><a href="#">운동 추천</a></li>
              <li><a href="#">식단 관리</a></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4>Developer</h4>
            <ul>
              <li><a href="#">그룹 소개</a></li>
              <li><a href="#">팀원 소개</a></li>
              <li><a href="#">문의하기</a></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4>법적 고지</h4>
            <ul>
              <li><a href="#">이용약관</a></li>
              <li><a href="#">개인정보처리방침</a></li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2025 Developer. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
