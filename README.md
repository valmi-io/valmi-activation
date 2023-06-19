<p align="center">
  <a href="https://valmi.io"><img width="400" src="https://blog.valmi.io/content/images/2023/06/valmilogo-1.png" alt="valmi.io"></a>
</p>

<p align="center">
  <b>
    <a href="https://www.valmi.io">Website</a>
    ·
    <a href="https://www.valmi.io/slack">Slack Community</a>
    ·
    <a href="https://docs.valmi.io">Documentation</a>
    ·
    <a href="https://blog.valmi.io">Blog</a>
  </b>
</p>

<p align="center">
    <em> <a href="https://valmi.io">valmi.io</a> is a open-source Reverse ETL (data activation) platform to load data from warehouses into SaaS platforms, Webhook Apis etc.</em>
</p>
<p align="center">
<a href="https://github.com/valmi-io/valmi-activation/stargazers/" target="_blank">
    <img src="https://img.shields.io/github/stars/valmi-io/valmi-activation?style=social&label=Star&maxAge=10000" alt="Test">
</a>
<a href="https://github.com/valmi-io/valmi-activation/blob/main/LICENSE.md" target="_blank">
    <img src="https://img.shields.io/static/v1?label=license&message=MIT&color=white" alt="License">
</a>
</p>
<div align="center" >

[![valmi-activation](https://github.com/valmi-io/valmi-activation/actions/workflows/valmi-activation-docker-image-action.yml/badge.svg)](https://github.com/valmi-io/valmi-activation/actions/workflows/valmi-activation-docker-image-action.yml) [![valmi-connectors](https://github.com/valmi-io/valmi-activation/actions/workflows/valmi-connectors-docker-image-action.yml/badge.svg)](https://github.com/valmi-io/valmi-activation/actions/workflows/valmi-connectors-docker-image-action.yml) [![valmi-dagster](https://github.com/valmi-io/valmi-activation/actions/workflows/valmi-dagster-docker-image-action.yml/badge.svg)](https://github.com/valmi-io/valmi-activation/actions/workflows/valmi-dagster-docker-image-action.yml) 
<br/>
[![valmi-repo](https://github.com/valmi-io/valmi-activation/actions/workflows/valmi-repo-docker-image-action.yml/badge.svg)](https://github.com/valmi-io/valmi-activation/actions/workflows/valmi-repo-docker-image-action.yml) [![valmi-app-backend](https://github.com/valmi-io/valmi-app-backend/actions/workflows/valmi-app-backend-docker-image-action.yml/badge.svg)](https://github.com/valmi-io/valmi-app-backend/actions/workflows/valmi-app-backend-docker-image-action.yml) [![valmi-app](https://github.com/valmi-io/valmi-app/actions/workflows/valmi-app-docker-image-action.yml/badge.svg)](https://github.com/valmi-io/valmi-app/actions/workflows/valmi-app-docker-image-action.yml)

  
<a href="/../../issues?q=is%3Aopen+is%3Aissue"> <img alt="GitHub issues" src="https://img.shields.io/github/issues-raw/valmi-io/valmi-activation?color=%23238636"></a> <a href="/../../issues?q=is%3Aissue+is%3Aclosed"> <img alt="GitHub closed issues" src="https://img.shields.io/github/issues-closed-raw/valmi-io/valmi-activation?color=%238957e5"> </a> <a href="/../../pulls?q=is%3Aopen+is%3Apr"> <img alt="GitHub pull requests" src="https://img.shields.io/github/issues-pr-raw/valmi-io/valmi-activation"> </a> <a href="/../../pulls?q=is%3Apr+is%3Aclosed"> <img alt="GitHub closed pull requests" src="https://img.shields.io/github/issues-pr-closed-raw/valmi-io/valmi-activation?color=%238957e5"> </a>
  
</div>
<p align="center">valmi.io uses some of the best tools to create an Open Source Activation (reverse ETL) Platform. It is built over the <a href="https://airbyte.com/">airbyte</a> protocol. <a href="https://www.getdbt.com/">dbt</a> is the centerpiece of our source connectors, and <a href="https://duckdb.org/">duckdb</a> for metrics. We engineered our orchestrator over <a href="https://dagster.io/">dagster</a>, and dagster dovetails perfectly with our vision of being a multi-persona tool.  </p>
  
 <p align="center">We envision a world where a vibrant community of engineers develops around connectors - a world in which the power of the open-source platform draws on the collective mind to keep the fast-moving world of connectors functional and cost-effective.</p>

### Demo Page
https://demo.valmi.io

### Run Locally

1. Clone this repo and move into the directory.
```bash
git clone git@github.com:valmi-io/valmi-activation.git
cd valmi-activation
git submodule update --init --recursive
```

2. Setup the environment
```bash
cp .env-sample .env

cd valmi-app-backend
cp .env-sample .env

cd ../valmi-app
cp .env-example .env
```

3. Intermediate storage, We are adding support for object stores like S3, GCS. Until then, Local storage is used.
```bash
sudo mkdir -p /tmp/shared_dir/intermediate_store
sudo chmod -R 777 /tmp/shared_dir/intermediate_store
```

4. And run
```bash
./valmi prod
```

5. For stopping service
```bash
./valmi prod down
```


### Develop Locally

1. Clone, setup environment variables and create intermediate storage (see above section)
2. New connector (Optional)
```bash
# Copy code base from any existing connectors from valmi-integrations folder (ex. destination-webhook)

cd valmi-integrations/connectors
cp -r destination-webhook your-awesome-connector

# Make necessary changes and build the connector
cd your-awesome-connector
make build_docker version=latest

# Add new connector information to "valmi-app-backend/init_db/connector_def.json"
```

3. Run the service
```bash
./valmi dev
```
 
4. Access the service
<pre>
 <code>
  <a href="http://localhost:3000">http://localhost:3000</a>
 </code>
</pre>
  

UI Backend API Server (http://localhost:4000/api/docs)       |  Activation Server Api (http://localhost:8000/docs)
:-------------------------:|:-------------------------:
![]( https://blog.valmi.io/content/images/2023/06/api-4000.png)  |  ![]( https://blog.valmi.io/content/images/2023/06/api-8000.png)

  Warehouses and Destinations   |  Sync Runs
:-------------------------:|:-------------------------:
![]( https://blog.valmi.io/content/images/2023/06/connections.png)  |  ![](https://blog.valmi.io/content/images/2023/06/sync_runs.png)

#### Watch the demo video here. 
[<img  src="https://i.ytimg.com/vi/UEC3-C4_7nk/maxresdefault.jpg" width="50%"/>](https://www.youtube.com/watch?v=UEC3-C4_7nk "Watch the demo video") 

5. Stop the service
```bash
./valmi dev down
```

#### Docs: https://docs.valmi.io
#### Usecases: https://blog.valmi.io
