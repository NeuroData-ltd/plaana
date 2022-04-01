mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
mysql --user cp1425760p08_contrapid --password 02MNeJXVsao+ --host localhost --port 3306 cp1425760p08_contrapid < "cp1425760p08_contrapid.sql"
