# -*- coding: utf-8 -*-
"""Luthfia-pbi-datascience.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dTqaMQodkFM2QN8etJ-PQVjpFGksAAhv

Import Package
=============================
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn import preprocessing
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import SimpleExpSmoothing, Holt
from statsmodels.tsa.arima.model import ARIMA
from pandas.plotting import autocorrelation_plot
import warnings

warnings.filterwarnings('ignore')

"""Data Reading
=============================================
"""

df_customer = pd.read_csv(r'/content/Customer.csv', delimiter=";")
df_product = pd.read_csv(r'/content/Product.csv', delimiter=";")
df_store= pd.read_csv(r'/content/Store.csv', delimiter=";")
df_transaction= pd.read_csv(r'/content/Transaction.csv', delimiter=";")

print("jumlah baris & kolom tabel customer= ",df_customer.shape)
print("jumlah baris & kolom tabel product= ",df_product.shape)
print("jumlah baris & kolom tabel store= ", df_store.shape)
print("jumlah baris & kolom tabel transaction= ",df_transaction.shape)

"""Data Cleansing
==========================================

cleansing data customer
"""

df_customer.head(5)       #menampilkan 5 baris data pertama dr data customer

#mengubah , menjadi . pada kolom income dan mengubahnya menjadi tipe data float
df_customer['Income']= df_customer['Income'].replace('(,)','.', regex=True).astype(float)

#menghitung data berganda
df_customer.duplicated().sum()

#menampilkan baris data yang memiliki CustomerID ganda
df_customer[df_customer.duplicated(subset=['CustomerID'])]

#mendeteksi kolom yang memiliki nilai Null
df_customer.isnull().any()

#karena kolom marital_status memiliki nilai null, maka akan ditampilkan
#baris data yang memiliki nilai null pada kolom marital_status
df_customer[df_customer['Marital Status'].isnull()]

#menghapus baris data yang memiliki nilai null
df_customer.dropna(subset=['Marital Status'], inplace=True)

"""cleansing data product"""

#menampilkan 5 baris data pada df_product
df_product.head(5)

#menampilkan baris data yang memiliki ProductID ganda
df_product[df_product.duplicated(subset=['ProductID'])]

#mendeteksi kolom yang memiliki nilai Null
df_product.isnull().any()

"""cleansing data store"""

#menampilkan 5 baris data pada df_store
df_store.head(5)

#mengubah , menjadi . pada kolom latitude dan longitude
#dan mengubahnya menjadi tipe data float
df_store['Latitude']=df_store['Latitude'].replace('(,)','.', regex=True).astype(float)
df_store['Longitude']=df_store['Longitude'].replace('(,)','.', regex=True).astype(float)

#mendeteksi kolom yang memiliki nilai Null
df_store.isnull().any()

#menampilkan baris data yang memiliki StoreID ganda
df_store[df_store.duplicated(subset=['StoreID'])].sum()

"""cleansing data transaction"""

#menampilkan 5 baris data pada df_transaction
df_transaction.head(5)

#mengubah datatype kolom date
df_transaction['Date']=pd.to_datetime(df_transaction['Date'])

#menghitung baris data yang terduplikat
df_transaction.duplicated().sum()

#menampilkan TransactionID yang muncul lebih dari sekali
value_counts = df_transaction['TransactionID'].value_counts()
value_counts[value_counts > 1]

#menampilkan baris data yang memiliki TransactionID di tanggal yang sama
duplicate_dates = df_transaction.groupby(['TransactionID', 'Date']).size()
duplicate_dates[duplicate_dates > 1]

#mengurutkan data berdasarkan yang telama hingga terbaru
df_transaction = df_transaction.sort_values('Date', ascending=True)
#menghapus data lama yang memiliki TransactionID yang sama dan mempertahankan
#data terbaru
df_transaction.drop_duplicates(subset='TransactionID', keep='last', inplace=True)
#melakukan pengecekan ulang kembali
value_counts = df_transaction['TransactionID'].value_counts()
value_counts[value_counts > 1]

"""#Menggabungkan Data"""

#menggabungkan seluruh data
df_merged=pd.merge(df_transaction, df_customer, on=['CustomerID'])
df_merged=pd.merge(df_merged, df_product.drop(columns=['Price']), on=['ProductID'])
df_merged=pd.merge(df_merged, df_store, on=['StoreID'])

