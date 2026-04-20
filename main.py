import streamlit as st
import math
from PIL import Image
import os
from fpdf import FPDF
import base64

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Gota Perfeita - Calculadora", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- FUNÇÃO PARA GERAR PDF COM ACENTUAÇÃO E FUNDO BRANCO ---
class PDF(FPDF):
    def header(self):
        self.set_fill_color(255, 255, 255)
        self.rect(0, 0, 210, 297, 'F') 
        if os.path.exists("logo.png"):
            self.image("logo.png", 10, 8, 30)
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(0, 0, 0)
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
    pdf.cell(0, 10, "Sugestões Técnicas de Pontas", 0, 1, 'L')
    pdf.ln(2)

    # Contador para indicar 1ª opção, 2ª opção...
    for i, p in enumerate(pontas_selecionadas):
        rgb = p['rgb']
        txt_rgb = p['txt_rgb']
        pdf.set_fill_color(rgb[0], rgb[1], rgb[2])
        pdf.set_text_color(txt_rgb[0], txt_rgb[1], txt_rgb[2])
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, f" {i+1}ª Opção: {p['nome']}", 1, 1, 'L', 1)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("helvetica", size=11)
        info = (f"-> Pressão exata para o alvo: {p['pressao']:.2f} {unidade}\n"
                f"-> Janela de Velocidade permitida: {p['v_min']:.1f} a {p['v_max']:.1f} km/h")
        pdf.multi_cell(0, 8, info, 1)
        pdf.ln(4)
    return pdf.output()

def exibir_pdf_iframe(pdf_bytes):
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf" style="background-color: white;"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- 2. LOGO E TITULO ---
if os.path.exists("logo.png"):
    st.image(Image.open("logo.png"), width=150)
st.title("Calculadora de Aplicação")

# --- 3. INPUTS ---
st.subheader("Parâmetros de Operação")
c1, c2 = st.columns(2)
with c1:
    v_kmh = st.number_input("Velocidade (km/h)", min_value=0.1, value=8.0, step=0.5, format="%.1f")
    esp_cm = st.number_input("Espaçamento (cm)", min_value=1.0, value=50.0, step=5.0, format="%.0f")
with c2:
    taxa_lha = st.number_input("Taxa de Aplicação (L/ha)", min_value=1.0, value=100.0, step=5.0, format="%.0f")
    unidade_p = st.selectbox("Unidade de Pressão:", ["psi", "bar", "kPa"])

if unidade_p == "psi":
    passo_p, val_min_p, val_max_p, formato = 5.0, 30.0, 60.0, "%.0f"
elif unidade_p == "bar":
    passo_p, val_min_p, val_max_p, formato = 0.5, 2.0, 4.0, "%.1f"
else: # kPa
    passo_p, val_min_p, val_max_p, formato = 50.0, 200.0, 400.0, "%.0f"

st.subheader("Informações da Ponta")
p1, p2 = st.columns(2)
with p1:
    p_min_input = st.number_input(f"P. Mínima ({unidade_p})", value=val_min_p, step=passo_p, format=formato)
with p2:
    p_max_input = st.number_input(f"P. Máxima ({unidade_p})", value=val_max_p, step=passo_p, format=formato)

# --- 4. LÓGICA DE CÁLCULO ---
vazao_alvo = (taxa_lha * v_kmh * esp_cm) / 60000
st.divider()
st.metric(label="Volume coletado em uma ponta", value=f"{vazao_alvo:.3f} L/min")

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

# --- 5. FILTRAGEM DE PONTAS ---
pontas_possiveis = []
for nome_ponta, dados in tabela_iso.items():
    p_min_psi = p_min_input * 14.5038 if unidade_p == "bar" else (p_min_input * 0.145038 if unidade_p == "kPa" else p_min_input)
    p_max_psi = p_max_input * 14.5038 if unidade_p == "bar" else (p_max_input * 0.145038 if unidade_p == "kPa" else p_max_input)
    v_min_p = dados["vazao"] * math.sqrt(p_min_psi / 40)
    v_max_p = dados["vazao"] * math.sqrt(p_max_psi / 40)
    
    if v_min_p <= vazao_alvo <= v_max_p:
        p_ex_psi = ((vazao_alvo / dados["vazao"]) ** 2) * 40
        p_ex_f = p_ex_psi / 14.5038 if unidade_p == "bar" else (p_ex_psi / 0.145038 if unidade_p == "kPa" else p_ex_psi)
        pontas_possiveis.append({
            "nome": nome_ponta, "pressao": p_ex_f, 
            "v_min": (v_min_p * 60000) / (taxa_lha * esp_cm), 
            "v_max": (v_max_p * 60000) / (taxa_lha * esp_cm),
            "rgb": dados['rgb'], "txt_rgb": dados['txt_rgb'], "cor_bg": dados['cor_bg'], "cor_txt": dados['cor_txt']
        })

if pontas_possiveis:
    st.subheader("Seleção Técnica")
    lista_nomes = [p['nome'] for p in pontas_possiveis]
    escolhidas_nomes = st.multiselect(
        "Selecione e ordene as pontas para o relatório (a primeira será a 1ª Opção):",
        options=lista_nomes,
        default=lista_nomes
    )
    
    pontas_para_exibir = [p for name in escolhidas_nomes for p in pontas_possiveis if p['nome'] == name]

    if pontas_para_exibir:
        for i, p in enumerate(pontas_para_exibir):
            st.markdown(f"""
                <div style="background-color: {p['cor_bg']}; padding: 15px; border-radius: 10px; border: 1px solid #333; margin-bottom: 10px; text-align: center;">
                    <h3 style="color: {p['cor_txt']}; margin: 0;">{i+1}ª Opção: {p['nome']}</h3>
                    <p style="color: {p['cor_txt']}; font-size: 16px; margin: 5px 0;">Pressão: <b>{p['pressao']:.2f} {unidade_p}</b></p>
                    <p style="color: {p['cor_txt']}; font-size: 14px; margin: 0;">Velocidade: {p['v_min']:.1f} a {p['v_max']:.1f} km/h</p>
                </div>
            """, unsafe_allow_html=True)

        pdf_raw = gerar_pdf(taxa_lha, v_kmh, esp_cm, vazao_alvo, pontas_para_exibir, unidade_p)
        st.divider()
        st.download_button(label="📥 Baixar Relatório PDF", data=bytes(pdf_raw), file_name="relatorio_calibracao.pdf", mime="application/pdf", use_container_width=True)
        with st.expander("👁️ Visualizar Prévia (para Print/Compartilhar)"):
            st.info("💡 **Dica:** Para compartilhar rapidamente, tire um print ou segure pressionado.")
            exibir_pdf_iframe(pdf_raw)
    else:
        st.info("Selecione pelo menos uma ponta acima para gerar o relatório.")
else:
    st.warning("Nenhuma ponta atende aos critérios.")
