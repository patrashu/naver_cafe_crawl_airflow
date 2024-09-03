## 에어플로우를 활용한 네이버 카페 크롤링

### File Directory
```
📂root
┗ 📂config
    ┗ 📜login_info.env
    ┗ 📜ioniq_cafe_info.env
┗ 📂dags
    ┗ 📂crawl
        ┗ 📜naver_cafe.env
        ┗ 📂utils
            ┗ 📜__init__.py
            ┗ 📜utils.py
┗ 📂data
    ┗ 📜ioniq.sql
    ┗ 📜create_ioniq.sql
┗ 📂logs
┗ 📂plugins
┗ 📜.gitignore
┗ 📜docker-compose.yaml
┗ 📜Dockerfile
┗ 📜README.md
┗ 📜requirements.txt
```


### Usage
- docker-compose.yaml에 들어간 apache-airflow 이미지에 추가로 필요한 라이브러리 설치를 위해 Dockerfile을 작성했습니다.
- compose file 내 image tag를 주석처리하고, build를 활성화 시킨 후 추가로 작업할 부분들을 Dockerfile에 같이 추가해줍니다.
- 초기 airflow UI (8080 port) ID/PW는 airflow/airflow이며, 추후 수정할 예정입니다.

    ```bash
    docker compose up -d
    ```

### Notice
- Naver Login 정보는 config/login_info.env로 설정하면 됩니다.
- remote server로 웹 크롤링을 수행하기 위해 [여기](https://hub.docker.com/r/selenium/standalone-chrome) 링크에 접속하여 이미지를 다운받습니다. 
- 필요한 파일들은 DAG 폴더 내에서 작업을 진행합니다.
- config/naver_cafe_info.yaml에 들어가서 원하는 카페와 keyword를 설정하면, 다양한 차종을 모니터링 할 수 있습니다.
- 아이오닉 동호회 카페에서 3달 간의 차량의 결함/이슈 관련 소비자 관심도를 분석하는 과정을 수행합니다. 