#menampilkan 5 baris data df_merged (data gabungan)
df_merged.head(5)

"""#Model ML Regression (Time Series)
Hal ini dilakukan untuk mendapatkan prediksi total quantity untuk stock harian yang dibutuhkan oleh tim Inventory
"""

#membuat data baru untuk regression
df_regretion = df_merged.groupby(['Date']).agg({
    'Qty': 'sum'
}).reset_index()

#menampilkan tabel df_regretion yang telah dibuat
df_regretion

# Melakukan dekomposisi seasonal
decomposed = seasonal_decompose(df_regretion.set_index('Date'))

# Mengatur ukuran figure
plt.figure(figsize=(8,8))
# Menampilkan trend
plt.subplot(311)
decomposed.trend.plot(ax=plt.gca())
plt.title('Trend')
# Menampilkan seasonal
plt.subplot(312)
decomposed.seasonal.plot(ax=plt.gca())
plt.title('Seasonal')
# Menampilkan residu
plt.subplot(313)
decomposed.resid.plot(ax=plt.gca())
plt.title('Residual')
# Mengatur layout agar rapi
plt.tight_layout()

from statsmodels.tsa.stattools import adfuller
# Melakukan uji Augmented Dickey-Fuller (ADF) pada kolom Qty dari data 'df_regretion'
result = adfuller(df_regretion['Qty'])
# Menampilkan ADF Statistic, p-value, dan Critical Values dari hasil uji ADF
print('ADF Statistic: %f' % result[0])
print('p-value: %f' % result[1])
print('Critical Values:')
for key, value in result[4].items():
    print('\t%s: %.3f' % (key, value))

# Bagi data menjadi train dan test
cut_off = round(df_regretion.shape[0] * 0.8)
df_train = df_regretion[:cut_off]
df_test = df_regretion[cut_off:]

df_train

df_test

# Gunakan 'Qty' dari df_train sebagai target (y)
y = df_train['Qty']

# Latih model ARIMA
ARIMAmodel = ARIMA(y, order=(40, 2, 1))
ARIMAmodel = ARIMAmodel.fit()

# Prediksi
y_pred = ARIMAmodel.get_forecast(steps=len(df_test))
y_pred_out = y_pred.predicted_mean

# Evaluasi prediksi
def eval(y_actual, y_pred):
    print(f'RMSE value: {mean_squared_error(y_actual, y_pred)**0.5}')
    print(f'MAE value: {mean_absolute_error(y_actual, y_pred)}')

eval(df_test['Qty'], y_pred_out)

# Plot hasil
plt.figure(figsize=(13, 4))
plt.plot(df_train.index, df_train['Qty'], label='Train')
plt.plot(df_test.index, df_test['Qty'], color='green', label='Test')
plt.plot(df_test.index, y_pred_out, color='black', label='ARIMA Prediction')
plt.xlabel('Date')  # Tambahkan label untuk sumbu x
plt.legend()
plt.show()

# Prediksi 30 hari ke depan setelah df_test
forecast_period = 30
forecast = ARIMAmodel.forecast(steps=forecast_period)

# Tampilkan tabel hasil prediksi
forecast_df = pd.DataFrame({
    'Qty Prediction': forecast
})
print(forecast_df)

"""#Model ML Clustering
hal ini dilakukan agar mendapatkan segment customer yang dibutuhkan oleh tim marketing
"""

#meninjau korelasi pada kolom kolom di data gabungan
df_merged.corr()

# Mengelompokkan data berdasarkan 'CustomerID' dan melakukan agregasi
# untuk mendapatkan informasi statistik terkait setiap pelanggan.
df_cluster=df_merged.groupby(('CustomerID')).agg({
    'TransactionID':'count', #Jumlah transaksi yg dilakukan
    'Qty':'sum', #Total kuantitas
    'Age':'first' #Usia pertama tercatat
}).reset_index()
df_cluster.rename(columns={'TransactionID': 'JumlahTransaksi', 'Qty': 'TotalQty'}, inplace=True)
#menampilkan beberapa baris data untuk df_clustering
df_cluster.head()

