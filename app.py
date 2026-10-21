import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from google import genai
import os

# 1. Configuration de la page Streamlit
st.set_page_config(page_title="Cabinet 360 - Assistant Data IA", layout="wide", page_icon="📊")

st.title("🤖 Cabinet 360 — Assistant Data & Text-to-Analytics")
st.markdown("Posez vos questions en langage naturel sur le CA HT, le DSO et le suivi des créances.")

# 2. Gestion de la clé API Gemini
# On demande la clé API sur la barre latérale ou via les variables d'environnement
api_key = st.sidebar.text_input("Clé API Google Gemini :", type="password")

if not api_key:
    st.info("👈 Veuillez saisir votre clé API Gemini dans la barre latérale pour démarrer.")
    st.stop()

client = genai.Client(api_key=api_key)


# 3. Chargement des données Cabinet 360
@st.cache_data
def load_data():
    # Remplacez par le nom exact de votre fichier (ex: 'data_cabinet360.csv' ou .xlsx)
    if os.path.exists("cabinet_360.csv"):
        return pd.read_csv("cabinet_360.csv")
    else:
        return None


df = load_data()

if df is None:
    st.error(
        "❌ Fichier de données introuvable. Veuillez ajouter 'cabinet_360.csv' ou '.xlsx' dans le dossier du projet.")
    st.stop()

# Aperçu des données dans un panneau dépliant
with st.expander("👀 Aperçu du jeu de données (Cabinet 360)"):
    st.dataframe(df.head())

# 4. Zone de dialogue utilisateur
query = st.text_input(
    "💬 Posez votre question sur les données (ex: 'Donne-moi le top 5 des clients par retard moyen') :")

if query:
    # Construction du prompt pour instruire Gemini
    prompt = f"""
Tu es un expert Data Analyst. Tu travailles avec un DataFrame pandas nommé `df`.
Voici les colonnes du DataFrame et leurs types :
{df.dtypes.to_string()}

Aperçu des 3 premières lignes :
{df.head(3).to_string()}

Question de l'utilisateur : "{query}"

Règle stricte : Génère uniquement un bloc de code Python valide (sans explication, sans balises de code Markdown au début ou à la fin).
Le code doit effectuer l'analyse demandée à partir du DataFrame `df`.
- Si la question demande un chiffre, un tableau ou un résumé textuel, stocke le résultat dans une variable nommée `result`.
- Si la question demande un graphique, crée le graphique avec matplotlib/seaborn et termine par `st.pyplot(plt.gcf())`.

Donne uniquement le code Python à exécuter.
"""

    with st.spinner("Analyse de la question en cours par Gemini..."):
        try:
            # Appel de l'API Gemini 2.5 Flash
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
            )

            # Nettoyage du code généré
            generated_code = response.text.replace("```python", "").replace("```", "").strip()

            with st.expander("🔍 Voir le code Python généré par l'IA"):
                st.code(generated_code, language="python")

            # Exécution du code généré sur le DataFrame
            local_vars = {"df": df, "pd": pd, "plt": plt, "st": st}
            exec(generated_code, globals(), local_vars)

            # Affichage du résultat si une variable 'result' a été créée
            if "result" in local_vars:
                st.success("Résultat de l'analyse :")
                res = local_vars["result"]
                if isinstance(res, (pd.DataFrame, pd.Series)):
                    st.dataframe(res)
                else:
                    st.write(res)

        except Exception as e:
            st.error(f"Une erreur s'est produite lors de l'exécution : {e}")