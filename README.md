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
    <em> <a href="https://valmi.io">valmi.io</a> is the open-source Reverse-ETL (data activation) platform to load data from warehouses into SaaS platforms, Webhook Apis etc.</em>
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

  <!---
<a href="/../../issues?q=is%3Aopen+is%3Aissue"> <img alt="GitHub issues" src="https://img.shields.io/github/issues-raw/valmi-io/valmi-activation?color=%23238636"></a> <a href="/../../issues?q=is%3Aissue+is%3Aclosed"> <img alt="GitHub closed issues" src="https://img.shields.io/github/issues-closed-raw/valmi-io/valmi-activation?color=%238957e5"> </a> <a href="/../../pulls?q=is%3Aopen+is%3Apr"> <img alt="GitHub pull requests" src="https://img.shields.io/github/issues-pr-raw/valmi-io/valmi-activation"> </a> <a href="/../../pulls?q=is%3Apr+is%3Aclosed"> <img alt="GitHub closed pull requests" src="https://img.shields.io/github/issues-pr-closed-raw/valmi-io/valmi-activation?color=%238957e5"> </a>
  --->
</div>
<p align="center">valmi.io uses some of the best tools to create an Open Source reverse-ETL (data activation) Platform. It is built over the <a href="https://airbyte.com/">airbyte</a> protocol. <a href="https://www.getdbt.com/">dbt</a> is the centerpiece of our source connectors, and <a href="https://duckdb.org/">duckdb</a> for metrics. We engineered our orchestrator over <a href="https://dagster.io/">dagster</a>, and dagster dovetails perfectly with our vision of being a multi-persona tool.  </p>
  
 <p align="center">We envision a world where a vibrant community of engineers develops around connectors - a world in which the power of the open-source platform draws on the collective mind to keep the fast-moving world of connectors functional and cost-effective.</p>

- ### Checkout docs at - [https://docs.valmi.io](https://docs.valmi.io/)
- ### Read the variety of usecases valmi.io will enable for your organization - [https://blog.valmi.io/](https://blog.valmi.io/)  
- ### 3 ways to start with valmi.io
    
    #### 1. See it in Action
    - You can quickly witness a One Million Record Sync at [Live Sync](https://demo.valmi.io/spaces/a9195c50-60ca-4692-8f03-5a486ee9f270/syncs/d69cf9f9-0e20-4e2c-a683-2649404f52ed/runs).
    - You can immediately create a sync at [https://demo.valmi.io.](https://demo.valmi.io/)
    - Watch demo video on creating a sync.
      
    <div align="center" >
      
  [<img  src="https://blog.valmi.io/content/images/size/w1000/2023/06/syncs_demo.png" width="90%" />](https://www.youtube.com/watch?v=um-Hgij3rL4 "Watch the demo video") 

    </div>
    
    #### 2.  Run it locally or in your Cloud
    
    - Clone this repo and move into the directory.
      ```bash
      git clone git@github.com:valmi-io/valmi-activation.git
      cd valmi-activation
      git submodule update --init --recursive
      ```
    
    - Setup the environment.
      ```bash
      
      cp .env-example .env
      
      cd valmi-app-backend
      cp .env-example .env
      
      cd ../valmi-app
      `For macos`
      cp .env-example.macos .env
      `For linux`
      cp .env-example.linux .env
      ```
    
    - Intermediate storage, We are adding support for object stores like S3, GCS. Until then, Local storage is used.
      ```bash
      sudo mkdir -p /tmp/shared_dir/intermediate_store
      sudo chmod -R 777 /tmp/shared_dir/intermediate_store
      ```
    
    - Launch the reverse-etl service.
      ```bash
      ./valmi prod
      ```
      
    - To stop the service, run the following.
      ```bash
      ./valmi prod down
      ```
      
    - Please wait for about 2 minutes before you access the service, since valmi-app builds an optimized compiled version of the app UI. To access the service, please check the ['Accessing the service'](https://github.com/valmi-io/valmi-activation#accessing-the-service-for-local-deployments) section for local deployments.
    
    
    #### 3. Develop a connector locally to customize valmi.io as per your needs. You can just contact us too.
    
    - Clone, setup environment variables and create intermediate storage (see above section).
    - Create a new connector (Optional).
      ```bash
      # Copy code base from any existing connectors from valmi-integrations folder (ex. destination-webhook)
      
      cd valmi-integrations/connectors
      cp -r destination-webhook destination-awesome_connector
      
      # Make necessary changes and build the connector
      cd destination-awesome_connector
      make build_docker version=latest
      
      # Add the new connector information to "valmi-app-backend/init_db/connector_def.json"
      ```
    
    - Run the service.
      ```bash
      ./valmi dev
      ```
       
    - To access the service, please check the ['Accessing the service'](https://github.com/valmi-io/valmi-activation#accessing-the-service-for-local-deployments) section for local deployments.

    - To Stop the service, run the following.
      ```bash
      ./valmi dev down
      ```
    
- ### Accessing the service for local deployments
  
    Syncs http://localhost:3000  |  Sync Runs http://localhost:3000
    :-------------------------:|:-------------------------:
    ![](https://blog.valmi.io/content/images/size/w1000/2023/06/syncs_page.png)  |  ![](https://blog.valmi.io/content/images/size/w1000/2023/06/sync_runs_page.png)

    UI Backend Server API http://localhost:4000/api/docs       |  Activation Server API http://localhost:8000/docs
    :-------------------------:|:-------------------------:
    ![](https://blog.valmi.io/content/images/size/w1000/2023/06/app_backend_api.png)  |  ![](https://blog.valmi.io/content/images/size/w1000/2023/06/activation_server_api.png)

  
    

