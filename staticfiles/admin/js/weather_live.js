// static/admin/js/weather_live.js
// 어드민에서 실시간 날씨 조회 기능

function getLiveWeather(latitude, longitude) {
    // 로딩 표시
    const button = event.target;
    const originalText = button.textContent;
    button.textContent = "🔄 조회 중...";
    button.disabled = true;
    
    // WeatherAPIClient 호출 (Django 뷰를 통해)
    fetch(`/api/weather/?lat=${latitude}&lon=${longitude}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 팝업으로 결과 표시
                showWeatherPopup(data.weather, data.location);
            } else {
                alert("날씨 데이터를 가져올 수 없습니다: " + (data.error || "알 수 없는 오류"));
            }
        })
        .catch(error => {
            alert("API 호출 실패: " + error.message);
        })
        .finally(() => {
            // 버튼 원상복구
            button.textContent = originalText;
            button.disabled = false;
        });
}

function showWeatherPopup(weatherData, location) {
    // 날씨 정보를 예쁘게 포맷해서 팝업으로 표시
    let content = `
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <h3>🌤️ ${location} 실시간 날씨</h3>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                    <h4 style="margin-top: 0; color: #495057;">현재 날씨</h4>
                    <p><strong>🌡️ 기온:</strong> ${weatherData.current?.temperature || 'N/A'}°C</p>
                    <p><strong>💧 습도:</strong> ${weatherData.current?.humidity || 'N/A'}%</p>
                    <p><strong>🌡️ 체감온도:</strong> ${weatherData.details?.feels_like || 'N/A'}°C</p>
                    <p><strong>☀️ 자외선:</strong> ${weatherData.details?.uv_index || 'N/A'} (${weatherData.details?.uv_level || 'N/A'})</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                    <h4 style="margin-top: 0; color: #495057;">대기질</h4>
                    <p><strong>🌫️ PM2.5:</strong> ${weatherData.air_quality?.pm25?.value || 'N/A'}μg/m³ (${weatherData.air_quality?.pm25?.grade || 'N/A'})</p>
                    <p><strong>🌫️ PM10:</strong> ${weatherData.air_quality?.pm10?.value || 'N/A'}μg/m³ (${weatherData.air_quality?.pm10?.grade || 'N/A'})</p>
                    <p><strong>🌅 일출:</strong> ${weatherData.details?.sunrise || 'N/A'}</p>
                    <p><strong>🌇 일몰:</strong> ${weatherData.details?.sunset || 'N/A'}</p>
                </div>
            </div>
            
            <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin-top: 20px;">
                <h4 style="margin-top: 0; color: #1976d2;">💡 여행 팁</h4>
                <p><strong>메시지:</strong> ${weatherData.travel_tip?.message || '야외활동하기 좋은 날씨입니다.'}</p>
                <p><strong>옷차림:</strong> ${weatherData.travel_tip?.clothing || '적당한 옷차림'}</p>
            </div>
            
            <div style="text-align: center; margin-top: 20px; font-size: 12px; color: #6c757d;">
                마지막 업데이트: ${weatherData.last_updated || new Date().toLocaleString()}
            </div>
        </div>
    `;
    
    // 팝업 생성
    const popup = window.open('', '실시간날씨', 'width=600,height=500,scrollbars=yes,resizable=yes');
    popup.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>실시간 날씨 정보</title>
            <meta charset="utf-8">
        </head>
        <body style="margin: 20px;">
            ${content}
            <div style="text-align: center; margin-top: 30px;">
                <button onclick="window.close()" style="background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">닫기</button>
            </div>
        </body>
        </html>
    `);
    popup.document.close();
}

// 페이지 로드 시 스타일 추가
document.addEventListener('DOMContentLoaded', function() {
    // 실시간 날씨 조회 버튼 스타일 개선
    const weatherButtons = document.querySelectorAll('a[onclick*="getLiveWeather"]');
    weatherButtons.forEach(button => {
        button.style.cssText = `
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 5px 10px;
            border-radius: 4px;
            text-decoration: none;
            font-size: 11px;
            font-weight: 500;
            display: inline-block;
            transition: all 0.3s ease;
        `;
        
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-1px)';
            this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });
});
