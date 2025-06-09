# Conexion a una base de datos MySQL
import pandas as pd

# Leer el archivo CSV
ruta_archivo = 'C:/Users/LENOVO/Downloads/Accidentalidadbq.csv'  # Reemplaza con la ruta real de tu archivo
df = pd.read_csv(ruta_archivo)

# Ver las primeras filas del DataFrame
print(df.head())


# Exploracion y limpieza

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

print(" Análisis de accidentalidad vial en la ciudad de Barranquilla 2022-2025")

columnas = ["Fecha_Accidente", "DIRECCION ACCIDENTE", "CONDICION_VICTIMA", "GRAVEDAD_ACCIDENTE", "CLASE_ACCIDENTE",
             "SEXO_VICTIMA", "EDAD_VICTIMA", "CANTIDAD_VICTIMAS",]
df = df[columnas]

print(df)
print(df.shape)
print(df.dtypes)

#Separar la columna Fecha_Accidente en dos columnas: FECHA y HORA
df[['FECHA', 'HORA']] = df['Fecha_Accidente'].str.split(' ', n=1, expand=True)
df['FECHA'] = pd.to_datetime(df['FECHA'], format='%m/%d/%Y',errors='coerce')

df.drop('HORA', axis=1, inplace=True)
df.drop('Fecha_Accidente', axis=1, inplace=True)

df =df.astype (
    {
    'DIRECCION ACCIDENTE': 'string',
    'CONDICION_VICTIMA':'string',
    'GRAVEDAD_ACCIDENTE':'string',
    'CLASE_ACCIDENTE':'string',
    'SEXO_VICTIMA':'string',
    
})
print(df.info())
#Antes de eliminar
print(f"\n Duplicados antes de limpiar: {df.duplicated().sum()}")
print(df.duplicated())

# Eliminar duplicados
df = df.drop_duplicates()
print(f"\n Duplicados después de limpiar: {df.duplicated().sum()}")

print("Valores nulos antes de limpieza:\n",df.isnull().sum())

df['EDAD_VICTIMA'] = pd.to_numeric(df['EDAD_VICTIMA'], errors='coerce')
df['CANTIDAD_VICTIMAS'] = pd.to_numeric(df['CANTIDAD_VICTIMAS'], errors='coerce')


# Eliminar registros con valores cero o nulos o vacios
df = df.dropna()
df = df[df['CANTIDAD_VICTIMAS'] > 0]
df = df[(df['EDAD_VICTIMA'] > 0) & (df['EDAD_VICTIMA'] <= 100)]
df['SEXO_VICTIMA'] = df['SEXO_VICTIMA'].str.strip()
df = df[df['SEXO_VICTIMA'] != '']
df = df.dropna(subset=['SEXO_VICTIMA'])

print("Valores nulos después de limpieza:\n",df.isnull().sum())
print(f"Filas después de limpiar: {len(df)}")

# Nueva columna: Día de la semana
df['DIA_SEMANA'] = df['FECHA'].dt.day_name()

# Nueva columna: Rango de edad
bins = [0, 17, 30, 45, 60, 200]
labels = ['<18', '18-30', '31-45', '46-60', '60+']
df['RANGO_EDAD'] = pd.cut(df['EDAD_VICTIMA'], bins=bins, labels=labels)

#Guardar base de datos limpia con los cambios aplicados
df.to_csv('accidentesbq_limpio.csv', index=False)
# calculos

print("\nConteo de muertes por tipo de accidente")
muertes_por_clase = df[df['GRAVEDAD_ACCIDENTE'] == 'muerto']['CLASE_ACCIDENTE'].value_counts()
print(muertes_por_clase)

print("\nTasa de mortalidad por tipo de accidente - compara cuántas muertes hay en proporción al total de accidentes de cada tipo")
# Total de accidentes por tipo
total_por_clase = df['CLASE_ACCIDENTE'].value_counts()
# Muertes por tipo
muertes_por_clase = df[df['GRAVEDAD_ACCIDENTE'] == 'muerto']['CLASE_ACCIDENTE'].value_counts()
## Tasa de mortalidad
tasa_mortalidad = (muertes_por_clase / total_por_clase).sort_values(ascending=False)
print(tasa_mortalidad)

print("\nComparar motociclistas jóvenes y peatones mayores")
grupo_moto_joven = df[(df['CONDICION_VICTIMA'] == 'Motociclista') & (df['EDAD_VICTIMA'].between(18,30))]
grupo_peaton_mayor = df[(df['CONDICION_VICTIMA'] == 'Peaton') & (df['EDAD_VICTIMA'] > 60)]

