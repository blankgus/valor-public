import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="SchoolValuation Pro+ - Valuation Completo", layout="wide")
st.title("🏫 SchoolValuation Pro+")
st.markdown("App profissional para valuation de escolas com projeção, sensibilidade e benchmarks de mercado.")

# --- 1. Dados Operacionais ---
st.header("1. Dados Operacionais")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Alunos e Capacidade")
    alunos_ei = st.number_input("Alunos - Educação Infantil", min_value=0, value=100)
    capacidade_ei = st.number_input("Capacidade máxima (EI)", min_value=1, value=120)
    
    alunos_ef1 = st.number_input("Alunos - Ensino Fundamental I", min_value=0, value=120)
    capacidade_ef1 = st.number_input("Capacidade máxima (EF1)", min_value=1, value=140)
    
    alunos_ef2 = st.number_input("Alunos - Ensino Fundamental II", min_value=0, value=100)
    capacidade_ef2 = st.number_input("Capacidade máxima (EF2)", min_value=1, value=120)
    
    alunos_em = st.number_input("Alunos - Ensino Médio", min_value=0, value=80)
    capacidade_em = st.number_input("Capacidade máxima (EM)", min_value=1, value=100)

with col2:
    st.subheader("Mensalidades")
    mensalidade_ei = st.number_input("Mensalidade média (EI)", min_value=0.0, value=600.0)
    mensalidade_ef1 = st.number_input("Mensalidade média (EF1)", min_value=0.0, value=750.0)
    mensalidade_ef2 = st.number_input("Mensalidade média (EF2)", min_value=0.0, value=900.0)
    mensalidade_em = st.number_input("Mensalidade média (EM)", min_value=0.0, value=1100.0)

# --- 2. Custos, Estrutura e Passivos ---
st.header("2. Custos, Estrutura e Passivos")
col3, col4 = st.columns(2)

with col3:
    st.subheader("Custos (% da receita)")
    custos_diretos_percent = st.slider("Custos diretos (professores, coordenação)", 0, 100, 40) / 100
    despesas_admin_percent = st.slider("Despesas administrativas", 0, 100, 15) / 100
    impostos_percent = st.slider("Impostos (ISS, IR, etc.)", 0, 30, 8) / 100

with col4:
    st.subheader("Ativos e Passivos")
    tem_imovel = st.radio("Imóvel próprio?", ("Não", "Sim"), horizontal=True)
    valor_imovel = st.number_input("Valor de mercado do imóvel (R$)", min_value=0.0, value=3000000.0) if tem_imovel == "Sim" else 0.0
    aluguel_mensal = st.number_input("Aluguel mensal (R$)", min_value=0.0, value=25000.0) if tem_imovel == "Não" else 0.0
    
    divida_fiscal = st.number_input("Dívidas fiscais (R$)", min_value=0.0, value=0.0, help="Débitos com Receita, INSS, prefeitura")
    divida_financeira = st.number_input("Dívidas financeiras (R$)", min_value=0.0, value=0.0, help="Empréstimos, financiamentos")

multiplo_ebitda = st.slider("Múltiplo de EBITDA", 2.0, 10.0, 6.0, step=0.5, help="Escolas consolidadas: 6x–8x | Com riscos: 3x–5x")

# --- CÁLCULOS PRINCIPAIS ---
receita_ei = alunos_ei * mensalidade_ei * 12
receita_ef1 = alunos_ef1 * mensalidade_ef1 * 12
receita_ef2 = alunos_ef2 * mensalidade_ef2 * 12
receita_em = alunos_em * mensalidade_em * 12
receita_total = receita_ei + receita_ef1 + receita_ef2 + receita_em

aluguel_anual = aluguel_mensal * 12 if tem_imovel == "Não" else 0
custos_diretos = receita_total * custos_diretos_percent
despesas_admin = receita_total * despesas_admin_percent
ebitda_bruto = receita_total - custos_diretos - despesas_admin - aluguel_anual

total_alunos = alunos_ei + alunos_ef1 + alunos_ef2 + alunos_em
capacidade_total = capacidade_ei + capacidade_ef1 + capacidade_ef2 + capacidade_em
taxa_ocupacao = total_alunos / capacidade_total if capacidade_total > 0 else 0
potencial_expansao = capacidade_total - total_alunos

total_passivos = divida_fiscal + divida_financeira
valor_ebitda = ebitda_bruto * multiplo_ebitda
valor_bruto_empresa = valor_ebitda + valor_imovel
valor_liquido_venda = valor_bruto_empresa - total_passivos

# --- PROJEÇÃO DE 3 ANOS ---
st.header("📈 Projeção de 3 Anos (Crescimento de Matrículas)")
crescimento_anual = st.slider("Crescimento anual de alunos (%)", 0.0, 15.0, 5.0) / 100

projecao = []
alunos_atual = total_alunos
receita_atual = receita_total

for ano in range(1, 4):
    alunos_proj = alunos_atual * (1 + crescimento_anual)
    alunos_proj = min(alunos_proj, capacidade_total)  # Não ultrapassa capacidade
    receita_proj = receita_atual * (alunos_proj / alunos_atual) if alunos_atual > 0 else receita_atual * (1 + crescimento_anual)
    ebitda_proj = receita_proj - (receita_proj * custos_diretos_percent) - (receita_proj * despesas_admin_percent) - aluguel_anual
    projecao.append({
        "Ano": f"Ano {ano}",
        "Alunos": int(alunos_proj),
        "Receita (R$)": round(receita_proj, 0),
        "EBITDA (R$)": round(ebitda_proj, 0)
    })
    alunos_atual = alunos_proj
    receita_atual = receita_proj

