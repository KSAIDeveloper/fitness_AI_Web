import React, { useCallback, useMemo, useState } from "react";
import "./FoodAnalyzer.css";

// Prefer proxy (/api) in dev; allow override via VITE_API_BASE
const API_BASE = import.meta.env.VITE_API_BASE || "/api";

export default function FoodAnalyzer() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const onFileChange = useCallback((e) => {
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);
      const url = URL.createObjectURL(f);
      setPreviewUrl(url);
      setResult(null);
      setError("");
    }
  }, []);

  const handleAnalyze = useCallback(async () => {
    if (!file) {
      setError("이미지를 먼저 선택해 주세요.");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const fd = new FormData();
      fd.append("image", file);
      fd.append("mode", "chat");
      const r = await fetch(`${API_BASE}/classify`, {
        method: "POST",
        body: fd,
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data?.detail || data?.error || "요청 실패");
      setResult(data);
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setLoading(false);
    }
  }, [file]);

  const uploadedLabel = useMemo(
    () => (file ? file.name : "이미지 파일을 선택하세요"),
    [file]
  );

  return (
    <div className="fa-container">
      <div className="fa-header">
        <h1>음식 이미지 분석</h1>
        <p>이미지를 업로드하면 음식 이름과 예상 칼로리를 분석해 드립니다.</p>
      </div>

      <div className="fa-grid">
        {/* 좌측: 업로드 카드 */}
        <section className="fa-card fa-upload">
          <h2>이미지 업로드</h2>
          <label className="fa-file-label">
            <input type="file" accept="image/*" onChange={onFileChange} />
            <span>{uploadedLabel}</span>
          </label>

          {previewUrl && (
            <div className="fa-preview">
              <img src={previewUrl} alt="미리보기" />
            </div>
          )}

          <button
            className="fa-analyze-btn"
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? "분석 중…" : "분석하기"}
          </button>
          {error && <div className="fa-error">{error}</div>}
        </section>

        {/* 우측: 결과 카드 */}
        <section className="fa-card fa-result">
          <h2>분석 결과</h2>
          {!result && !loading && (
            <div className="fa-placeholder">
              이미지를 업로드하고 분석을 시작하세요.
            </div>
          )}
          {result && (
            <div className="fa-result-body">
              <div className="fa-result-main">
                <div className="fa-kcal-box">
                  <div className="fa-kcal-value">
                    {(() => {
                      try {
                        const kcal = result?.data?.calories_kcal ?? null;
                        if (kcal == null) return "-";
                        const n = Number(kcal);
                        return Number.isFinite(n) ? Math.round(n) : "-";
                      } catch {
                        return "-";
                      }
                    })()}
                  </div>
                  <div className="fa-kcal-label">예상 칼로리 (kcal)</div>
                </div>
                <div className="fa-meta">
                  <div className="fa-meta-item">
                    <span className="fa-meta-key">음식 이름</span>
                    <span className="fa-meta-val">
                      {result?.data?.label_ko || result?.data?.label || "-"}
                    </span>
                  </div>
                  <div className="fa-meta-item">
                    <span className="fa-meta-key">신뢰도</span>
                    <span className="fa-meta-val">
                      {(() => {
                        const c = result?.data?.confidence;
                        return c != null ? Number(c).toFixed(2) : "-";
                      })()}
                    </span>
                  </div>
                  <div className="fa-meta-item">
                    <span className="fa-meta-key">1회 제공량</span>
                    <span className="fa-meta-val">
                      {result?.data?.serving_ko || result?.data?.serving || "-"}
                    </span>
                  </div>
                </div>
              </div>
              <div className="fa-notes">
                {result?.data?.notes_ko || result?.data?.notes || ""}
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
