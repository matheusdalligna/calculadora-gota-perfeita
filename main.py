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

# --- FUNÇÃO PARA GERAR PDF ---
class PDF(FPDF):
    def header(self):
        if os.path.exists("logo.png"):
            self.image("logo.png", 10, 8, 30)
        self.set_font('helvetica', 'B', 16)
        self.cell(0, 10, 'Relatorio de Calibracao - Gota Perfeita', 0, 1, 'R')
        self.ln(10)

def gerar_pdf(taxa, vel, esp, vazao, pontas_selecionadas, unidade):
    pdf = PDF()
    pdf.add_page()
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "Parametros de Operacao", 1, 1, 'L', 1)
    pdf.set_font("helvetica", size=10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f"Taxa de Aplicacao: {taxa} L/ha", 0, 1)
    pdf.cell(0, 8, f"Velocidade Alvo: {vel} km/h", 0, 1)
    pdf.cell(0, 8, f"Espacamento: {esp} cm", 0, 1)
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(0, 8, f"Volume a coletar por ponta (Caneca): {vazao:.3f} L/min", 0, 1)
    pdf.ln(5)
    
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "Sugestoes de Pontas", 0, 1, 'L')
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
        info = (f"-> Pressao exata para o alvo: {p['pressao']:.2f} {unidade}\n"
                f"-> Janela de Velocidade permitida: {p['v_min']:.1f} a {p['v_max']:.1f} km/h")
        pdf.multi_cell(0, 8, info, 1)
        pdf.ln(4)
    return pdf.output()

# --- FUNÇÃO PARA MOSTRAR PRÉVIA DO PDF ---
def visualizar_pdf(pdf_bytes):
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    # O iframe permite ver o PDF dentro da página. Ajustamos a altura para 500px.
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- 2. LOGO E TITULO ---
nome_arquivo_logo = "logo.png"
if os.path.exists(nome_arquivo_logo):
    st.image(Image.open(nome_arquivo_logo), width=150)

col_tit, col_btn = st.columns([2, 1])
with col_tit:
    st.title("Calculadora de Aplicacao")

# --- 3. INPUTS ---
st.subheader("Parametros de Operacao")

c1, c2 = st.columns(2)
with c1:
    v_kmh = st.number_input("Velocidade (km/h)", min_value=0.1, value=8.0, step=0.5, format="%.1f")
    esp_cm = st.number_input("Espacamento (cm)", min_value=1.0, value=50.0, step=5.0, format="%.0f")
with c2:
    taxa_lha = st.number_input("Taxa de Aplicacao (L/ha)", min_value=1.0, value=100.0, step=5.0, format="%.0f")
    unidade_p = st.selectbox("Unidade de Pressao:", ["psi", "bar", "kPa"])

if unidade_p == "psi":
    passo_p, val_min_p, val_max_p, formato = 5.0, 30.0, 60.0, "%.0f"
elif unidade_p == "bar":
    passo_p, val_min_p, val_max_p, formato = 0.5, 2.0, 4.0, "%.1f"
else: # kPa
    passo_p, val_min_p, val_max_p, formato = 50.0, 200.0, 400.0, "%.0f"

st.subheader("Informacoes da Ponta")
p1, p2 = st.columns(2)
with p1:
    p_min_input = st.number_input(f"P. Minima ({unidade_p})", value=val_min_p, step=passo_p, format=formato)
with p2:
    p_max_input = st.number_input(f"P. Maxima ({unidade_p})", value=val_max_p, step=passo_p, format=formato)

# --- 4. LOGICA DE CALCULO ---
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
st.metric(label="Volume coletado em uma ponta", value=f"{vazao_alvo:.3f} L/min")

tabela_iso = {
    "ISO 01 (Laranja)": {"vazao": 0.38, "cor_bg": "#FF8C00", "rgb": (255, 140, 0), "txt_rgb": (255, 255, 255), "cor_txt": "white"},
    "ISO 015 (Verde)": {"vazao": 0.57, "cor_bg": "#32CD32", "rgb": (50, 205, 50), "txt_rgb": (255, 255, 255), "cor_txt": "white"},
    "ISO 02 (Amarelo)": {"vazao": 0.76, "cor_bg": "#FFFF00", "rgb": (255, 255, 0), "txt_rgb": (0, 0, 0), "cor_txt": "black"},
    "ISO 025 (Lilas)": {"vazao": 0.95, "cor_bg": "#DA70D6", "rgb": (218, 112, 214), "txt_rgb": (255, 255, 255), "cor_txt": "white"},
    "ISO 03 (Azul)": {"vazao": 1.14, "cor_bg": "#0000FF", "rgb": (0, 0, 255), "txt_rgb": (255, 255, 255), "cor_txt": "white"},
    "ISO 035 (Vinho)": {"vazao": 1.33, "cor_bg": "#800000", "rgb": (128, 0, 0), "txt_rgb": (255, 255, 255), "cor_txt": "white"},
    "ISO 04 (Vermelho)": {"vazao": 1.52, "cor_bg": "#FF0000", "rgb": (255, 0, 0), "txt_rgb": (255, 255, 255), "cor_txt": "white"},
    "ISO 05 (Marrom)": {"vazao": 1.89, "cor_bg": "#8B4513", "rgb": (139, 69, 19), "txt_rgb": (255, 255, 255), "cor_txt": "white"}
}

# --- 5. RESULTADOS E PREVIA ---
pontas_encontradas_lista = []
encontrou_ponta = False

st.subheader("Pontas Sugeridas:")

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
                    Pressao: <b>{p_exata_final:.2f} {unidade_p}</b>
                </p>
                <p style="color: {dados['cor_txt']}; font-size: 14px; margin: 0;">
                    Velocidade: {vel_min_possivel:.1f} a {vel_max_possivel:.1f} km/h
                </p>
            </div>
        """, unsafe_allow_html=True)
        encontrou_ponta = True

if encontrou_ponta:
    pdf_raw = gerar_pdf(taxa_lha, v_kmh, esp_cm, vazao_alvo, pontas_encontradas_lista, unidade_p)
    
    # Adicionamos o botão de download no local de costume
    with col_btn:
        st.write("") 
        st.download_button(
            label="📥 Relatorio",
            data=bytes(pdf_raw),
            file_name="relatorio_calibracao.pdf",
            mime="application/pdf"
        )
    
    # NOVA SEÇÃO: PRÉVIA DO RELATÓRIO
    st.divider()
    st.subheader("Previa do Relatorio:")
    visualizar_pdf(pdf_raw)
else:
    st.warning("Nenhuma ponta atende aos criterios.")