data_cluster=df_cluster.drop(columns=['CustomerID']) #menghapus kolom CustomerID
data_cluster_normalize=preprocessing.normalize(data_cluster) #mernomalisasi data
print(data_cluster_normalize)

#membuat grafik elbow method
K = range(2, 9)

fits = []
score = []

for k in K:
    model = KMeans(n_clusters=k, random_state=0, n_init='auto')
    model.fit(data_cluster_normalize)
    fits.append(model)
    labels = model.predict(data_cluster_normalize)
    score.append(silhouette_score(data_cluster_normalize, labels))

# Menampilkan grafik Elbow Method
plt.figure(figsize=(8,4))
sns.lineplot(x=K, y=score)
plt.xlabel('Number of Clusters (K)')
plt.ylabel('Silhouette Score')
plt.title('Silhouette Score vs. Number of Clusters')
plt.xticks(K)  # Tampilkan semua nilai K pada sumbu x
plt.show()

fits[2]

df_cluster['cluster_label']=fits[2].labels_ #masukkan cluster label ke data awal
df_cluster #menampilkan data yang baru

# Mengelompokkan data berdasarkan label kluster dan menghitung statistik untuk setiap variabel
# Menghitung jumlah CustomerID, rata-rata JumlahTransaksi, rata-rata TotalQty, dan rata-rata Age untuk setiap kluster
cluster_summary = df_cluster.groupby(['cluster_label']).agg({
    'CustomerID': 'count',  # Menghitung jumlah CustomerID di setiap kluster
    'JumlahTransaksi': 'mean',  # Menghitung rata-rata JumlahTransaksi di setiap kluster
    'TotalQty': 'mean',  # Menghitung rata-rata TotalQty di setiap kluster
    'Age': 'mean'  # Menghitung rata-rata Age di setiap kluster
})

"""Cluster 0:
Dalam cluster ini rata-rata transaksi yang dilakukan sekitar 10.1 transaksi. Dan rata-rata total barang yang dibeli oleh customer dalam cluster ini adalah sekitar 35,6. Usia rata-rata customer dalam cluster ini adalah sekitar 46,4 tahun. Cluster ini mungkin mewakili customer dengan tingkat aktivitas belanja menengah hingga tinggi, dengan usia di sekitar pertengahan hingga akhir.

Cluster 1:

Rata-rata transaksi yang dilakukan oleh customer dalam cluster ini adalah sekitar 7.8 transaksi. Dan rata-rata total barang yang dibeli oleh customer dalam cluster ini adalah sekitar 25.8. Rata-rata usia customer dalam cluster ini adalah sekitar 50.5 tahun. Cluster ini mungkin mewakili customer dengan tingkat aktivitas belanja yang lebih rendah dibandingkan dengan cluster lain, dengan usia cenderung lebih tua.

Cluster 2:

Rata-rata transaksi yang dilakukan oleh customer dalam cluster ini adalah sekitar 13.1 transaksi. Rata-rata total barang yang dibeli oleh customer dalam cluster ini adalah sekitar 50.7. Rata-rata usia customer dalam cluster ini adalah sekitar 27.0 tahun. Cluster ini mungkin mewakili customer dengan tingkat aktivitas belanja yang tinggi, dengan usia relatif muda.

Cluster 3:

Rata-rata transaksi yang dilakukan oleh customer dalam cluster ini adalah sekitar 11.8 transaksi. Rata-rata total barang yang dibeli oleh customer dalam cluster ini adalah sekitar 43.0. Rata-rata usia customer dalam cluster ini adalah sekitar 37.9 tahun. Cluster ini mungkin mewakili customer dengan tingkat aktivitas belanja yang cukup tinggi, dengan usia di tengah-tengah.



#Rekomendasi bisnis:
*   Cluster 2 (tingkat aktivitas belanja tinggi, usia muda) dapat menjadi fokus kampanye pemasaran untuk produk-produk baru atau promosi.
*   Cluster 1 (tingkat aktivitas belanja rendah, usia lebih tua) dapat diincar dengan program diskon khusus atau penawaran yang menarik untuk mendorong pembelian lebih lanjut.

Analisis lebih lanjut diperlukan untuk memahami karakteristik dan preferensi pelanggan di setiap cluster guna menyusun strategi pemasaran yang lebih tepat.






"""