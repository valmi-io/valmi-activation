<p align="center">
  <a href="https://valmi.io"><img width="400" src="https://www.valmi.io/img/logo.svg" alt="valmi.io"></a>
</p>

<p align="center">
  <b>
    <a href="https://www.valmi.io">Website</a>
    ·
    <a href="https://www.valmi.io/slack">Slack Community</a>
    ·
    <a href="https://docs.valmi.io">Documentation</a>
  </b>
</p>

<p align="center">
    <em> <a href="https://valmi.io">valmi.io</a> activation (reverse-ETL) is the open-source data activation platform to load data from warehouses into SaaS platforms, Webhook Apis etc.</em>
</p>
<p align="center">
<a href="https://github.com/valmi-io/valmi-activation/stargazers/" target="_blank">
    <img src="https://img.shields.io/github/stars/valmi-io/valmi-activation?style=social&label=Star&maxAge=10000" alt="Test">
</a>
  
<a href="https://github.com/valmi-io/valmi-activation/blob/main/LICENSE.md" target="_blank">
    <img src="https://img.shields.io/static/v1?label=license&message=MIT&color=white" alt="License">
</a> 
</p>

<p align="center">valmi.io uses some of the best tools to create an Open Source Activation (reverse ETL) Platform. It is built over the <a href="https://airbyte.com/">airbyte</a> protocol. <a href="https://www.getdbt.com/">dbt</a> is the centerpiece of our source connectors, and <a href="https://duckdb.org/">duckdb</a> for metrics. We engineered our orchestrator over <a href="https://dagster.io/">dagster</a>, and dagster dovetails perfectly with our vision of being a multi-persona tool.  </p>
  
 <p align="center">We envision a world where a vibrant community of engineers develops around connectors - a world in which the power of the open-source platform draws on the collective mind to keep the fast-moving world of connectors functional and cost-effective.</p>


### a. How to Run?

Demo at https://demo.valmi.io

OR

Run locally as below

1. Clone this repo and move into the directory.
```
git clone git@github.com:valmi-io/valmi-activation.git
cd valmi-activation
git submodule update --init --recursive

```

2. Setup the environment
```
cd valmi-app-backend
cp .env-sample .env

cd ../valmi-app
cp .env-example .env
```
3. Make connectors
```
cd valmi-integrations/connectors/source-postgres
make build_docker

cd valmi-integrations/connectors/destination-webhook
make build_docker
```

4. Run the service
```
docker-compose up -d --build
```

5. We are adding support for object stores like S3, GCS. Until then, Local storage is used.
```
sudo chmod -R 777 /tmp/shared_dir/intermediate_store
```

6. Access the service

```
http://localhost:3000
```

UI Backend API Server (http://localhost:4000/api/docs)       |  Activation Server Api (http://localhost:8000/docs)
:-------------------------:|:-------------------------:
![]( https://blog.valmi.io/content/images/2023/06/api-4000.png)  |  ![]( https://blog.valmi.io/content/images/2023/06/api-8000.png)

  Warehouses and Destinations   |  Sync Runs
:-------------------------:|:-------------------------:
![]( https://blog.valmi.io/content/images/2023/06/connections.png)  |  ![](https://blog.valmi.io/content/images/2023/06/sync_runs.png)

#### Watch the demo video here. 
[<img  src="https://i.ytimg.com/vi/UEC3-C4_7nk/maxresdefault.jpg" width="50%"/>](https://www.youtube.com/watch?v=UEC3-C4_7nk "Watch the demo video") 

#### b. TODO:
- Describe architecture details

- Write Vision

- Describe licenses

- Write known issues & Roadmap
  1. Inject checkpoint state for re-runs.
  2. remove hard-coded references to **/tmp/shared_dir** 
  3. Add support for object stores like S3, GCS etc.
  4. can only work with single worker uvicorn, to go multiprocess, acquire lock for metrics, job_manager & run_manager& warmup processes.
  5. Share the dbSession.
  6. ...