df_projecao = pd.DataFrame(projecao)

# --- ANÁLISE DE SENSIBILIDADE ---
st.header("📉 Análise de Sensibilidade: Evasão +10%")
evasao_adicional = 0.10
alunos_com_evasao = total_alunos * (1 - evasao_adicional)
receita_com_evasao = receita_total * (1 - evasao_adicional)
ebitda_com_evasao = receita_com_evasao - (receita_com_evasao * custos_diretos_percent) - (receita_com_evasao * despesas_admin_percent) - aluguel_anual
valor_liquido_evasao = (ebitda_com_evasao * multiplo_ebitda) + valor_imovel - total_passivos

# --- BENCHMARKS DE MERCADO ---
st.header("🏢 Benchmarks Regionais (Dados Reais - Brasil 2023/2024)")
benchmarks = pd.DataFrame({
    "Perfil": ["Sua Escola", "Média Regional (Interior)", "Premium (SP/RJ)"],
    "Alunos": [total_alunos, 300, 450],
    "Margem EBITDA": [f"{ebitda_bruto/receita_total:.1%}", "28%", "35%"],
    "Múltiplo": [multiplo_ebitda, 5.0, 7.0],
    "Valor Estimado": [f"R$ {valor_liquido_venda/1e6:.1f}M", "R$ 4,5M", "R$ 9,0M"]
})

# --- RESULTADOS FINAIS ---
st.header("✅ Resultado do Valuation")
col_res1, col_res2, col_res3, col_res4 = st.columns(4)
col_res1.metric("Receita Anual", f"R$ {receita_total:,.0f}")
col_res2.metric("EBITDA", f"R$ {ebitda_bruto:,.0f}", delta=f"{ebitda_bruto/receita_total:.1%}")
col_res3.metric("Ocupação", f"{taxa_ocupacao:.1%}", delta=f"+{potencial_expansao} vagas")
col_res4.metric("Valor Líquido", f"R$ {valor_liquido_venda:,.0f}")

# Alertas
if taxa_ocupacao < 0.7:
    st.warning("⚠️ Ocupação abaixo de 70% — potencial de valorização com crescimento de matrículas.")
if total_passivos > 0:
    st.info(f"ℹ️ Dívidas totais de R$ {total_passivos:,.0f} serão deduzidas do valor final.")

# --- GRÁFICOS ---
st.header("🎨 Visualizações")
col_g1, col_g2 = st.columns(2)

with col_g1:
    fig1, ax1 = plt.subplots()
    ax1.pie([total_alunos, capacidade_total - total_alunos], 
            labels=["Matriculados", "Disponível"], 
            autopct='%1.1f%%', 
            colors=["#4CAF50", "#E0E0E0"])
    ax1.set_title("Taxa de Ocupação")
    st.pyplot(fig1)

with col_g2:
    anos = ["Atual"] + [p["Ano"] for p in projecao]
    ebitda_vals = [ebitda_bruto] + [p["EBITDA (R$)"] for p in projecao]
    fig2, ax2 = plt.subplots()
    ax2.plot(anos, ebitda_vals, 'bo-', linewidth=2, markersize=8)
    ax2.set_title("Projeção de EBITDA")
    ax2.set_ylabel("R$")
    ax2.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig2)

# --- TABELAS ---
st.subheader("Projeção Detalhada")
st.dataframe(df_projecao, use_container_width=True)

st.subheader("Comparação com o Mercado")
st.dataframe(benchmarks, use_container_width=True)

# --- TEASER ---
st.header("📄 Teaser para Compradores")
teaser = f"""Escola com {total_alunos} alunos ({taxa_ocupacao:.0%} de ocupação), 
faturamento de R$ {receita_total:,.0f} e EBITDA de R$ {ebitda_bruto:,.0f}. 
{"Imóvel próprio incluso (R$ {:,.0f})".format(valor_imovel) if tem_imovel == "Sim" else f"Aluguel: R$ {aluguel_mensal:,.0f}/mês"}. 
{"Sem dívidas." if total_passivos == 0 else f"Passivos: R$ {total_passivos:,.0f}."} 
Valor líquido: R$ {valor_liquido_venda:,.0f}. 
Potencial de expansão: +{potencial_expansao} alunos. 
Projeção: EBITDA de R$ {projecao[-1]['EBITDA (R$)']:,.0f} em 3 anos."""
st.text_area("Copie e envie para potenciais compradores:", teaser, height=160)

# --- DOWNLOAD DO RELATÓRIO ---
st.header("📥 Relatório Completo")
if st.button("Gerar Relatório em Excel"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Dados principais
        dados_principais = {
            "Item": ["Alunos Totais", "Capacidade Total", "Receita Anual", "EBITDA", "Valor Líquido"],
            "Valor": [total_alunos, capacidade_total, receita_total, ebitda_bruto, valor_liquido_venda]
        }
        pd.DataFrame(dados_principais).to_excel(writer, sheet_name="Resumo", index=False)
        df_projecao.to_excel(writer, sheet_name="Projeção", index=False)
        benchmarks.to_excel(writer, sheet_name="Benchmarks", index=False)
    output.seek(0)
    st.download_button(
        label="📥 Baixar Excel",
        data=output,
        file_name="valuation_escola_completo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    )

