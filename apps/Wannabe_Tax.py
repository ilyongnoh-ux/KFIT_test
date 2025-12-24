import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import json
from utils import send_data_to_api, render_common_form # [NEW]
from models import TaxData  # 모델 사용

def app(input_col):
    # ==========================================
    # CSS 스타일링 (원본 100% 유지)
    # ==========================================
    st.markdown("""
    <style>
    .main { background-color: #0E1117 !important; color: #FAFAFA !important; }
    html, body, [class*="css"], .stMarkdown, .stButton, .stNumberInput, .stSlider, .stTextInput, .stTextArea {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 16px !important;
    }
    .title-container { width: 100%; text-align: center; margin-bottom: 20px; padding: 10px 0; }
    .responsive-title {
        font-weight: 900; color: #4CAF50; white-space: nowrap;
        font-size: clamp(1.8rem, 6vw, 3.5rem); line-height: 1.2;
    }
    .sidebar-container { width: 100%; margin-bottom: 10px; text-align: center; }
    .responsive-sidebar-title {
        font-weight: 800; color: #4CAF50; white-space: nowrap;
        font-size: clamp(1.2rem, 13cqw, 2rem); 
        line-height: 1.2;
    }
    .big-number-box {
        background-color: #1F2937; padding: 2vw; border-radius: 12px;
        border: 1px solid #374151; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 10px; min-height: 140px;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        container-type: inline-size; 
    }
    .big-number-label { color: #E5E7EB; font-weight: 600; white-space: nowrap; font-size: clamp(0.8rem, 5cqw, 1.2rem); margin-bottom: 5px; }
    .big-number-value { color: #FAFAFA; font-weight: 800; line-height: 1.1; white-space: nowrap; font-size: clamp(1.2rem, 15cqw, 3.5rem); }
    .sub-text-wrapper { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width: 100%; }
    .sub-text-positive { color: #4ADE80; font-weight: bold; font-size: clamp(0.7rem, 4cqw, 1rem); margin-top: 5px; }
    .sub-text-negative { color: #FF7F50; font-weight: bold; font-size: clamp(0.7rem, 4cqw, 1rem); margin-top: 5px; }
    .sub-text-highlight { color: #FFFF00; font-weight: 800; text-shadow: 0px 0px 5px rgba(255, 255, 0, 0.3); font-size: clamp(0.8rem, 5cqw, 1.3rem); margin-top: 5px; }
    .val-positive { color: #34D399; } 
    .val-negative { color: #F87171; } 
    .warning-box { background-color: #450a0a; color: #fca5a5; padding: 20px; border-radius: 12px; border-left: 8px solid #ef4444; margin-top: 20px; line-height: 1.5; font-size: clamp(0.9rem, 1.5vw, 1.2rem); }
    .safe-box { background-color: #064e3b; color: #6ee7b7; padding: 20px; border-radius: 12px; border-left: 8px solid #10b981; margin-top: 20px; line-height: 1.5; font-size: clamp(0.9rem, 1.5vw, 1.2rem); }
    .stSlider label p, .stNumberInput label p, .stToggle label p, .stTextInput label p, .stTextArea label p {
        font-size: clamp(0.8rem, 1.2vw, 1.1rem) !important;
        white-space: nowrap !important;
    }
    .stCheckbox label p {
        font-size: clamp(11px, 4.5cqw, 14px) !important;
        white-space: nowrap !important; 
        width: 100%;
        overflow: visible;
    }
    </style>
    """, unsafe_allow_html=True)

    # ==========================================
    # 함수 정의
    # ==========================================
    def calculate_tax(tax_base):
        if tax_base <= 0: return 0
        elif tax_base <= 100000000: return tax_base * 0.1
        elif tax_base <= 500000000: return tax_base * 0.2 - 10000000
        elif tax_base <= 1000000000: return tax_base * 0.3 - 60000000
        elif tax_base <= 3000000000: return tax_base * 0.4 - 160000000
        else: return tax_base * 0.5 - 460000000

    def format_krw_display(value):
        eok = value / 100000000
        return f"{eok:,.1f}억"

    # ==========================================
    # [왼쪽 프레임] 입력창 구성 (상담폼 제거됨)
    # ==========================================
    with input_col:
        st.markdown("""
            <div class="sidebar-container">
                <div class="responsive-sidebar-title">🧮 Client Info</div>
            </div>
        """, unsafe_allow_html=True)
        #st.markdown("---")
        
        # 1. 자산 입력
        st.markdown("#### 1️⃣ 현재 자산 (부모님)")
        real_estate_billions = st.number_input("🏠 부동산 (단위: 억)", value=30, step=1)
        financial_billions = st.number_input("💰 금융/동산 (단위: 억)", value=10, step=1)
        total_estate = (real_estate_billions + financial_billions) * 100000000
        
        st.markdown("---")
        
        # 2. 가정 설정
        st.markdown("#### 2️⃣ 시뮬레이션 가정")
        has_spouse = st.toggle("배우자 생존 여부", value=True)
        
        if has_spouse:
            slider_years_label = "배우자 예상 생존 기간 (년)"
            pct_disabled = False
        else:
            slider_years_label = "시뮬레이션 기간 (본인 생존 가정)"
            pct_disabled = True
            
        spouse_share_pct = st.slider("배우자 상속 비율 (%)", 0, 100, 60, disabled=pct_disabled)
        sim_years = st.slider(slider_years_label, 0, 40, 20)
        
        st.markdown("---")
        
        # 3. 미래 변수
        st.markdown("#### 3️⃣ 미래 변수 (복리)")
        inflation_real_estate = st.slider("부동산 연 상승률 (%)", 0, 10, 5, step=1) / 100
        inflation_financial = st.slider("금융자산 연 수익률 (%)", 0, 10, 2, step=1) / 100

        # [삭제됨] 상담 신청 폼은 여기서 제거되어 오른쪽 하단으로 이동했습니다.

    # ==========================================
    # 메인 로직 및 계산
    # ==========================================
    basic_deduction = 500000000 
    spouse_deduction = 0

    if not has_spouse:
        spouse_share_pct = 0 

    if has_spouse:
        actual_spouse_take = total_estate * (spouse_share_pct / 100)
        spouse_deduction = min(max(actual_spouse_take, 500000000), 3000000000)

    tax_base_1_now = total_estate - basic_deduction - spouse_deduction
    tax_1_now = calculate_tax(tax_base_1_now)

    years = list(range(sim_years + 1))
    assets_re = []
    assets_fin = []
    taxes = []
    crisis_year = None
    shortage_amount = 0

    if has_spouse:
        simulation_title = "배우자 기준 2차 상속세 (Liquidity Death Cross)"
        simulation_desc = "※ 그래프 시작점: 1차 납부 후 배우자가 받은 몫"
        
        net_estate_1 = total_estate - tax_1_now
        curr_re_val = (net_estate_1 * (spouse_share_pct/100)) * (real_estate_billions / (real_estate_billions+financial_billions) if total_estate > 0 else 0)
        curr_fin_val = (net_estate_1 * (spouse_share_pct/100)) - curr_re_val
        deduction_future = 500000000
    else:
        simulation_title = "미래 시점 1차 상속세 (유동성 분석)"
        simulation_desc = "※ 본인 자산 성장 후 자녀 부담 상속세 변화"
        
        curr_re_val = real_estate_billions * 100000000
        curr_fin_val = financial_billions * 100000000
        deduction_future = 500000000 

    for y in years:
        curr_total = curr_re_val + curr_fin_val
        curr_base = curr_total - deduction_future
        curr_tax = calculate_tax(curr_base)
        
        assets_re.append(curr_re_val)
        assets_fin.append(curr_fin_val)
        taxes.append(curr_tax)
        
        if curr_tax > curr_fin_val and crisis_year is None:
            crisis_year = y
            shortage_amount = curr_tax - curr_fin_val
        
        curr_re_val *= (1 + inflation_real_estate)
        curr_fin_val *= (1 + inflation_financial)

    final_tax_simulated = taxes[-1]
    final_financial_simulated = assets_fin[-1]
    final_total_asset_simulated = assets_re[-1] + assets_fin[-1]

    liquidity_crisis = True if crisis_year is not None else False
    shortage = final_tax_simulated - final_financial_simulated if liquidity_crisis else 0

    # ==========================================
    # 6. [오른쪽 프레임] 메인 리포트 UI
    # ==========================================
    st.markdown("""
        <div class="title-container">
            <div class="responsive-title">⛳ Inheritance Tax Simulation</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        deduction_msg = "✅ 배우자 공제 적용" if has_spouse else "ℹ️ 일괄 공제만 적용"
        st.markdown(f"""
            <div class="big-number-box">
                <div class="big-number-label">현재 사망 시 상속세</div>
                <div class="big-number-value val-positive">{format_krw_display(tax_1_now)}</div>
                <div class="sub-text-wrapper sub-text-positive">{deduction_msg}</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        if has_spouse:
            box_label = f"2차 상속세 ({sim_years}년 후)"
            sub_msg = "🚨 배우자 공제 소멸!"
        else:
            box_label = f"미래 상속세 ({sim_years}년 후)"
            sub_msg = "📈 자산 가치 상승 반영"

        st.markdown(f"""
            <div class="big-number-box" style="border-color: #EF4444;">
                <div class="big-number-label">{box_label}</div>
                <div class="big-number-value val-negative">{format_krw_display(final_tax_simulated)}</div>
                <div class="sub-text-wrapper sub-text-negative">{sub_msg}</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        if has_spouse:
            total_burden = tax_1_now + final_tax_simulated
            ratio_desc = "원금 대비 총 세금"
            tax_ratio = (total_burden / total_estate * 100) if total_estate > 0 else 0
        else:
            total_burden = final_tax_simulated 
            ratio_desc = f"{sim_years}년 후 자산 대비"
            tax_ratio = (total_burden / final_total_asset_simulated * 100) if final_total_asset_simulated > 0 else 0

        st.markdown(f"""
            <div class="big-number-box">
                <div class="big-number-label">총 납부 예상액</div>
                <div class="big-number-value">{format_krw_display(total_burden)}</div>
                <div class="sub-text-wrapper sub-text-highlight">{ratio_desc}: 약 {tax_ratio:.1f}%</div>
            </div>
        """, unsafe_allow_html=True)

    # --- [유동성 경고 메시지] ---
    if liquidity_crisis:
        if has_spouse:
            crisis_context = "2차 상속 시"
            subject = "자녀들이"
        else:
            crisis_context = "미래 시점 상속 시"
            subject = "자녀들이"

        final_shortage = final_tax_simulated - final_financial_simulated

        if final_shortage > 0:
            st.markdown(f"""
            <div class="warning-box">
                <h3>🚨 WARNING: 유동성 위기 (흑자 부도)</h3>
                <p>
                    <strong>{sim_years}년 뒤 {crisis_context}</strong>, {subject} 내야 할 세금은 <strong>{format_krw_display(final_tax_simulated)}</strong>입니다.<br>
                    하지만 그때 가용 가능한 현금은 <strong>{format_krw_display(final_financial_simulated)}</strong> 뿐입니다.<br>
                    <br>
                    <span style="font-size: clamp(1rem, 2vw, 1.5rem); font-weight: bold; color: #FFF; background-color: #ef4444; padding: 5px 10px; border-radius: 5px; white-space: nowrap;">
                    부족한 현금: {format_krw_display(final_shortage)}
                    </span>
                    <br><br>
                    👉 <strong>그래프의 빨간 막대가 파란색 영역을 뚫고 올라갔습니다.</strong><br>
                    부동산을 급매하거나 재원을 미리 마련해야 합니다.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
             st.markdown(f"""
             <div class="warning-box">
                <h3>⚠️ CAUTION: 일시적 위험</h3>
                <p>{crisis_year}년차 즈음에 일시적으로 세금이 보유 현금을 초과할 수 있습니다.</p>
             </div>
             """, unsafe_allow_html=True)

    else:
        st.markdown(f"""
        <div class="safe-box">
            <h3>✅ SAFE: 유동성 양호</h3>
            <p>예상되는 상속세보다 보유 현금이 더 많습니다.<br>(그래프의 빨간 막대가 파란 영역 내에 안정적으로 존재합니다.)</p>
        </div>
        """, unsafe_allow_html=True)

    # ==========================================
    # 7. 차트 시각화
    # ==========================================
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"### 🎯 {simulation_title}")
    st.caption(simulation_desc)

    df_chart = pd.DataFrame({
        "Year": years,
        "RealEstate": [x / 100000000 for x in assets_re],
        "Financial": [x / 100000000 for x in assets_fin],
        "Tax": [x / 100000000 for x in taxes]
    })

    fig = go.Figure()

# 1. 배경: 총 자산
    fig.add_trace(go.Scatter(
        x=df_chart["Year"],
        y=df_chart["RealEstate"] + df_chart["Financial"],
        mode='lines',
        name='총 자산',
        line=dict(width=1, color='rgba(160, 160, 160, 0.5)'),
        fill='tozeroy',
        fillcolor='rgba(128, 128, 128, 0.3)',
        # 🔧 여기 수정: hoverinfo 대신 hovertemplate 사용
        hovertemplate="<b>%{x}년 후</b><br>총자산: %{y:.1f}억<extra></extra>"
    ))


    # 2. 기준선: 금융자산 (보유 현금)
    fig.add_trace(go.Scatter(
        x=df_chart["Year"], y=df_chart["Financial"],
        mode='lines', name='보유 현금',
        line=dict(width=4, color='#00BFFF', dash='solid'),
        hovertemplate='보유현금: %{y:.1f}억<extra></extra>'
    ))

    # 3. 막대: 상속세
    fig.add_trace(go.Bar(
        x=df_chart["Year"], y=df_chart["Tax"],
        name='예상 상속세',
        marker_color='#EF4444', opacity=0.9,
        hovertemplate='예상상속세: %{y:.1f}억<extra></extra>'
    ))

    # 4. 핀포인트 텍스트
    if liquidity_crisis and crisis_year is not None:
        crisis_tax_val = df_chart.loc[crisis_year, "Tax"]
        fig.add_annotation(
            x=crisis_year,
            y=crisis_tax_val,
            text=f"🚨 <b>{crisis_year}년후 부족!</b>",
            showarrow=True, arrowhead=2, arrowsize=2.0, arrowwidth=2, arrowcolor="#FFFF00",
            ax=0, ay=-40, bgcolor="#0054FF", bordercolor="#FFFF00",
            font=dict(size=15, color="white", family="sans-serif")
        )

    # 차트 레이아웃
    fig.update_layout(
        template="plotly_dark", height=550,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=120, b=50, l=20, r=20),
        xaxis=dict(title="경과 기간(년)", fixedrange=True, tickmode='linear', tick0=0, dtick=5, showgrid=True, gridcolor='#374151'),
        yaxis=dict(title="금액 단위(억원)", fixedrange=True, tickformat=".1f", showgrid=True, gridcolor='#374151'),
        dragmode=False,
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.info("""
    💡 **그래프 해석 가이드**:
    1. **회색 산**: 전체 자산 규모
    2. **파란 선**: 세금 낼 수 있는 현금 능력
    3. **빨간 막대**: 자녀가 낼 세금 (빨간 막대가 파란 선을 넘으면 위험)
    """)

    # --------------------------------------------------------------------------
    # [수정됨] 공통 상담 폼 호출 + 진단 결과 데이터 추가 저장
    # --------------------------------------------------------------------------
    render_common_form(
        app_type="tax",
        DataModelClass=TaxData,
        
        # 1. 사용자 입력 데이터 (Input)
        real_estate_billions=real_estate_billions,
        financial_billions=financial_billions,
        total_estate_eok=total_estate/100000000,
        has_spouse_str="있음" if has_spouse else "없음",
        spouse_pct=spouse_share_pct if has_spouse else 0,
        sim_years=sim_years,
        inflation_re_pct=inflation_real_estate * 100,
        inflation_fin_pct=inflation_financial * 100,

        # 2. [NEW] 시뮬레이션 진단 결과 데이터 (Output)
        # 이 값들이 구글 시트/DB에 함께 저장됩니다.
        calculated_tax_now=tax_1_now,                       # 현재 기준 예상 상속세 (원)
        calculated_future_tax=final_tax_simulated,          # 미래 예상 상속세 (원)
        calculated_future_cash=final_financial_simulated,   # 미래 가용 현금 (원)
        is_liquidity_crisis="위험(흑자부도)" if liquidity_crisis else "안전", # 유동성 위기 여부
        shortage_amount=shortage                            # 부족한 현금 액수 (원)
    )
