import streamlit as st
import math
from PIL import Image
import os
from fpdf import FPDF

# 1. CONFIGURAÇÃO DA PÁGINA (Foco total no Mobile)
st.set_page_config(
    page_title="Gota Perfeita - Calculadora", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- FUNÇÃO PARA GERAR PDF ---
class PDF(FPDF):
    def header(self):
        if os.path.exists("logo.png"):
            self.image("logo.png", 10, 8, 30)
        self.set_font('helvetica', 'B', 16)
        self.cell(0, 10, 'Relatório de Calibração - Gota Perfeita', 0, 1, 'R')
        self.ln(10)

def gerar_pdf(taxa, vel, esp, vazao, pontas_selecionadas, unidade):
    pdf = PDF()
    pdf.add_page()
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "Parâmetros de Operação", 1, 1, 'L', 1)
    pdf.set_font("helvetica", size=10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f"Taxa de Aplicação: {taxa} L/ha", 0, 1)
    pdf.cell(0, 8, f"Velocidade Alvo: {vel} km/h", 0, 1)
    pdf.cell(0, 8, f"Espaçamento: {esp} cm", 0, 1)
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(0, 8, f"Volume a coletar por ponta (Caneca): {vazao:.3f} L/min", 0, 1)
    pdf.ln(5)
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "Sugestões de Pontas (Configurações de Campo)", 0, 1, 'L')
    pdf.ln(2)
    for p in pontas_selecionadas:
        rgb = p['rgb']
        txt_rgb = p['txt_rgb']
        pdf.set_fill_color(rgb[0], rgb[1], rgb[2])
        pdf.set_text_color(txt_rgb[0], txt_rgb[1], txt_rgb[2])
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, f" {p['nome']}", 1, 1, 'L', 1)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("helvetica", size=11)
        info = (f"-> Pressão exata para o alvo: {p['pressao']:.2f} {unidade}\n"
                f"-> Janela de Velocidade permitida: {p['v_min']:.1f} a {p['v_max']:.1f} km/h")
        pdf.multi_cell(0, 8, info, 1)
        pdf.ln(4)
    return pdf.output()

# --- 2. LOGO E CABEÇALHO ---
nome_arquivo_logo = "logo.png"
if os.path.exists(nome_arquivo_logo):
    st.image(Image.open(nome_arquivo_logo), width=120)

col_tit, col_btn = st.columns([2, 1])
with col_tit:
    st.title("Calculadora de Aplicação")

# --- 3. ENTRADA DE DADOS (SLIDERS PARA CELULAR) ---
st.markdown("### 🚜 Parâmetros de Operação")

# Velocidade com Slider (Fácil de arrastar com o polegar)
v_kmh = st.slider("Velocidade (km/h)", 1.0, 25.0, 8.0, 0.5)

# Colunas para Taxa e Espaçamento
c1, c2 = st.columns(2)
with c1:
    taxa_lha = st.slider("Taxa (L/ha)", 10, 500, 100, 5)
with c2:
    esp_cm = st.slider("Espaçamento (cm)", 20, 100, 50, 5)

st.markdown("### ⚙️ Configuração das Pontas")
u1, u2 = st.columns([1, 1])
with u1:
    unidade_p = st.selectbox("Unidade:", ["psi", "bar", "kPa"])

# Pressões com number_input formatado para abrir teclado numérico
p1, p2 = st.columns(2)
with p1:
    p_min_input = st.number_input(f"P. Mínima", value=30.0 if unidade_p == "psi" else 2.0, step=0.1, format="%.1f")
with p2:
    p_max_input = st.number_input(f"P. Máxima", value=60.0 if unidade_p == "psi" else 4.0, step=0.1, format="%.1f")

# --- 4. CÁLCULOS ---
def converter_para_psi(valor, unidade):
    if unidade == "bar": return valor * 14.5038
    if unidade == "kPa": return valor * 0.145038
    return valor

def converter_de_psi(valor_psi, unidade_destino):
    if unidade_destino == "bar": return valor_psi / 14.5038
    if unidade_destino == "kPa": return valor_psi / 0.145038
    return valor_psi

p_min_psi = converter_para_psi(p_min_input, unidade_p)
p_max_psi = converter_para_psi(p_max_input, unidade_p)
vazao_alvo = (taxa_lha * v_kmh * esp_cm) / 60000

