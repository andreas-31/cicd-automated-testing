# Ensuring Quality Releases
CI/CD pipeline in Azure DevOps for automated building, deployment, testing, monitoring, and logging.

[![Build Status](https://dev.azure.com/Agaupmann0652/CICD-Automated-Testing/_apis/build/status/andreas-31.cicd-automated-testing?branchName=main)](https://dev.azure.com/Agaupmann0652/CICD-Automated-Testing/_build/latest?definitionId=3&branchName=main)

## Project Overview
| ![Azure DevOps CI/CD Pipeline drives various services and tools for automated building, deployment, testing, monitoring, and logging](https://user-images.githubusercontent.com/20167788/119121028-39be4e80-ba2d-11eb-9156-18ab7a2c11b5.png) | 
|:--:| 
| *Azure DevOps CI/CD Pipeline drives various services and tools for automated building, deployment, testing, monitoring, and logging.* |

## Azure DevOps
The subsequently described CI/CD pipeline is defined in the YAML file ```azure-piplines.yaml``` that is contained in this GitHub repository.

## Description of the Stages of the CI/CD Pipeline
### Build Stage
#### Terraform (Infrastructure as Code)
Terraform is used in the CI/CD pipeline to provision and manage resources in Azure cloud. In order to allow Terraform to create resources in Azure, a [Service Connection](https://docs.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops&tabs=yaml) to Azure Resource Manager (ARM) using service principal authentication has been configured in the Project Settings in Azure DevOps. Terraform uses the Azure credentials that are made available by the service connection as environment variables: ARM_CLIENT_ID, ARM_CLIENT_SECRET, ARM_SUBSCRIPTION_ID, and ARM_TENANT_ID.

Terraform has been configured to store state remotely in Azure storage account by following this tutorial: [Store Terraform state in Azure Storage](https://docs.microsoft.com/en-us/azure/developer/terraform/store-state-in-azure-storage).

| ![Azure resources created by Terraform](https://user-images.githubusercontent.com/20167788/119124719-45ac0f80-ba31-11eb-80cd-02068b97e80f.PNG) | 
|:--:| 
| *Azure resources created by Terraform.* |

| ![Azure Storage Explorer showing Terraform state (.tfstate) files stored in Azure storage account](https://user-images.githubusercontent.com/20167788/119124722-4644a600-ba31-11eb-8f1d-eda3bdceca4c.PNG) | 
|:--:| 
| *Azure Storage Explorer showing Terraform state files (.tfstate) files stored in Azure storage account.* |

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

The API Data Validation Test Suite first creating employee data and then validates that the employee data has been correctly provided by the web application:
|Data Validation Testcase |API Endpoint |
|--- | --- |
|V1 Create Employee Data |http://dummy.restapiexample.com/api/v1/create|
|V2 Validate Employee Data |http://dummy.restapiexample.com/api/v1/employee/{{newId}}|

### Deployment Stage
#### Deploy Fake REST API Artifact to Azure App Services
The application package (ZIP file) containing the web app is deployed to the app service that has earlier been created by Terraform in the build stage. Azure App Service registers a domain name for the web app 

#### Deploy and Run Selenium on Ubuntu VM
Functional UI test are run in Python scripts by using the [Selenium WebDriver](https://pypi.org/project/selenium/) Python module and the [chromedriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) driver for controlling the Chromium web browser in non-GUI mode.

The test website [saucedemo.com/](https://www.saucedemo.com/) is used for running functional UI tests like logging into the webshop, adding items to the shopping cart, and then removing items again. After adding or removing an item, it is verified that the item is really in or no longer in the shopping cart, respectively.

#### Run Load Tests With JMeter and Publish Them
