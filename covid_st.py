import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st

#----------------------------------------------- PREVIA -----------------------------------------------------------
st.markdown("<h1 style='text-align: center;'>&#128567 Análisis del COVID-19 en Estados Unidos</h1>", unsafe_allow_html=True)
# Preproceso el dataframe
df = pd.read_csv('./COVID-19_Reported_Patient_Impact_and_Hospital_Capacity_by_State_Timeseries.csv')
df = df.sort_values('date').reset_index(drop=True)
df = df[df['date'] < '2022/08/01']
# Lleno los valores NaN con 0 para evitar problemas de calculo
for i in df:
  df[i] = df[i].fillna(0)


#---------------------------------------------- 1 ------------------------------------------------------------
st.markdown("<h2>&#128719 Análisis de ocupación hospitalaria</h2>", unsafe_allow_html=True)
# Preparo el dafaframe para este análisis
df_camas = df[['state', 
                'date', 
                'total_adult_patients_hospitalized_confirmed_covid', 
                'total_pediatric_patients_hospitalized_confirmed_covid', 
                'inpatient_beds_used_covid'
                ]]
df_camas['total_camas'] = df_camas['total_pediatric_patients_hospitalized_confirmed_covid'] + df_camas['total_adult_patients_hospitalized_confirmed_covid']
# Creo un dataframe para el primer semestre
df_primer_semestre = df_camas[df_camas['date']<'2020/07/01']
# Agrupo por estado y llamo al top 5 (total de camas calculado)
top_primer_semestre = df_primer_semestre[['state', 'total_camas']].groupby('state').sum(min_count=1).sort_values(by='total_camas', ascending=False).head()
with st.expander('Top 5 estados con mayor ocupación en el primer semestre de 2020'):
  st.dataframe(top_primer_semestre)
#Creo un dataframe para el top 5 ocupacion de adultos
top_primer_semestre_adultos = df_primer_semestre[['state', 'total_adult_patients_hospitalized_confirmed_covid']].groupby('state').sum(min_count=1).sort_values(by='total_adult_patients_hospitalized_confirmed_covid', ascending=False).head()
with st.expander('Top 5 estados con mayor ocupación en el primer semestre de 2020 (solo adultos)'):
  st.dataframe(top_primer_semestre_adultos)
# Creo un dataframe para el top 5 ocupacion pediatricos
top_primer_semestre_pediatrico = df_primer_semestre[['state', 'total_pediatric_patients_hospitalized_confirmed_covid']].groupby('state').sum(min_count=1).sort_values(by='total_pediatric_patients_hospitalized_confirmed_covid', ascending=False).head()
with st.expander('Top 5 estados con mayor ocupación en el primer semestre de 2020 (solo pediatricos)'):
  st.dataframe(top_primer_semestre_pediatrico)



#---------------------------------------------- 2 -----------------------------------------------------------
st.markdown("<h2>&#128509 Análisis de camas en Nueva York en cuarentena</h2>", unsafe_allow_html=True)
# Preparo el dafaframe para este análisis
df_ny = df_camas.loc[df['state'] == 'NY']
df_ny_q = df_ny.loc[(df_ny['date'] > '2020/03/22') & (df_ny['date'] < '2021/06/13')]
# Preparo el grafico
from datetime import datetime
df_ny_q['date'] = [datetime.strptime(date, '%Y/%m/%d').date() for date in df_ny_q['date']]
df_ny_q.rename(columns={'date':'fechas', 'total_camas':'total de camas ocupadas'}, inplace=True)
fig1 =  px.line(df_ny_q, x='fechas', y=['total de camas ocupadas', 'inpatient_beds_used_covid'], title='Evolución de la ocupación de las cámas')
with st.expander('Mostrar gráfico'):
  st.plotly_chart(fig1)



#--------------------------------------------- 3 -------------------------------------------------------------
st.markdown("<h2>&#128657 Ocupación de unidades de cuidados intensivos durante 2020</h2>", unsafe_allow_html=True)
# Creo un dataframe particular para la ocupacion de UCI del año 2020
df_icu = df[['state', 'date', 'total_staffed_adult_icu_beds', 'staffed_icu_adult_patients_confirmed_covid', 'total_staffed_pediatric_icu_beds', 'staffed_icu_pediatric_patients_confirmed_covid', ]]
df_icu['total_icu'] = df_icu['total_staffed_adult_icu_beds'] + df_icu['total_staffed_pediatric_icu_beds']
df_icu_2020 = df_icu[df_icu['date']< '2021/01/01']
with st.expander('Top 5 estados con mayor ingresos a unidades de cuidado intensivo'):
  st.dataframe(df_icu_2020.groupby('state')['total_icu'].sum().sort_values( ascending=False).head())



