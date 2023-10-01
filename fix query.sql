-- Pembuatan dan input data untuk tabel customer
CREATE TABLE IF NOT EXISTS public."Customer"
(
    customerid integer NOT NULL,
    age integer,
    gender integer,
    marital_status character varying COLLATE pg_catalog."default",
    income character varying COLLATE pg_catalog."default",
    CONSTRAINT "Customer_pkey" PRIMARY KEY (customerid)
)
--0=wanita, 1=pria
COPY public."Customer" FROM 'D:/matlab/sys/postgresql/win64/PostgreSQL/bin/Customer.csv'  DELIMITER ';' CSV HEADER;
select * from public."Customer"

-- Pembuatan dan input data untuk tabel store
CREATE TABLE IF NOT EXISTS public."Store"
(
	store_id int primary key,
	store_name varchar(100),
	group_store varchar(100),
	type varchar(100),
	latitude varchar(100),
	longitude varchar(100)
);
COPY public."Store" FROM 'D:/matlab/sys/postgresql/win64/PostgreSQL/bin/Store.csv' DELIMITER ';' CSV HEADER;
SELECT * FROM public."Store";

-- Pembuatan dan input data untuk tabel product
CREATE TABLE IF NOT EXISTS public."Product"
(
	productid varchar(100) primary key,
	productname varchar(100),
	price int
);
COPY public."Product" FROM 'D:/matlab/sys/postgresql/win64/PostgreSQL/bin/Product.csv' DELIMITER ';' CSV HEADER;
SELECT * FROM public."Product";

-- Pembuatan dan input data untuk tabel transaction
CREATE TABLE IF NOT EXISTS public."Transaction"
(
	transactionid varchar(100),
	customerid int,
	date varchar(100),
	productid varchar(100) references public."Product"(productid),
	price int,
	qty int,
	totalamount int,
	storeid int references public."Store"(store_id)
);
COPY public."Transaction" FROM 'D:/matlab/sys/postgresql/win64/PostgreSQL/bin/Transaction.csv' DELIMITER ';' CSV HEADER;
SELECT * FROM public."Transaction";

--Akan ditentukan rata-rata umur customer jika dilihat dari marital statusnya
SELECT
    ROUND(AVG(CASE WHEN marital_status = 'Married' THEN age END)) AS rerata_customer_sudah_menikah,
    ROUND(AVG(CASE WHEN marital_status = 'Single' THEN age END)) AS rerata_customer_belum_menikah
FROM
    public."Customer";

--Akan ditentukan rata-rata umur customer berdasarkan gendernya
SELECT
    ROUND(AVG(CASE WHEN gender = '0' THEN age END)) AS rerata_customer_wanita,
    ROUND(AVG(CASE WHEN gender = '1' THEN age END)) AS rerata_customer_pria
FROM
    public."Customer";

--Akan ditentukan nama store dengan total quantity terbanyak
WITH TotalQtyPerStore AS (
  SELECT 
    s.store_name, SUM(t.qty) AS total_quantity
  FROM public."Transaction" t
  JOIN public."Store" s ON t.storeid = s.store_id
  GROUP BY s.store_name
)
SELECT store_name, total_quantity
FROM TotalQtyPerStore
ORDER BY total_quantity DESC
LIMIT 1;

--Akan dientukan nama produk terlaris dengan total amount terbanyak
WITH TotalAmountPerProduct AS (
  SELECT productname, SUM(totalamount) 
  AS total_amount
  FROM public."Transaction" t
  JOIN public."Product" p ON t.productid = p.productid
  GROUP BY productname
)
SELECT productname, total_amount
FROM TotalAmountPerProduct
ORDER BY total_amount DESC
LIMIT 1;