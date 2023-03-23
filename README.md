<p align="center">
  <a href="https://valmi.io"><img width="300" src="https://www.valmi.io/img/logo.svg" alt="valmi.io"></a>
</p>
<p align="center">
    <em>valmi.io activation (reverse-ETL) is the open-source data activation platform to load data from warehouses into SaaS platforms, Webhook Apis etc.</em>
</p>
<p align="center">
<a href="https://github.com/valmi-io/valmi-activation/stargazers/" target="_blank">
    <img src="https://img.shields.io/github/stars/valmi-io/valmi-activation?style=social&label=Star&maxAge=2592000" alt="Test">
</a>
  
<a href="https://github.com/valmi-io/valmi-activation/blob/main/LICENSE.md" target="_blank">
    <img src="https://img.shields.io/static/v1?label=license&message=MIT&color=white" alt="License">
</a> 
</p>



#### **TODO**:
- How to Run section

- Describe technology

- Write Vision

- Describe licenses

- Write known issues & Roadmap
  1. remove hard-coded references to **/tmp/shared_dir** 
  2. Add support for object stores like S3, GCS etc.
  3. can only work with single worker uvicorn, to go multiprocess, acquire lock for metrics, job_manager & run_manager& warmup processes.
  4. Share the dbSession.
  5. ...
