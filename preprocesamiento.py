import pandas as pd

df = pd.read_excel("data\Prestamos_Data_Alumnos_v5.xlsx")
df.head()

df.info

df.dtypes

# mirar cuantos duplicados hay
df['Proposito'].duplicated().value_counts()

# hacemos copia por si acaso
copia = df.copy()

copia.shape
#filtrar por vivienda => lo que nos toca
copia = copia[copia["Proposito"] == "Vivienda"]
copia.head()

copia['Proposito'].value_counts()

# ver las filas de duplicados
duplicados=copia[copia.duplicated()]
duplicados

id_dup=copia[copia['ID']=='AIJ783']
id_dup

#mirar valores nulos
copia.isna().sum()

#sustituir nulos por las medias
media_duracion = copia['Duracion'].mean()

copia['Duracion']=copia['Duracion'].fillna(media_duracion)

copia['Duracion'] = copia['Duracion'].isna().sum()

copia["Estudios"]