#--------------------------------------------- 4 -------------------------------------------------------------
st.markdown("<h2>&#128118 Ocupación de camas de pacientes pediátricos</h2>", unsafe_allow_html=True)
# Creo un dataframe sobre las camas de pacientes pediatricos para el año 2020
df_pediatrico = df[['state', 'date', 'total_pediatric_patients_hospitalized_confirmed_covid']]
df_pediatrico = df_pediatrico[df_pediatrico['date']< '2021/01/01']
pediatrico_2020 = df_pediatrico.groupby('state')['total_pediatric_patients_hospitalized_confirmed_covid'].sum()
fig2 = px.bar(pediatrico_2020)
with st.expander('Mostrar gráfico'):
  st.plotly_chart(fig2)



#---------------------------------------------- 5 ------------------------------------------------------------
st.markdown("<h2>&#128202 Porcentaje de ocupación de unidades de cuidado intensivo para pacientes con COVID-19 confirmado</h2>", unsafe_allow_html=True)
# Preparo las variables para calcular el porcentaje
df_icu['total_icu_covid'] = df_icu['staffed_icu_adult_patients_confirmed_covid'] + df_icu['staffed_icu_pediatric_patients_confirmed_covid']
total_icu_estados = df_icu.groupby('state')['total_icu'].sum().sort_values( ascending=False)
icu_covid_estados = df_icu.groupby('state')['total_icu_covid'].sum().sort_values( ascending=False)
icu_total_vs_covid = df_icu.groupby('state').apply(lambda x: (total_icu_estados/icu_covid_estados)*100)
l = []
for i in total_icu_estados.index:
  l.append(round(float(icu_covid_estados[total_icu_estados.index==i].values/total_icu_estados[total_icu_estados.index==i].values*100), 2))
print(l)
fig3 = px.bar(x = icu_total_vs_covid.index, y = l)
fig3.update_layout(title="Porcentaje de ocupación UCI de pacientes con COVID-19", xaxis_title="Estados", yaxis_title="Porcentaje de ocupación")
with st.expander('Mostrar gráfico'):
  st.plotly_chart(fig3)



#---------------------------------------------- 6 ------------------------------------------------------------
st.markdown("<h2>&#128506 Mapa de muertes por COVID-19 por estado</h2>", unsafe_allow_html=True)
# Preparo el dataframe que representa las muertes
df_deaths = df[['state','date', 'deaths_covid']]
df_deaths_total = df_deaths.groupby(by='state', as_index=False).sum().sort_values(by='deaths_covid', ascending=False)
df_deaths_2021 = df_deaths[(df_deaths['date'] > '2020/12/31') & (df_deaths['date'] < '2022/01/01')]
#Mapa para el 2021
fig = px.choropleth(df_deaths_2021, 
                    locations=df_deaths_2021['state'], 
                    locationmode='USA-states', 
                    scope='usa', 
                    color=df_deaths_2021['deaths_covid'], 
                    color_continuous_scale='ylorrd', 
                    range_color=(0, 600),
                    labels={'locations':'Estado', 
                            'color':'Muertes'}
                    )
fig.update_layout(geo_scope='usa')
with st.expander('Muertes hasta el 2021'):
  st.plotly_chart(fig)
# Mapa con total de muertes
figb = px.choropleth(df_deaths_total, 
                    locations=df_deaths_total['state'], 
                    locationmode='USA-states', 
                    scope='usa', 
                    color=df_deaths_total['deaths_covid'], 
                    color_continuous_scale='ylorrd',
                    labels={'locations':'Estado', 
                            'color':'Muertes'}
                    )
figb.update_layout(geo_scope='usa')
with st.expander('Total de muertes'):
  st.plotly_chart(figb)



#---------------------------------------------- 7 ------------------------------------------------------------
st.markdown("<h2>&#128200 &#128201 Relación muertes-falta de personal (2021)</h2>", unsafe_allow_html=True)
# Creo el dataframe para calcular la correlación
df_muertes_staff = df[['state', 'date', 'critical_staffing_shortage_today_yes', 'deaths_covid']]
df_muertes_staff_2021 = df_muertes_staff.loc[(df_muertes_staff['date'] > '2020/12/31') & (df_muertes_staff['date'] > '2022/01/01')]
# Uso la función de numpy para calcular la correlación entre las muertes y la falta de personal
corr_muerte_staff = np.corrcoef(df_muertes_staff_2021['deaths_covid'], df_muertes_staff_2021['critical_staffing_shortage_today_yes'])[0,1]
st.markdown(f'''<p>El coeficiente de correlación entre las muertes por coronavirus y la falta de personal es de {round(corr_muerte_staff, 2)}.</p>''', unsafe_allow_html=True)
#st.markdown('<p>Se calculo de la siguiente manera:</p>', unsafe_allow_html=True)
#st.code('''np.corrcoef(df_muertes_staff_2021['deaths_covid'], df_muertes_staff_2021['critical_staffing_shortage_today_yes'])[0,1]''', language='python')