st.divider()
st.metric(label="Volume alvo por ponta", value=f"{vazao_alvo:.3f} L/min")

tabela_iso = {
    "ISO 01 (Laranja)": {"vazao": 0.38, "cor_bg": "#FF8C00", "rgb": (255, 140, 0), "txt_rgb": (255, 255, 255), "cor_txt": "white"},
    "ISO 015 (Verde)": {"vazao": 0.57, "cor_bg": "#32CD32", "rgb": (50, 205, 50), "txt_rgb": (255, 255, 255), "cor_txt": "white"},
    "ISO 02 (Amarelo)": {"vazao": 0.76, "cor_bg": "#FFFF00", "rgb": (255, 255, 0), "txt_rgb": (0, 0, 0), "cor_txt": "black"},
    "ISO 025 (Lilás)": {"vazao": 0.95, "cor_bg": "#DA70D6", "rgb": (218, 112, 214), "txt_rgb": (255, 255, 255), "cor_txt": "white"},
    "ISO 03 (Azul)": {"vazao": 1.14, "cor_bg": "#0000FF", "rgb": (0, 0, 255), "txt_rgb": (255, 255, 255), "cor_txt": "white"},
    "ISO 035 (Vinho)": {"vazao": 1.33, "cor_bg": "#800000", "rgb": (128, 0, 0), "txt_rgb": (255, 255, 255), "cor_txt": "white"},
    "ISO 04 (Vermelho)": {"vazao": 1.52, "cor_bg": "#FF0000", "rgb": (255, 0, 0), "txt_rgb": (255, 255, 255), "cor_txt": "white"},
    "ISO 05 (Marrom)": {"vazao": 1.89, "cor_bg": "#8B4513", "rgb": (139, 69, 19), "txt_rgb": (255, 255, 255), "cor_txt": "white"}
}

# --- 5. RESULTADOS E PDF ---
pontas_encontradas_lista = []
encontrou_ponta = False

st.subheader("Pontas Recomendadas:")

for nome_ponta, dados in tabela_iso.items():
    q_nominal = dados["vazao"]
    v_min_ponta = q_nominal * math.sqrt(p_min_psi / 40)
    v_max_ponta = q_nominal * math.sqrt(p_max_psi / 40)
    
    if v_min_ponta <= vazao_alvo <= v_max_ponta:
        p_exata_psi = ((vazao_alvo / q_nominal) ** 2) * 40
        p_exata_final = converter_de_psi(p_exata_psi, unidade_p)
        vel_min_possivel = (v_min_ponta * 60000) / (taxa_lha * esp_cm)
        vel_max_possivel = (v_max_ponta * 60000) / (taxa_lha * esp_cm)
        
        pontas_encontradas_lista.append({
            "nome": nome_ponta, "pressao": p_exata_final, 
            "v_min": vel_min_possivel, "v_max": vel_max_possivel,
            "rgb": dados['rgb'], "txt_rgb": dados['txt_rgb']
        })

        st.markdown(f"""
            <div style="background-color: {dados['cor_bg']}; padding: 15px; border-radius: 10px; border: 1px solid #333; margin-bottom: 10px; text-align: center;">
                <h3 style="color: {dados['cor_txt']}; margin: 0;">{nome_ponta}</h3>
                <p style="color: {dados['cor_txt']}; font-size: 16px; margin: 5px 0;">
                    Pressão Alvo: <b>{p_exata_final:.2f} {unidade_p}</b>
                </p>
                <p style="color: {dados['cor_txt']}; font-size: 14px; margin: 0; opacity: 0.9;">
                    Janela: {vel_min_possivel:.1f} a {vel_max_possivel:.1f} km/h
                </p>
            </div>
        """, unsafe_allow_html=True)
        encontrou_ponta = True

if encontrou_ponta:
    pdf_raw = gerar_pdf(taxa_lha, v_kmh, esp_cm, vazao_alvo, pontas_encontradas_lista, unidade_p)
    with col_btn:
        st.write("") # Espaçador
        st.download_button(
            label="📥 PDF",
            data=bytes(pdf_raw),
            file_name="calibracao_gota.pdf",
            mime="application/pdf"
        )
else:
    st.warning("Ajuste os parâmetros para encontrar uma ponta.")