print("\nPorcentaje de fatalidad en ambos grupos")
fatal_moto_joven = (grupo_moto_joven['GRAVEDAD_ACCIDENTE'] == 'muerto').mean() * 100
fatal_peaton_mayor = (grupo_peaton_mayor['GRAVEDAD_ACCIDENTE'] == 'muerto').mean() * 100
print(f"Motociclistas jóvenes - % mortalidad: {fatal_moto_joven:.2f}%")
print(f"Peatones mayores - % mortalidad: {fatal_peaton_mayor:.2f}%")

print("\nAnálisis de la relación entre el sexo de la víctima y la gravedad del accidente")
from scipy.stats import chi2_contingency
pd.crosstab(df['SEXO_VICTIMA'], df['GRAVEDAD_ACCIDENTE'])
#Asegurar formato consistente en texto
df['GRAVEDAD_ACCIDENTE'] = df['GRAVEDAD_ACCIDENTE'].str.strip().str.lower()
df['DIRECCION ACCIDENTE'] = df['DIRECCION ACCIDENTE'].str.strip().str.upper()

#Agrupar por dirección y tipo de gravedad
zonas = df.groupby(['DIRECCION ACCIDENTE', 'GRAVEDAD_ACCIDENTE']).size().unstack(fill_value=0)

#Asegurar que existan columnas 'muerto' y 'herido'
for col in ['muerto', 'herido']:
    if col not in zonas.columns:
        zonas[col] = 0

#Calcular total de accidentes
zonas['TOTAL_ACCIDENTES'] = zonas['muerto'] + zonas['herido']
#Top zonas con más fallecidos
top_muertos = zonas.sort_values('muerto', ascending=False).head(10)
print("\nZonas con más víctimas fatales:")

print(top_muertos[['muerto', 'TOTAL_ACCIDENTES']])


#Top zonas con más accidentes totales

top_accidentes = zonas.sort_values('TOTAL_ACCIDENTES', ascending=False).head(10)
print("\nZonas con más accidentes totales:")
print(top_accidentes[['TOTAL_ACCIDENTES', 'muerto']])
# Visualización de datos
#HIPÓTESIS 1:
#GRÁFICO 1: Zonas con más muertos
plt.figure(figsize=(12, 6))
plt.barh(top_muertos.index, top_muertos['muerto'], color='pink')
plt.xlabel('Cantidad de fallecidos')
plt.title('Zonas con mayor cantidad de víctimas fatales')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()

#GRÁFICO 2: Zonas con más accidentes totales
plt.figure(figsize=(12, 6))
plt.barh(top_accidentes.index, top_accidentes['TOTAL_ACCIDENTES'], color='lightblue')
plt.xlabel('Cantidad total de accidentes')
plt.title(' Zonas con mayor cantidad de accidentes')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()

#HIPÓTESIS 2:
#Gravedad según edad y condición
plt.figure()
sns.boxplot(data=df[df['GRAVEDAD_ACCIDENTE'] != 'ileso'], x='CONDICION_VICTIMA', y='EDAD_VICTIMA', hue='GRAVEDAD_ACCIDENTE')
plt.title("Edad y Gravedad según Rol")
plt.xticks(rotation=45)
plt.show()


# Distribución por tipo de accidente
plt.figure()
sns.countplot(data=df, x='CLASE_ACCIDENTE', order=df['CLASE_ACCIDENTE'].value_counts().index)
plt.title('Tipos de Accidente')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Distribución de gravedad
plt.figure()
sns.countplot(data=df, x='GRAVEDAD_ACCIDENTE')
plt.title('Distribución de Gravedad del Accidente')
plt.show()

# Distribución por sexo y condición
plt.figure()
sns.countplot(data=df, x='SEXO_VICTIMA', hue='CONDICION_VICTIMA')
plt.title('Sexo vs Rol en el Accidente')
plt.show()

#¿Qué clase de accidentes causa más muertes?
sns.countplot(data=df[df['GRAVEDAD_ACCIDENTE'] == 'muerto'], x='CLASE_ACCIDENTE', order=df['CLASE_ACCIDENTE'].value_counts().index)
plt.title("Tipo de Accidente vs Muertes")
plt.xticks(rotation=45)
plt.show()

#Tasa de mortalidad por grupo de edad
edad_muertes = df[df['GRAVEDAD_ACCIDENTE'] == 'muerto']['RANGO_EDAD'].value_counts(normalize=True)
edad_total = df['RANGO_EDAD'].value_counts(normalize=True)
riesgo = (edad_muertes / edad_total).sort_values(ascending=False)

riesgo.plot(kind='bar', title="Tasa de mortalidad por Rango de Edad", color='cyan')
plt.ylabel("Tasa Mortalidad")
plt.show()
