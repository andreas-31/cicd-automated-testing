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
#### Build: Terraform

#### Build: Create Fake REST API Artifact (ZIP File)

#### API Integration Tests with Newman (Postman)
Newman is installed. Regression tests and Data Validation tests are run. The results of both test suites are published as artifacts in the pipeline.

### Deployment Stage
