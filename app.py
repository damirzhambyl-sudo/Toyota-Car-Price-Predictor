import streamlit as st
import pandas as pd
import numpy as np
import joblib

st.set_page_config(page_title="Toyota Price Expert", layout="wide")

@st.cache_data
def load_full_data():
    return pd.read_csv("toyota_cleaned_final.csv")

@st.cache_resource
def load_model():
    return joblib.load('toyota_model_final.joblib')

df = load_full_data()
model = load_model()

st.title("Калькулятор стоимости Toyota")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Основные параметры")
    all_models = sorted(df['Модель'].unique().tolist())
    selected_model = st.selectbox("Модель", all_models)
    model_data = df[df['Модель'] == selected_model]
    
    available_years = sorted(model_data['Год'].unique().tolist(), reverse=True)
    year = st.selectbox("Год выпуска", available_years)
    year_data = model_data[model_data['Год'] == year]
    
    available_engines = sorted(year_data['Объем_двигателя'].unique().tolist())
    engine = st.selectbox("Объем двигателя", available_engines)
    mileage = st.number_input("Пробег (км)", 0, 1000000, 100000)

with col2:
    st.subheader("Характеристики")
    available_transmissions = sorted(year_data['Коробка'].unique().tolist())
    selected_transmission = st.selectbox("Коробка передач", available_transmissions)
    
    available_drives = sorted(year_data['Привод'].unique().tolist())
    selected_drive = st.selectbox("Привод", available_drives)
    
    available_fuels = sorted(year_data['Тип_топлива'].unique().tolist())
    selected_fuel = st.selectbox("Тип топлива", available_fuels)
    
    available_bodies = sorted(year_data['Кузов'].unique().tolist())
    selected_body = st.selectbox("Тип кузова", available_bodies)

with col3:
    st.subheader("Дополнительно")
    all_cities = sorted(df['Город'].unique().tolist())
    selected_city = st.selectbox("Город", all_cities)
    all_colors = sorted(df['Цвет'].unique().tolist())
    selected_color = st.selectbox("Цвет", all_colors)
    
    steering = st.radio("Руль", ["Левый", "Правый"])
    customs = st.radio("Растаможен в РК", ["Да", "Нет"])

if st.button("Рассчитать стоимость", use_container_width=True):
    input_df = pd.DataFrame({
        'Модель': [selected_model],
        'Город': [selected_city],
        'Год': [year], # Год вернули
        'Пробег': [mileage],
        'Кузов': [selected_body],
        'Коробка': [selected_transmission],
        'Привод': [selected_drive],
        'Руль': ["Слева" if steering == "Левый" else "Справа"],
        'Растаможен': ["Да" if customs == "Да" else "Нет"],
        'Цвет': [selected_color],
        'Тип_топлива': [selected_fuel],
        'Объем_двигателя': [engine],
        'Возраст': [2026 - year]
    })

    price = np.expm1(model.predict(input_df))[0]

    # Применяем рыночные коэффициенты
    if customs == "Нет":
        price *= 0.65
    if steering == "Правый":
        price *= 0.85

    st.divider()
    st.success(f"### Рекомендуемая цена: {price:,.0f} KZT")
    
    if customs == "Нет": st.info("Учтена скидка 35% за отсутствие растаможки")
    if steering == "Правый": st.info("Учтена скидка 15% за правый руль")