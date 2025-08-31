# streamlit_app.py
import streamlit as st
import pandas as pd
import yaml

st.set_page_config(page_title="Banca Virtual – SEEDES (pontos)", layout="wide")
st.title("Banca Virtual – SEEDES (por pontos)")

# ===== YAML padrão embutido (fallback) =====
SEEDES_FALLBACK_YAML = """
id: seedes_oficial
name: SEEDES – Regras por critério
version: '0.1'
elimination_threshold: 0.70
criteria:
  - { id: alinhamento_equipe,        label: 'Alinhamento da Equipe',                     weight: 0.10, max_points: 10 }
  - { id: dedicacao_processo,        label: 'Dedicação ao Processo',                     weight: 0.10, max_points: 10 }
  - { id: participacao_fundador,     label: 'Participação do Fundador',                  weight: 0.10, max_points: 10 }
  - { id: pitch,                     label: 'Pitch',                                     weight: 0.05, max_points:  5 }
  - { id: potencial_mercado,         label: 'Potencial de Mercado',                      weight: 0.15, max_points: 15 }
  - { id: viabilidade_financeira,    label: 'Viabilidade Econômico-Financeira',         weight: 0.10, max_points: 10 }
  - { id: viabilidade_operacional,   label: 'Viabilidade Operacional',                   weight: 0.10, max_points: 10 }
  - { id: mvp_validacao_aprendizado, label: 'MVP (Validação e Aprendizado)',             weight: 0.10, max_points: 10 }
  - { id: sustentabilidade_ods,      label: 'Sustentabilidade / ODS',                    weight: 0.10, max_points: 10 }
  - { id: cadeias_estrategicas_es,   label: 'Alinhamento às Cadeias Estratégicas do ES', weight: 0.10, max_points: 10 }
"""

# ===== Motor mínimo (por pontos brutos) =====
def load_rules(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f), "Arquivo carregado"
    except Exception as e:
        return yaml.safe_load(SEEDES_FALLBACK_YAML), f"Usando YAML embutido (fallback) – {e}"

def compute_score(rules, inputs_raw: dict):
    total = 0.0
    details = []
    for c in rules["criteria"]:
        cid = c["id"]; label = c["label"]; w = float(c["weight"]); mx = float(c.get("max_points", 1.0))
        raw = float(inputs_raw.get(cid, 0.0)); raw = max(0.0, min(mx, raw))
        norm = (raw / mx) if mx > 0 else 0.0
        total += norm * w
        details.append({"id": cid, "critério": label, "peso": w, "pontos_max": mx,
                        "pontos_lançados": raw, "nota_normalizada": norm,
                        "parcela": w * norm})
    eliminated = total < float(rules.get("elimination_threshold", 0.7))
    return total, eliminated, details

def what_if(rules, base_inputs: dict, target: str, delta: float):
    new = dict(base_inputs)
    new[target] = float(new.get(target, 0.0)) + float(delta)
    return compute_score(rules, new)

# ===== UI =====
rules_path = st.text_input("Arquivo de regras (YAML)", "app/engine/rules/seedes.yml")
rules, msg = load_rules(rules_path)
st.caption(msg)

try:
    st.success(f"Regras carregadas: {rules['name']}")
except:
    st.error("YAML inválido. Conferir estrutura de 'criteria' etc.")
    st.stop()

st.subheader("Lançamento de notas (em pontos brutos)")
inputs = {}
cols = st.columns(2)
for i, c in enumerate(rules["criteria"]):
    with cols[i % 2]:
        mx = float(c.get("max_points", 1.0))
        inputs[c["id"]] = st.number_input(f"{c['label']} (0–{mx:g})",
                                          min_value=0.0, max_value=mx, value=0.0, step=0.5)

total, eliminated, details = compute_score(rules, inputs)
st.metric("Nota total normalizada (0–1)", f"{total:.3f}")
st.metric("Equivalente (0–100)", f"{total*100:.1f}")
st.warning("Situação: Eliminado (<70)") if eliminated else st.success("Situação: Apto (≥70)")

st.write("**Detalhamento**")
st.dataframe(pd.DataFrame(details), use_container_width=True)

st.write("**What-if** (ajuste em pontos)")
target = st.selectbox("Critério a simular", [d["id"] for d in details])
delta = st.number_input("Δ pontos", value=1.0, step=0.5)
new_total, _, _ = what_if(rules, inputs, target, delta)
st.metric("Nova nota (0–1)", f"{new_total:.3f}")
st.metric("Equivalente (0–100)", f"{new_total*100:.1f}")
