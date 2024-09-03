## 에어플로우를 활용한 네이버 카페 크롤링

### Service Link
- 추후 추가 예정

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
- remote server로 웹 크롤링을 수행하기 위해 [해당 링크](https://hub.docker.com/r/selenium/standalone-chrome)에 접속하여 이미지를 다운받습니다. 
- docker-compose.yaml에 들어간 apache-airflow 이미지에 추가로 필요한 라이브러리 설치를 위해 Dockerfile을 작성했습니다.
- compose file 내 image tag를 주석처리하고, build를 활성화 시킨 후 추가로 작업할 부분들을 Dockerfile에 같이 추가해줍니다.
    ```bash
    docker compose up -d
    ```
- 필요한 파일들은 DAG 폴더 내에서 작업을 진행합니다.

### Notice
- Naver Login 정보는 config/login_info.env로 설정하면 됩니다.
- data/ 경로에 sql 관련 파일들을 같이 업로드해주시면 됩니다.
- config/naver_cafe_info.yaml에 들어가서 원하는 카페와 keyword를 설정하면, 다양한 차종을 모니터링 할 수 있습니다.
- PostgresOperator를 사용하려면, connection_id를 airflow에 등록해야합니다. 이때, host_name을 container_name으로 지정해줍니다.

### Goal
- [O] 주기적으로 에러없이 크롤링을 수행하고 DB에 저장하는 파이프라인을 구축합니다. 
- [O] 작업 성공/실패시 Slack을 통해 알림을 주는 로직을 구현합니다.
- [ ] 아이오닉 동호회 카페에서 3달 간의 차량의 결함/이슈 관련 소비자 관심도를 분석하는 과정을 수행합니다. 

### DB 저장 및 Slack 알림 결과