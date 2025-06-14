# clio

Clio (mental palace)

### Installation
Clone repo and install with pip:
```bash
git clone https://github.com/fsncps/clio.git
cd clio
pip install .
```

#### DB setup
Setup a MySQL/MariaDB database and user:
```sql
CREATE DATABASE clio CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'clio_user'@'localhost' IDENTIFIED BY 'strongpassword';
GRANT ALL PRIVILEGES ON clio.* TO 'cliouser'@'localhost';
FLUSH PRIVILEGES;
```
Import Clio schema:
```bash
mysql -u cliouser -p clio < db/clio_schema.sql
```
Configure environment variable with the connection string:
```bash
mysql -u cliouser -p clio < db/clio_schema.sqexport CLIO_DB_URL="mysql+pymysql://clio_user:strongpassword@localhost/clio"
```


