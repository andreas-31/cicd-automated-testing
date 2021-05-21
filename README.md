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

#### Create Fake REST API Artifact (ZIP File)

#### API Integration Tests with Newman (Postman)
Newman is installed. Regression tests and Data Validation tests are run. The results of both test suites are published as artifacts in the pipeline.

### Deployment Stage
