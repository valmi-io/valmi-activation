<p align="center">
  <a href="https://valmi.io"><img width="400" src="https://www.valmi.io/img/logo.svg" alt="valmi.io"></a>
</p>
<p align="center">
    <em>valmi.io activation (reverse-ETL) is the open-source data activation platform to load data from warehouses into SaaS platforms, Webhook Apis etc.</em>
</p>
<p align="center">
<a href="https://github.com/valmi-io/valmi-activation/stargazers/" target="_blank">
    <img src="https://img.shields.io/github/stars/valmi-io/valmi-activation?style=social&label=Star&maxAge=10000" alt="Test">
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
  1. Inject checkpoint state for re-runs.
  2. remove hard-coded references to **/tmp/shared_dir** 
  3. Add support for object stores like S3, GCS etc.
  4. can only work with single worker uvicorn, to go multiprocess, acquire lock for metrics, job_manager & run_manager& warmup processes.
  5. Share the dbSession.
  6. ...
