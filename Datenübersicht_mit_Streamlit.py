import streamlit as st
import pandas as pd
import altair as alt

st.title("Datenübersicht mit Streamlit")
st.divider()

uploaded_files = st.file_uploader("Wähle eine oder mehrere Dateien", type=["txt", "csv", "xlsx", "jpg", "png"], accept_multiple_files=True)

def zeige_zusammenfassung(df):
    with st.expander("Zusammenfassung der Tabelle"):
        st.write(f"- Anzahl Zeilen: {df.shape[0]}")
        st.write(f"- Anzahl Spalten: {df.shape[1]}")
        st.write(f"- Spaltennamen: {list(df.columns)}")

        st.write("Fehlende Werte pro Spalte:")
        st.write(df.isnull().sum())

        st.write("Basisstatistiken (numerische Spalten):")
        st.write(df.describe())

        cat_cols = df.select_dtypes(include=['object']).columns
        for col in cat_cols:
            unique_vals = df[col].dropna().unique()[:5]
            st.write(f"Spalte '{col}' - einige einzigartige Werte: {unique_vals}")

def plot_spalte(df):
    numerische_spalten = df.select_dtypes(include=['number']).columns.tolist()
    if numerische_spalten:
        st.write("### Diagramm erstellen")

        spalte = st.selectbox("Numerische Spalte zum Plotten", numerische_spalten)

        # Filteroption nur fürs Diagramm
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        filter_df = df  # Standard: komplette Daten

        if cat_cols:
            filter_spalte = st.selectbox("Diagramm filtern nach Kategorie (optional)", options=[None] + cat_cols)
            if filter_spalte:
                filter_wert = st.selectbox(f"Wert in '{filter_spalte}' auswählen", options=df[filter_spalte].dropna().unique())
                filter_df = df[df[filter_spalte] == filter_wert]

        chart = alt.Chart(filter_df).mark_bar().encode(
            x=alt.X(spalte, bin=True, title=spalte),
            y=alt.Y('count()', title='Anzahl'),
            tooltip=[spalte, 'count()']
        ).properties(
            width=600,
            height=300,
            title=f"Verteilung der Werte in '{spalte}'"
        ).interactive()

        st.altair_chart(chart, use_container_width=False)
    else:
        st.write("Keine numerischen Spalten zum Plotten gefunden.")

if uploaded_files:
    # Sidebar: Datei auswählen
    file_names = [f.name for f in uploaded_files]
    selected_file_name = st.sidebar.selectbox("Wähle eine Datei aus", file_names)

    # Finde die Datei im Upload basierend auf dem Namen
    selected_file = next((f for f in uploaded_files if f.name == selected_file_name), None)

    st.write("Dateiname:", selected_file.name)

    try:
        if selected_file.name.endswith(".txt"):
            content_bytes = selected_file.read()
            try:
                content = content_bytes.decode("utf-8")
            except UnicodeDecodeError:
                content = content_bytes.decode("latin-1")
            st.text_area("Inhalt der Datei", content, height=300)

        elif selected_file.name.endswith(".csv"):
            selected_file.seek(0)  # Falls vorher schon gelesen
            df = pd.read_csv(selected_file)
            st.dataframe(df)
            zeige_zusammenfassung(df)
            plot_spalte(df)

        elif selected_file.name.endswith(".xlsx"):
            selected_file.seek(0)
            xls = pd.ExcelFile(selected_file)
            sheets = xls.sheet_names

            if len(sheets) == 1:
                sheet = sheets[0]
                st.info(f"Es gibt nur ein Blatt: **{sheet}**")
            else:
                sheet = st.selectbox("Blatt auswählen", sheets)

            df = pd.read_excel(xls, sheet_name=sheet)
            st.dataframe(df)
            zeige_zusammenfassung(df)
            plot_spalte(df)

        elif selected_file.name.endswith((".jpg", ".png")):
            st.image(selected_file, caption="Hochgeladenes Bild", use_column_width=True)

        else:
            st.warning("Dateityp wird nicht unterstützt.")

    except Exception as e:
        st.error(f"Fehler beim Verarbeiten der Datei: {e}")

else:
    st.info("Bitte lade mindestens eine Datei hoch.")