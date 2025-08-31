import streamlit as st
import pandas as pd
import yaml
from app.engine.scoring import load_rules, compute_score, what_if
from app.analyzers.pitch_pdf import extract_pdf_outline, simple_section_score
from app.engine.valuation import scorecard_valuation, ScorecardInputs, vc_method, dcf_simple

st.set_page_config(page_title="Banca Virtual – MVP", layout="wide")

st.title("Banca Virtual – MVP")
st.caption("Analista de Propostas, Elegibilidade, Pitch Analyzer e Valuation")

st.sidebar.header("Módulos")
mod = st.sidebar.radio("Escolha:", ["Elegibilidade & Critérios", "Banca Virtual", "Pitch Analyzer", "Valuation"])

if mod == "Elegibilidade & Critérios":
    st.subheader("Carregar regras de edital (YAML)")
    col1, col2 = st.columns(2)
    with col1:
        rules_opt = st.selectbox("Modelos de exemplo", ["centelha", "tecnova"])
    if rules_opt == "centelha":
        path = "app/engine/rules/centelha.yml"
    else:
        path = "app/engine/rules/tecnova.yml"
    rules = load_rules(path)
    st.json({"id": rules.id, "name": rules.name, "criteria": [{ "id": c.id, "label": c.label, "weight": c.weight } for c in rules.criteria]})
    st.info("Use esta base para validar seus critérios/itens de avaliação. Você pode carregar outras regras no futuro.")

elif mod == "Banca Virtual":
    st.subheader("Pontuação por Critérios")
    rules_opt = st.selectbox("Modelos de exemplo", ["centelha", "tecnova"], key="banca_rules")
    path = "app/engine/rules/centelha.yml" if rules_opt=="centelha" else "app/engine/rules/tecnova.yml"
    rules = load_rules(path)

    st.write("**Informe notas (0–1) por critério**")
    inputs = {}
    cols = st.columns(2)
    for i, c in enumerate(rules.criteria):
        with cols[i%2]:
            inputs[c.id] = st.slider(f"{c.label} ({c.id})", 0.0, 1.0, 0.5, 0.05)

    result = compute_score(rules, inputs)
    st.metric("Nota total (0–1)", f"{result.total:.3f}")
    if result.eliminated:
        st.error("Situação: Eliminado pela regra de corte do edital (threshold).")
    else:
        st.success("Situação: Apto (acima do threshold do edital).")

    st.write("**Detalhamento**")
    det_df = pd.DataFrame([{"critério": d.label, "peso": d.weight, "nota": d.score, "parcela": d.weight*d.score} for d in result.details])
    st.dataframe(det_df, use_container_width=True)

    st.write("**What-if** (simular ganhos)")
    target = st.selectbox("Critério a simular", [d.id for d in result.details])
    delta = st.slider("Ajuste (–0.2 a +0.2)", -0.2, 0.2, 0.1, 0.01)
    new = what_if(rules, inputs, {target: delta})
    st.metric("Nova nota total", f"{new.total:.3f}")
    if new.total > result.total:
        st.info(f"Ganho de {(new.total - result.total):.3f} pontos.")

elif mod == "Pitch Analyzer":
    st.subheader("Análise de Pitch (PDF)")
    up = st.file_uploader("Envie o PDF do pitch", type=["pdf"])
    if up:
        data = up.read()
        outline = extract_pdf_outline(data)
        st.json(outline)
        # Very rough text extraction for keyword hits
        import fitz
        doc = fitz.open(stream=data, filetype="pdf")
        full_text = ""
        for i in range(min(doc.page_count, 10)):
            full_text += doc.load_page(i).get_text("text") + "\n"
        struct_score = simple_section_score(full_text)
        st.metric("Cobertura de seções comuns (heurística)", f"{struct_score*100:.0f}%")
        st.caption("Seções buscadas: Problema, Solução/Produto, Mercado, Modelo, GTM, Concorrência, Tração, Equipe, Roadmap, Use of Funds")

    st.divider()
    st.subheader("Transcrição de Áudio (opcional)")
    aud = st.file_uploader("Envie o áudio do pitch (mp3/wav/m4a)", type=["mp3","wav","m4a"])
    if aud:
        tmp_path = f"/tmp/{aud.name}"
        with open(tmp_path, "wb") as f:
            f.write(aud.read())
        st.info("Transcrevendo... (modelo small; CPU pode ser lento)")
        try:
            from app.analyzers.audio import transcribe
            t = transcribe(tmp_path, device="cpu", compute_type="int8")
            st.success(f"Língua: {t['language']} | Duração: {t['duration']:.1f}s")
            st.text_area("Transcrição", t["text"], height=200)
        except Exception as e:
            st.error(f"Falha ao transcrever: {e}")

elif mod == "Valuation":
    st.subheader("Scorecard (early stage)")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: team = st.slider("Time", 0.0, 1.0, 0.6, 0.05)
    with c2: product = st.slider("Produto", 0.0, 1.0, 0.6, 0.05)
    with c3: market = st.slider("Mercado", 0.0, 1.0, 0.6, 0.05)
    with c4: traction = st.slider("Tração", 0.0, 1.0, 0.5, 0.05)
    with c5: moat = st.slider("Moat", 0.0, 1.0, 0.5, 0.05)
    base = st.number_input("Base (valuation máximo referência)", 1_000_000, 20_000_000, 5_000_000, 100_000)
    val_scorecard = scorecard_valuation(ScorecardInputs(team, product, market, traction, moat), base=base)
    st.metric("Valuation (Scorecard)", f"R$ {val_scorecard:,.0f}")

    st.divider()
    st.subheader("VC Method (reverse)")
    post_money_target = st.number_input("Saída alvo (post-money, R$)", 10_000_000, 1_000_000_000, 100_000_000, 1_000_000)
    ownership = st.slider("Participação alvo do investidor", 0.05, 0.5, 0.2, 0.01)
    discount = st.slider("Taxa de retorno anual", 0.2, 1.0, 0.5, 0.05)
    years = st.slider("Horizonte (anos)", 2, 10, 5, 1)
    val_vc = vc_method(post_money_target, ownership, discount, years)
    st.metric("Valuation (VC Method)", f"R$ {val_vc:,.0f}")

    st.divider()
    st.subheader("DCF simples")
    revenue_year1 = st.number_input("Receita ano 1 (R$)", 100_000, 10_000_000, 1_000_000, 10_000)
    growth = st.slider("Crescimento anual", 0.0, 1.0, 0.4, 0.05)
    margin = st.slider("Margem FCFF (aprox.)", 0.05, 0.6, 0.2, 0.01)
    d_years = st.slider("Anos projetados", 3, 10, 5, 1)
    d_discount = st.slider("Taxa de desconto", 0.1, 0.6, 0.3, 0.05)
    g_terminal = st.slider("Crescimento terminal", 0.0, 0.05, 0.02, 0.005)
    val_dcf = dcf_simple(revenue_year1, growth, margin, d_years, d_discount, g_terminal)
    st.metric("Valuation (DCF)", f"R$ {val_dcf:,.0f}")
