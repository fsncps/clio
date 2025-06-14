# clio

Clio, a digital mental palace and note taking database where I record ideas, code snippets, sources and references, writing projects etc. Organized in tree hierarchy, where any species of record can hold any other (apart from the top "genus").

## Functionality

- Create records of different kinds: "Note", "Book", "Topic", "Code", "Text" etc.
- Organize in a mind map tree an move around
- Add appendices (sources, references, URLs)
- Generate vector embeddings of the records
- Create dynamic relations between records
- Create notes with cli tool `clio note`
    - pipe command output to a note: `tail ~/.clio/clio_log.txt | clio note`
    - redirect, e.g. file content: `clio note < /.clio/clio_log.txt`

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
GRANT ALL PRIVILEGES ON clio.* TO 'clio_user'@'localhost';
FLUSH PRIVILEGES;
```
Import Clio schema:
```bash
mysql -u clio_user -p clio < db/clio_schema.sql
```
Configure environment variable with the connection string:
```bash
export CLIO_DB_URL="mysql+pymysql://cliouser:strongpassword@localhost/clio"
```