# Preparo las fechas del dataframe
from datetime import datetime
df_muertes_staff_2021['date'] = [datetime.strptime(date, '%Y/%m/%d').date() for date in df_muertes_staff_2021['date']]
# Preparo el gráfico para ver la relación visualmente
fig4 =  px.line(df_muertes_staff_2021, x='date', y=['deaths_covid','critical_staffing_shortage_today_yes'])

#Como el codigo anterior no me mostraba bien el gráfico usé otro método:
# Grafico el paralelismo entre las muertes por covid y la falta de personal
sns.lineplot(data=df_muertes_staff, x= df_muertes_staff_2021['date'], y=df_muertes_staff_2021['deaths_covid'], palette='r')
sns.lineplot(data=df_muertes_staff, x= df_muertes_staff_2021['date'], y=df_muertes_staff_2021['critical_staffing_shortage_today_yes'], palette='b').set(xlabel='Fecha', ylabel='cantidad');
#Este codigo se corrió en el notebook y guarde la imagen para exponerla.

with st.expander('Gráfico relación muertes-falta de personal:'):
  st.markdown('<p>Con naranja representando las muertes y azul la falta de personal</p>', unsafe_allow_html=True)
  st.image('./images/grafico_muertes_staff.png')



#---------------------------------------------- 8 ------------------------------------------------------------
st.markdown("<h2>&#128680 Peor mes para Estados Unidos por el COVID-19</h2>", unsafe_allow_html=True)
# Creo un dataframe para separar mensualmente los datos
df_mensual = df_deaths
df_mensual['date'] = pd.to_datetime(df_mensual['date'], format='%Y-%m-%d')


# Tomo en cuenta las muertes para elegir el peor mes
st.markdown("<h3>&#9760 Por muertes</h3>", unsafe_allow_html=True)
# Agrupo por año y mes y llamo al mes con mayor cantidad de muertes en todo Estados Unidos
df_mensual_grupo_muertes = df_mensual.groupby([df_mensual['date'].dt.year, df_mensual['date'].dt.month])['deaths_covid'].sum()
peor_mes_muertes = df_mensual_grupo_muertes.loc[df_mensual_grupo_muertes.values == df_mensual_grupo_muertes.max()]
# NOTA: Por errores en como muestra el dataframe voy a cargarlos como imágen sacada del notebook
with st.expander('Mostrar (año/mes/total muertes)'):
  st.image('./images/peor_mes_muertes.png')


#Tomo en cuenta la ocupación de UCI
st.markdown("<h3>&#128737 Por ocupacción de unidades de cuidado intensivo</h3>", unsafe_allow_html=True)
# Agrego la columna de icu por covid
df_mensual['total_icu_covid'] = df_icu['total_icu_covid']
# Agrupo por año y mes y llamo al mes con mayor ocupacion de icu en todo Estados Unidos
df_mensual_grupo_icu = df_mensual.groupby([df_mensual['date'].dt.year, df_mensual['date'].dt.month])['total_icu_covid'].sum()
peor_mes_icu = df_mensual_grupo_icu.loc[df_mensual_grupo_icu == df_mensual_grupo_icu.max()]
with st.expander('Mostrar (año/mes/ocupación uci)'):
  st.image('./images/peor_mes_icu.png')


# Tomo en cuenta la ocupación hospitalaria
st.markdown("<h3>&#127973 Por ocupacción hospitalaria</h3>", unsafe_allow_html=True)
# Agrego la columna de camas por covid
df_mensual['total_camas'] = df_camas['total_camas']
# Agrupo por año y mes y llamo al mes con mayor ocupacion de camas en todo Estados Unidos
df_mensual_grupo_camas = df_mensual.groupby([df_mensual['date'].dt.year, df_mensual['date'].dt.month])['total_camas'].sum()
peor_mes_ocupacion = df_mensual_grupo_camas.loc[df_mensual_grupo_camas == df_mensual_grupo_camas.max()]
with st.expander('Mostrar (año/mes/ocupación hospitalaria)'):
  st.image('./images/peor_mes_ocupacion.png')




