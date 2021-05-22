# Ensuring Quality Releases
CI/CD pipeline in Azure DevOps for automated building, deployment, testing, monitoring, and logging.

[![Build Status](https://dev.azure.com/Agaupmann0652/CICD-Automated-Testing/_apis/build/status/andreas-31.cicd-automated-testing?branchName=main)](https://dev.azure.com/Agaupmann0652/CICD-Automated-Testing/_build/latest?definitionId=3&branchName=main)

## Project Overview
| ![Azure DevOps CI/CD Pipeline drives various services and tools for automated building, deployment, testing, monitoring, and logging](https://user-images.githubusercontent.com/20167788/119121028-39be4e80-ba2d-11eb-9156-18ab7a2c11b5.png) | 
|:--:| 
| *Azure DevOps CI/CD Pipeline drives various services and tools for automated building, deployment, testing, monitoring, and logging.* |

## Azure DevOps
The subsequently described CI/CD pipeline is defined in the YAML file ```azure-piplines.yaml``` that is contained in this GitHub repository. The declarations in the YAML file are evaluated by Azure Pipelines that is part of Azure DevOps. When the pipeline runs, the system begins to run one or more jobs on [Azure Pipelines Agents](https://docs.microsoft.com/en-us/azure/devops/pipelines/agents/agents). An agent is computing infrastructure with installed agent software that runs one job at a time. All except one pipeline steps are executed on Microsoft-hosted agents. The functional UI tests are run on self-hosted agent. It is an Ubuntu 18.04 virtual machine that is created by Terraform and was added to an [Azure Pipelines environment](https://docs.microsoft.com/en-us/azure/devops/pipelines/process/environments) called "TEST". In summary, the following configurations have been made in Azure Pipelines:
- Declaring and setting of variables in ```azure-piplines.yaml```:
  * for Azure: azureLocation, azureResourceGroup, azureApplicationType, azureVirtualNetworkName, azureAddressPrefixTest, azureAddressSpace, subscriptionConnection
  * for Terraform: tf-resource-group-name, tf-storage-account-name, tf-container-name, tf-blob-key-name, terraformDirectory
- Declaring and setting of variables in Azure Pipelines Web Interface
  * SSH public key for Ubuntu VM (id_rsa.pub): ssh-public-key
  * for Azure Log Analytics: azure_log_customer_id, azure_log_shared_key
- Definition of Azure pipelines environment "TEST". Adding the Ubuntu VM to this environment with tag "ubuntu".
- Adding SSH private key (id_rsa) as secure file to Azure Pipelines Library: the ["Install SSH Key"](https://docs.microsoft.com/en-us/azure/devops/pipelines/tasks/utility/install-ssh-key) task adds the SSH private key to key manager (ssh-agent) running on Azure Pipelines agents.

## Description of the CI/CD Pipeline
### Structure of the CI/CD Pipeline

| ![Azure Pipelines showing the two stages of the CI/CD pipeline: Build and Deployment](https://user-images.githubusercontent.com/20167788/119217972-156e7a80-bade-11eb-8552-bb91812958fa.PNG) | 
|:--:| 
| *Azure Pipelines showing the two stages of the CI/CD pipeline: Build and Deployment.* |

| ![Azure Pipelines showing jobs for each stage](https://user-images.githubusercontent.com/20167788/119217974-16071100-bade-11eb-9ab2-a1c285e4f307.PNG) | 
|:--:| 
| *Azure Pipelines showing jobs for each stage.* |

### Build Stage
The Build job in the Build stage performs several steps:
- Install an SSH Key: installs SSH key on Azure Pipelines agent where the Terraform commands will be run.
- Terraform: credentials, initialize, validate, plan, apply, show
- Newman: install Newman, run API integration tests, publish results
- Webapp Artifact: Create and upload ZIP archive containing Fake REST API webapp
#### Terraform (Infrastructure as Code)
Terraform is used in the CI/CD pipeline to provision and manage resources in Azure cloud. In order to allow Terraform to create resources in Azure, a [Service Connection](https://docs.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops&tabs=yaml) to Azure Resource Manager (ARM) using service principal authentication has been configured in the Project Settings in Azure DevOps. Terraform uses the Azure credentials that are made available by the service connection as environment variables: ARM_CLIENT_ID, ARM_CLIENT_SECRET, ARM_SUBSCRIPTION_ID, and ARM_TENANT_ID.

Terraform has been configured to store state remotely in Azure storage account by following this tutorial: [Store Terraform state in Azure Storage](https://docs.microsoft.com/en-us/azure/developer/terraform/store-state-in-azure-storage). The parameters for configuring the remote Terraform backend are defined as variables in ```azure-piplines.yaml``` (resource_group_name, storage_account_name, container_name, key) or queried at pipeline runtime with Azure CLI (access_key for Azure storage account).

| ![Azure Storage Explorer showing Terraform state (.tfstate) files stored in Azure storage account](https://user-images.githubusercontent.com/20167788/119124722-4644a600-ba31-11eb-8f1d-eda3bdceca4c.PNG) | 
|:--:| 
| *Azure Storage Explorer showing Terraform state files (.tfstate) files stored in Azure storage account.* |

All Azure resources that are created by Terraform are contained in the Azure resource group ```cicd-automated-testing-rg```.
| ![Azure resources created by Terraform](https://user-images.githubusercontent.com/20167788/119124719-45ac0f80-ba31-11eb-80cd-02068b97e80f.PNG) | 
|:--:| 
| *Azure resources created by Terraform.* |

#### Build Fake REST API Artifact (ZIP File)
An ASP.NET application that implements a Fake REST API is stored in the subdirectory ```automatedtesting/jmeter/fakerestapi``` within this GitHub repository. That subdirectory is zipped and the ZIP file is stored as artifact in Azure DevOps. The application package will later be deployed in the deployment stage to Azure App Services.

#### API Integration Tests with Newman (Postman)
Newman is installed via npm (Node.js package manager). The API Regression Test Suite and the API Data Validation Test Suite are located in the subdirectory ```automatedtesting/postman``` and are run with Newman. The results of both test suites are published into Azure DevOps Test Hub where the results are summarized and visualized.

The API Regression Test Suite checks all API endpoints for successful response status codes and messages:
|Regression Testcase |API Endpoint |
|--- | --- |
|R1 Get All Employees|http://dummy.restapiexample.com/api/v1/employees|
|R2 Get Single Employee |http://dummy.restapiexample.com/api/v1/employee/{{id}}|
|R3 Create Employee |http://dummy.restapiexample.com/api/v1/create|
|R4 Update Employee |http://dummy.restapiexample.com/api/v1/update/{{id}}|
|R5 Delete Employee |http://dummy.restapiexample.com/api/v1/delete/{{id}}|

The API Regression Test Suite is run in the pipeline with this command:
```
newman run "automatedtesting/postman/API Regression Test Suite.postman_collection.json" --env-var newSalary="456" --environment automatedtesting/postman/DummyRestApiEnvironment.postman_environment.json --reporters cli,junit --reporter-junit-export newmanResults/junitReport-regressionTests.xml
```

The API Data Validation Test Suite first creating employee data and then validates that the employee data has been correctly provided by the web application:
|Data Validation Testcase |API Endpoint |
|--- | --- |
|V1 Create Employee Data |http://dummy.restapiexample.com/api/v1/create|
|V2 Validate Employee Data |http://dummy.restapiexample.com/api/v1/employee/{{newId}}|

The API Data Validation Test Suite is run in the pipeline with this command:
```
newman run "automatedtesting/postman/API Data Validation Test Suite.postman_collection.json" --environment automatedtesting/postman/DummyRestApiEnvironment.postman_environment.json --iteration-data automatedtesting/postman/Dummy-REST-API-Data.csv --reporters cli,junit --reporter-junit-export newmanResults/junitReport-dataValidationTests.xml
```
The ["Publish Test Results"](https://docs.microsoft.com/en-us/azure/devops/pipelines/tasks/test/publish-test-results) task is used to publish the results of the regression and data validation test runs in "JUnit" format to Azure Pipelines Test Plans.

### Deployment Stage
The following jobs are run in the Deployment stage:
- Job "Deployment: FakeRestApi": Deploy Azure Web App
- Job "Deployment: VMDeploy":
  * Deploy and Run Selenium on Ubuntu VM
  * Ingest Selenium logfile into Azure Log Analytics
- Job "RunLoadTestsWithJMeter":
  * JMeter installation and setup
  * Start JMeter to run load tests against the deployed webapp (Fake REST API): endurance tests and stress tests
  * Publish JMeter test reports as artifacts (ZIP files) in the pipeline
#### Deploy Fake REST API Artifact to Azure App Services
The application package (ZIP file) containing the web app is deployed to the app service that has earlier been created by Terraform in the build stage. Azure App Service registers a public domain name (URL) for the web app to be reachable over the Internet. The URL will be used as destination (target) for the requests generated by the JMeter load tests.

#### Deploy and Run Selenium on Ubuntu VM
##### Prepare Environment and Run Selenium
Functional UI test are defined and run in Python scripts by using the [Selenium WebDriver](https://pypi.org/project/selenium/) Python module and the [chromedriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) driver for controlling the Chromium web browser in non-GUI mode.

The test website [saucedemo.com](https://www.saucedemo.com/) is used for running functional UI tests like logging into the webshop, adding items to the shopping cart, and then removing items again. After adding or removing an item, it is verified that the item is really in or no longer in the shopping cart, respectively.

The Python scripts provides information of its status by writing log messages to the CLI as well as a Selenium logfile in CSV format: see [exemplary Selenium logfile in CSV format](cicd-automated-testing/automatedtesting/selenium/seleniumLogfile_2021-05-19_18-25-06.csv).

##### Azure Log Analytics: Ingest Selenium Logfile
The Selenium CSV logfile is ingested into an Azure Log Analytics workspace. The logs collected in Azure Monitor or Azure Log Analytics can be displayed and inspected with [Kusto](https://docs.microsoft.com/en-us/azure/data-explorer/kusto/query/tutorial?pivots=azuremonitor) queries.

| ![Kusto query for displaying all Selenium logs related to removed shopping cart items sorted by time generated](https://user-images.githubusercontent.com/20167788/119223458-dbab6d00-baf9-11eb-9a5d-6ebd91e30558.PNG) | 
|:--:| 
| *Kusto query for displaying all Selenium logs related to removed shopping cart items sorted by time generated.* |

#### Run Load Tests With JMeter and Publish HTML Test Reports
In this step, OpenJDK Java Runtime Environment is installed and JMeter tool is downloaded to the Azure Pipelines agent machine. Then, the Endurance Test Plan and the Stress Test Plan are run.
- Endurance_Test_Plan_CICD.jmx
- Stress_Test_Plan_CICD.jmx

##### Endurance Test Plan
The Endurance Test Plan is designed to send 6 HTTP requests every 10 seconds for 1 minute by using these settings:
- Constant Throughput Timer with Target Throughput of 6 samples per minute (applies to each thread group)
- Threat Groups:
  * GET Activity
  * POST Book
  * PUT Author
- Threat Groups configuration
  * Number of Threads (users): 2
  * Loop Count: Infinite
  * Specify Thread Lifetime: duration 60 seconds
- Parameters and JSON body values for GET, POST, and PUT requests are read from CSV files.

| ![JMeter Endurance Test Plan: Constant Throughput Timer settings](https://user-images.githubusercontent.com/20167788/119222242-a13ed180-baf3-11eb-89ec-0f48bc58c3f2.PNG) | 
|:--:| 
| *JMeter Endurance Test Plan: Constant Throughput Timer settings.* |

| ![JMeter Endurance Test Plan: Thread Groups settings](https://user-images.githubusercontent.com/20167788/119222243-a1d76800-baf3-11eb-8e7c-ba0be6285a68.PNG) | 
|:--:| 
| *JMeter Endurance Test Plan: Thread Groups settings.* |

| ![JMeter Endurance Test Plan: Parameters and JSON body values for GET, POST, and PUT requests are read from CSV files](https://user-images.githubusercontent.com/20167788/119228189-23d68980-bb12-11eb-88c2-3a56c8fc951a.PNG) | 
|:--:| 
| *Parameters and JSON body values for GET, POST, and PUT requests are read from CSV files.* |

##### Stress Test Plan
The Stress Test Plan is designed to send many HTTP requests in a short amount of time by using these settings:
- Threat Groups:
  * GET All Activities
  * GET All Books
  * Get All Authors
- Threat Groups configuration
  * Number of Threads (users): 30
  * Loop Count: Infinite
  * Specify Thread Lifetime: duration 30 seconds

| ![JMeter Stress Test Plan: "GET All" queries executed by 30 users over 30 seconds](https://user-images.githubusercontent.com/20167788/119222245-a26ffe80-baf3-11eb-8f1e-07634a72a410.PNG) | 
|:--:| 
| *JMeter Stress Test Plan: "GET All" queries executed by 30 users per thread group (amounts to 90 users in total) over 30 seconds.* |

##### Azure Pipelines: Publishing of JMeter Test Reports

| ![Azure Pipelines: list of pipeline artifacts showing zipped JMeter test reports](https://user-images.githubusercontent.com/20167788/119227438-2b942f00-bb0e-11eb-9f46-c674b3922eca.PNG) | 
|:--:| 
| *Azure Pipelines: list of pipeline artifacts showing zipped JMeter HTML reports for endurance and stress tests.* |

| ![JMeter Endurance Test Report (HTML format)](https://user-images.githubusercontent.com/20167788/119227757-c7726a80-bb0f-11eb-9f3a-a8e927bb33e6.PNG) | 
|:--:| 
| *JMeter Endurance Test Report (HTML format).* |

| ![JMeter Stress Test Report (HTML format)](https://user-images.githubusercontent.com/20167788/119227759-c80b0100-bb0f-11eb-8fa0-092b0023ffdf.PNG) | 
|:--:| 
| *JMeter Stress Test Report (HTML format).* |

##### Azure Monitor: Send Alarms by Email
Azure Monitor alarms have been configured for "cicd-app-AppService" (Fake REST API webapp):
- AppServiceCPU_TimeAlert: triggers whenever the maximum CPU time is greater than 30
- AppServiceHandleCountAlert: trigger whenever the maximum handles is greater than 50

| ![Azure Monitor: alarms configured for App Service "cicd-app-AppService"](https://user-images.githubusercontent.com/20167788/119224956-49a76280-bb01-11eb-8489-8394b0231a89.PNG) | 
|:--:| 
| *Azure Monitor: alarms configured for App Service "cicd-app-AppService".* |

| ![Azure Monitor: graph showing that alarm "AppServiceCPU_TimeAlert" did fire because maximum CPU time exceeded 30 seconds](https://user-images.githubusercontent.com/20167788/119224452-c553e000-bafe-11eb-9a76-4013dd4ebce6.PNG) | 
|:--:| 
| *Azure Monitor: graph showing that alarm "AppServiceCPU_TimeAlert" did fire because maximum CPU time exceeded 30 seconds.* |

| ![Azure Monitor: graph showing that alarm "AppServiceHandleCountAlert" did fire because maximum handle count exceeded 50](https://user-images.githubusercontent.com/20167788/119224446-c38a1c80-bafe-11eb-812a-c21fe4ad2f04.PNG) | 
|:--:| 
| *Azure Monitor: graph showing that alarm "AppServiceHandleCountAlert" did fire because maximum handle count exceeded 50.* |

| ![Azure Monitor: email notification for alert "AppServiceCPU_TimeAlert, Page 1" ](https://user-images.githubusercontent.com/20167788/119224450-c4bb4980-bafe-11eb-8217-f9255081c09e.PNG) | 
|:--:| 
| *Azure Monitor: email notification for alert "AppServiceCPU_TimeAlert", Page 1.* |

| ![Azure Monitor: email notification for alert "AppServiceCPU_TimeAlert, Page 2" ](https://user-images.githubusercontent.com/20167788/119224451-c553e000-bafe-11eb-8f2a-74dec969568b.PNG) | 
|:--:| 
| *Azure Monitor: email notification for alert "AppServiceCPU_TimeAlert", Page 2.* |

| ![Azure Monitor: email notification for alert "AppServiceHandleCountAlert", Page 1](https://user-images.githubusercontent.com/20167788/119224456-c6850d00-bafe-11eb-9406-487116e56aa0.PNG) | 
|:--:| 
| *Azure Monitor: email notification for alert "AppServiceHandleCountAlert", Page 1.* |

| ![Azure Monitor: email notification for alert "AppServiceHandleCountAlert", Page 2](https://user-images.githubusercontent.com/20167788/119224457-c6850d00-bafe-11eb-9f25-4981cff20df5.PNG) | 
|:--:| 
| *Azure Monitor: email notification for alert "AppServiceHandleCountAlert", Page 2.* |
