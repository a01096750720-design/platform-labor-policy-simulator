import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="배달 플랫폼 노동 정책 시뮬레이터", page_icon="🛵", layout="wide")

st.title("🛵 배달 플랫폼 노동 정책 시뮬레이터")
st.caption("대기시간 보상·배달 수수료·플랫폼 수수료율을 바꾸며 노동자 소득과 플랫폼 비용 변화를 비교하는 탐구용 도구")

st.markdown("""
이 시뮬레이터는 **플랫폼 노동 문제를 정보 비대칭·협상력 불균형·시장실패 관점에서 분석**하기 위해 만든 간단한 모형입니다.  
실제 임금 산정 도구가 아니라, 정책 조건이 바뀔 때 어떤 경제적 결과가 달라지는지 비교하는 **탐구용 시뮬레이션**입니다.
""")

with st.expander("📌 탐구 질문 보기", expanded=True):
    st.markdown("""
    **탐구 질문**  
    플랫폼 경제에서 배달 노동자의 노동 조건은 어떻게 결정되며, 정보 비대칭과 협상력 불균형은 시장실패로 이어질 수 있는가?

    **분석 흐름**  
    배달 플랫폼 확산 → 알고리즘 배차·평점·대기시간 문제 → 정보 비대칭과 협상력 불균형 → 시장실패 가능성 → 정책 개입 필요성 검토
    """)

st.sidebar.header("⚙️ 기본 조건 설정")

orders_per_day = st.sidebar.slider("하루 배달 건수", 5, 60, 25, 1)
fee_per_order = st.sidebar.slider("배달 1건당 노동자 수수료(원)", 2000, 8000, 3500, 100)
working_hours = st.sidebar.slider("하루 앱 접속/노동 시간(시간)", 2.0, 14.0, 8.0, 0.5)
wait_minutes_per_order = st.sidebar.slider("배달 1건당 평균 대기시간(분)", 0, 30, 10, 1)
platform_commission_rate = st.sidebar.slider("플랫폼 수수료율 또는 관리비율(%)", 0, 40, 15, 1)
accident_risk_cost = st.sidebar.slider("노동자 부담 위험비용 추정치(원/일)", 0, 30000, 5000, 1000)

st.sidebar.header("🧪 정책 조건 설정")
wait_compensation_rate = st.sidebar.slider("대기시간 보상률(%)", 0, 100, 30, 5)
algorithm_transparency = st.sidebar.slider("알고리즘 투명성 수준(0~100)", 0, 100, 40, 5)
industrial_accident_support = st.sidebar.slider("산재·안전 지원 수준(0~100)", 0, 100, 50, 5)

# Calculations
wait_hours = orders_per_day * wait_minutes_per_order / 60
base_income = orders_per_day * fee_per_order
wait_hourly_value = fee_per_order * 1.2  # simple model: waiting hour valued by average opportunity cost
wait_compensation = wait_hours * wait_hourly_value * (wait_compensation_rate / 100)
risk_support = accident_risk_cost * (industrial_accident_support / 100)
worker_net_income = base_income + wait_compensation + risk_support - accident_risk_cost
current_worker_income = base_income - accident_risk_cost

platform_revenue_proxy = base_income * (1 + platform_commission_rate / 100)
platform_current_cost = base_income
platform_policy_cost = base_income + wait_compensation + risk_support
platform_extra_cost = platform_policy_cost - platform_current_cost

current_hourly_wage = current_worker_income / working_hours if working_hours else 0
policy_hourly_wage = worker_net_income / working_hours if working_hours else 0

# Indices
worker_satisfaction = min(5, max(1, 1 + (wait_compensation_rate / 30) + (industrial_accident_support / 40)))
company_burden = min(5, max(1, 1 + (platform_extra_cost / max(base_income, 1)) * 10))
market_sustainability = min(5, max(1, 2 + (algorithm_transparency / 40) + (industrial_accident_support / 80) - (company_burden - 2) * 0.25))

col1, col2, col3, col4 = st.columns(4)
col1.metric("현재 제도 노동자 순소득", f"{current_worker_income:,.0f}원")
col2.metric("정책 적용 노동자 순소득", f"{worker_net_income:,.0f}원", f"{worker_net_income - current_worker_income:,.0f}원")
col3.metric("현재 추정 시급", f"{current_hourly_wage:,.0f}원")
col4.metric("정책 적용 추정 시급", f"{policy_hourly_wage:,.0f}원", f"{policy_hourly_wage - current_hourly_wage:,.0f}원")

st.divider()

left, right = st.columns([1.2, 1])

