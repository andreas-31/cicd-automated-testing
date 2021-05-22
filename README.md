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
The application package (ZIP file) containing the web app is deployed to the app service that has earlier been created by Terraform in the build stage. Azure App Service registers a domain name for the web app 

#### Deploy and Run Selenium on Ubuntu VM
Functional UI test are run in Python scripts by using the [Selenium WebDriver](https://pypi.org/project/selenium/) Python module and the [chromedriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) driver for controlling the Chromium web browser in non-GUI mode.

The test website [saucedemo.com](https://www.saucedemo.com/) is used for running functional UI tests like logging into the webshop, adding items to the shopping cart, and then removing items again. After adding or removing an item, it is verified that the item is really in or no longer in the shopping cart, respectively.

#### Run Load Tests With JMeter and Publish Them
