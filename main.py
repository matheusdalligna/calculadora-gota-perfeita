import streamlit as st
import math
from PIL import Image
import os
from fpdf import FPDF

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Gota Perfeita - Calculadora", layout="wide")

# --- FUNÇÃO PARA GERAR PDF COM CORES E ACENTOS ---
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

# --- 2. BARRA LATERAL ---
nome_arquivo_logo = "logo.png"
if os.path.exists(nome_arquivo_logo):
    st.sidebar.image(Image.open(nome_arquivo_logo), use_container_width=True)
else:
    st.sidebar.title("Gota Perfeita")

st.sidebar.divider()
st.sidebar.header("Parâmetros de Operação")
v_kmh = st.sidebar.number_input("Velocidade (km/h)", min_value=0.1, value=8.0, step=0.1)
taxa_lha = st.sidebar.number_input("Taxa de Aplicação (L/ha)", min_value=1.0, value=100.0, step=1.0)
esp_cm = st.sidebar.number_input("Espaçamento (cm)", min_value=1.0, value=50.0, step=1.0)

st.sidebar.divider()
st.sidebar.header("Informações da Ponta")
unidade_p = st.sidebar.selectbox("Unidade de Pressão:", ["psi", "bar", "kPa"])
p_min_input = st.sidebar.number_input(f"Pressão Mínima ({unidade_p})", value=30.0 if unidade_p == "psi" else 2.0)
p_max_input = st.sidebar.number_input(f"Pressão Máxima ({unidade_p})", value=60.0 if unidade_p == "psi" else 4.0)

# --- 3. LÓGICA ---
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

# --- 4. LAYOUT PRINCIPAL ---
col_tit, col_btn = st.columns([3, 1])
with col_tit:
    st.title("Calculadora de ponta de aplicação")

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

st.divider()
st.subheader(f"Pontas Sugeridas:")

pontas_encontradas_lista = []
encontrou_ponta = False

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
            <div style="background-color: {dados['cor_bg']}; padding: 20px; border-radius: 10px; border: 2px solid #333; margin-bottom: 15px; text-align: center;">
                <h2 style="color: {dados['cor_txt']}; margin: 0;">{nome_ponta}</h2>
                <p style="color: {dados['cor_txt']}; font-size: 18px; margin: 10px 0;">
                    Para {taxa_lha} L/ha a {v_kmh} km/h: <strong>{p_exata_final:.2f} {unidade_p}</strong>
                </p>
                <div style="border-top: 1px solid {dados['cor_txt']}; opacity: 0.3; margin: 10px 0;"></div>
                <p style="color: {dados['cor_txt']}; font-size: 15px; margin: 0;">
                    <b>Janela de Velocidade Operacional:</b><br>
                    Mín: {vel_min_possivel:.1f} km/h | Máx: {vel_max_possivel:.1f} km/h
                </p>
            </div>
        """, unsafe_allow_html=True)
        encontrou_ponta = True

# --- 5. GERAÇÃO DO RELATÓRIO CORRIGIDA ---
if encontrou_ponta:
    pdf_raw = gerar_pdf(taxa_lha, v_kmh, esp_cm, vazao_alvo, pontas_encontradas_lista, unidade_p)
    pdf_final = bytes(pdf_raw) # Conversão para corrigir o erro de bytearray
    
    with col_btn:
        st.write(" ") 
        st.download_button(
            label="📥 Gerar Relatório",
            data=pdf_final,
            file_name="relatorio_calibracao.pdf",
            mime="application/pdf"
        )
else:
    st.error("Nenhuma ponta atende aos critérios.")