with left:
    st.subheader("📊 현재 제도 vs 제안 정책 비교")
    comparison = pd.DataFrame({
        "항목": ["노동자 순소득", "노동자 추정 시급", "플랫폼 비용", "플랫폼 추가 부담", "대기시간 보상", "위험비용 보전"],
        "현재 제도": [current_worker_income, current_hourly_wage, platform_current_cost, 0, 0, 0],
        "제안 정책": [worker_net_income, policy_hourly_wage, platform_policy_cost, platform_extra_cost, wait_compensation, risk_support],
    })
    st.dataframe(comparison.style.format({"현재 제도": "{:,.0f}", "제안 정책": "{:,.0f}"}), use_container_width=True)

with right:
    st.subheader("🧭 정책 평가")
    def stars(x):
        return "★" * int(round(x)) + "☆" * (5 - int(round(x)))

    st.write(f"**노동자 만족도** {stars(worker_satisfaction)}")
    st.write(f"**기업 부담** {stars(company_burden)}")
    st.write(f"**시장 지속가능성** {stars(market_sustainability)}")

    if wait_compensation_rate == 0:
        st.warning("대기시간 보상이 없어 노동자의 실제 노동시간이 소득에 충분히 반영되지 않을 수 있습니다.")
    elif wait_compensation_rate < 30:
        st.info("대기시간 일부 보상으로 노동자 소득은 개선되지만, 보상 수준은 제한적입니다.")
    else:
        st.success("대기시간 보상이 확대되어 노동자 소득과 공정성이 개선되는 방향입니다.")

    if company_burden >= 4:
        st.warning("기업 부담이 높아 소비자 가격 상승 또는 플랫폼 운영비 증가 가능성을 함께 고려해야 합니다.")

st.divider()

st.subheader("📈 대기시간 보상률 변화에 따른 결과")

rates = list(range(0, 105, 5))
rows = []
for r in rates:
    wc = wait_hours * wait_hourly_value * (r / 100)
    income = base_income + wc + risk_support - accident_risk_cost
    platform_cost = base_income + wc + risk_support
    rows.append({"대기시간 보상률(%)": r, "노동자 순소득": income, "플랫폼 비용": platform_cost})
scenario_df = pd.DataFrame(rows)

chart_tab1, chart_tab2 = st.tabs(["선그래프", "데이터 표"])
with chart_tab1:
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(scenario_df["대기시간 보상률(%)"], scenario_df["노동자 순소득"], marker="o", label="노동자 순소득")
    ax.plot(scenario_df["대기시간 보상률(%)"], scenario_df["플랫폼 비용"], marker="o", label="플랫폼 비용")
    ax.set_xlabel("대기시간 보상률(%)")
    ax.set_ylabel("금액(원/일)")
    ax.set_title("대기시간 보상률 변화에 따른 노동자 소득과 플랫폼 비용")
    ax.grid(True, alpha=0.3)
    ax.legend()
    st.pyplot(fig)

with chart_tab2:
    st.dataframe(scenario_df.style.format({"노동자 순소득": "{:,.0f}", "플랫폼 비용": "{:,.0f}"}), use_container_width=True)

st.divider()

st.subheader("📝 보고서에 쓸 수 있는 해석 문장")

interpretation = f"""
본 시뮬레이션에서 하루 배달 건수 {orders_per_day}건, 건당 수수료 {fee_per_order:,.0f}원, 평균 대기시간 {wait_minutes_per_order}분을 기준으로 설정했을 때, 
대기시간 보상률을 {wait_compensation_rate}%로 적용하면 노동자의 하루 순소득은 {current_worker_income:,.0f}원에서 {worker_net_income:,.0f}원으로 변화하였다. 
이는 대기시간이 단순한 휴식 시간이 아니라 실제 노동 과정에 포함될 수 있음을 보여준다. 
다만 플랫폼 비용 역시 {platform_current_cost:,.0f}원에서 {platform_policy_cost:,.0f}원으로 증가하므로, 노동자 보호와 기업의 지속가능성을 함께 고려한 균형적 제도 설계가 필요하다.
"""
st.text_area("해석 문장", interpretation.strip(), height=170)

st.download_button(
    label="📥 시뮬레이션 결과 CSV 다운로드",
    data=scenario_df.to_csv(index=False).encode("utf-8-sig"),
    file_name="platform_labor_simulation_results.csv",
    mime="text/csv",
)

st.caption("※ 이 모델은 실제 플랫폼 수익 구조를 단순화한 교육·탐구용 시뮬레이션입니다. 실제 정책 분석에는 더 많은 자료와 검증이 필요합니다.")
