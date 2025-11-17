import React, { useState, useEffect } from "react";
import "./CalorieCalculator.css";

const CalorieCalculator = () => {
  const [weight, setWeight] = useState(70);
  const [unit, setUnit] = useState("kg");
  const [duration, setDuration] = useState(30);
  const [customDuration, setCustomDuration] = useState("");
  const [selectedExercise, setSelectedExercise] = useState("걷기");
  const [calories, setCalories] = useState(0);

  // ✅ 추가된 상태
  const [mode, setMode] = useState("MET"); // MET | HR
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("male");
  const [heartRate, setHeartRate] = useState("");

  // MET 값
  const metValues = {
    걷기: 3.0,
    "여유 산책": 3.0,
    "실내 산책": 2.5,
    하이킹: 6.0,
    "반려견 산책": 3.0,
  };

  const exercises = [
    { name: "걷기", met: 3.0 },
    { name: "여유 산책", met: 3.0 },
    { name: "실내 산책", met: 2.5 },
    { name: "하이킹", met: 6.0 },
    { name: "반려견 산책", met: 3.0 },
  ];

  const durations = [15, 20, 25, 30, 35, 40, 45, 60];

  // ✅ HR 계산
  const calcHRCalories = () => {
    const time = customDuration || duration;
    const w = unit === "kg" ? weight : weight * 0.453592;
    let cals = 0;

    if (gender === "male") {
      cals =
        ((age * 0.2017) + (heartRate * 0.6309) - (w * 0.09036) - 55.0969) *
        (time / 4.184);
    } else {
      cals =
        ((age * 0.074) + (heartRate * 0.4472) - (w * 0.05741) - 20.4022) *
        (time / 4.184);
    }

    return Math.max(0, Math.round(cals));
  };

  // ✅ 기존 MET 계산
  const calcMETCalories = () => {
    const weightInKg = unit === "kg" ? weight : weight * 0.453592;
    const time = customDuration || duration;
    const met = metValues[selectedExercise] || 3.0;

    return Math.round(met * weightInKg * (time / 60));
  };

  // ✅ 계산 모드에 따라 분기
  const calculateCalories = () => {
    if (mode === "HR") {
      setCalories(calcHRCalories());
    } else {
      setCalories(calcMETCalories());
    }
  };

  useEffect(() => {
    calculateCalories();
  }, [weight, unit, duration, customDuration, selectedExercise, mode, age, gender, heartRate]);

  return (
    <div className="calorie-calculator">
      <div className="calculator-header">
        <h1>운동 칼로리 소모량 계산기</h1>
        <p>한 번의 운동 중 몇 칼로리를 소모했는지 계산해보세요!</p>
        <p className="subtitle">
          MET 기반 / HR(심박수) 기반 모두 지원
        </p>
      </div>

      <div className="calculator-container">
        <div className="input-section">

          {/* ✅ 계산 방식 */}
          <div className="form-group">
            <label className="form-label">계산 방식</label>
            <select
              className="form-input"
              value={mode}
              onChange={(e) => setMode(e.target.value)}
            >
              <option value="MET">MET 기반</option>
              <option value="HR">HR 기반</option>
            </select>
          </div>

          {/* ✅ 무게 */}
          <div className="form-group">
            <label className="form-label">무게</label>
            <div className="weight-input-group">
              <input
                type="number"
                value={weight}
                onChange={(e) => setWeight(Number(e.target.value))}
                className="form-input"
              />

              <div className="unit-toggle">
                <button
                  className={`unit-btn ${unit === "kg" ? "active" : ""}`}
                  onClick={() => setUnit("kg")}
                >
                  kg
                </button>
                <button
                  className={`unit-btn ${unit === "lbs" ? "active" : ""}`}
                  onClick={() => setUnit("lbs")}
                >
                  lbs
                </button>
              </div>
            </div>
          </div>

          {/* ✅ 공통: 운동 시간 */}
          <div className="form-group">
            <label className="form-label">지속 시간(분)</label>
            <div className="duration-buttons">
              {durations.map((time) => (
                <button
                  key={time}
                  className={`duration-btn ${duration === time && !customDuration ? "active" : ""}`}
                  onClick={() => {
                    setDuration(time);
                    setCustomDuration("");
                  }}
                >
                  {time}분
                </button>
              ))}
            </div>
            <input
              type="number"
              placeholder="30"
              value={customDuration}
              onChange={(e) => setCustomDuration(e.target.value)}
              className="form-input custom-duration"
            />
          </div>

          {/* ✅ MET일 때만 */}
          {mode === "MET" && (
            <div className="form-group">
              <label className="form-label">운동 유형</label>

              <div className="exercise-dropdown">
                <button className="exercise-btn-main">
                  {selectedExercise}
                  <span className="dropdown-arrow">▼</span>
                </button>

                <div className="exercise-list">
                  {exercises.map((exercise) => (
                    <button
                      key={exercise.name}
                      className={`exercise-item ${selectedExercise === exercise.name ? "active" : ""}`}
                      onClick={() => setSelectedExercise(exercise.name)}
                    >
                      {exercise.name}
                      <span className="met-value">MET {exercise.met}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* ✅ HR일 때만 */}
          {mode === "HR" && (
            <>
              <div className="form-group">
                <label className="form-label">나이</label>
                <input
                  type="number"
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label className="form-label">성별</label>
                <select
                  value={gender}
                  onChange={(e) => setGender(e.target.value)}
                  className="form-input"
                >
                  <option value="male">남성</option>
                  <option value="female">여성</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">심박수(bpm)</label>
                <input
                  type="number"
                  value={heartRate}
                  onChange={(e) => setHeartRate(e.target.value)}
                  className="form-input"
                />
              </div>
            </>
          )}
        </div>

        {/* ✅ 결과 */}
        <div className="result-section">
          <div className="result-card">
            <div className="result-number">{calories}</div>
            <div className="result-label">소모된 칼로리</div>
          </div>

          <div className="detail-info">
            <h3>계산 세부 정보</h3>

            <div className="detail-row">
              <span>방식:</span>
              <span className="detail-value">{mode}</span>
            </div>

            {mode === "MET" && (
              <>
                <div className="detail-row">
                  <span>운동:</span>
                  <span className="detail-value">{selectedExercise}</span>
                </div>

                <div className="detail-row">
                  <span>MET 값:</span>
                  <span className="detail-value">{metValues[selectedExercise]}</span>
                </div>
              </>
            )}

            {mode === "HR" && (
              <>
                <div className="detail-row">
                  <span>나이:</span>
                  <span className="detail-value">{age}</span>
                </div>
                <div className="detail-row">
                  <span>성별:</span>
                  <span className="detail-value">{gender}</span>
                </div>
                <div className="detail-row">
                  <span>심박수:</span>
                  <span className="detail-value">{heartRate} bpm</span>
                </div>
              </>
            )}

            <div className="detail-row">
              <span>무게:</span>
              <span className="detail-value">
                {weight} {unit}
              </span>
            </div>

            <div className="detail-row">
              <span>운동 시간:</span>
              <span className="detail-value">{customDuration || duration} min</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CalorieCalculator;
