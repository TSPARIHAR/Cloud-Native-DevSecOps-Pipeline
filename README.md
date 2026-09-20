# 🚀 DevSecOps Cloud-Native 2-Tier Flask App (CI/CD + K8s)

[![Jenkins](https://img.shields.io/badge/Jenkins-2.401+-D24939?style=for-the-badge&logo=jenkins&logoColor=white)](https://www.jenkins.io/)
[![SonarQube](https://img.shields.io/badge/SonarQube-Community-4E9BCD?style=for-the-badge&logo=sonarqube&logoColor=white)](https://www.sonarqube.org/)
[![Trivy](https://img.shields.io/badge/Trivy-CVE_Scanner-1976D2?style=for-the-badge&logo=aquasec&logoColor=white)](https://www.aquasec.com/products/trivy/)
[![Docker](https://img.shields.io/badge/Docker-24.0+-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-kind-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![Helm](https://img.shields.io/badge/Helm-v3-0F1689?style=for-the-badge&logo=helm&logoColor=white)](https://helm.sh/)

An automated, enterprise-grade **DevSecOps pipeline** deploying a high-availability **Flask + Redis** two-tier microservice onto a local Kubernetes (`kind`) cluster. 

This repository demonstrates persistent CI/CD infrastructure, static code analysis, vulnerability scanning, custom Helm orchestration, and non-blocking health probe architecture.

---

## 🏗️ Architecture & Pipeline Flow

```text
  [ Developer Commit ] 
         │
         ▼
 ┌─────────────────┐
 │ Jenkins Engine  │ ──► [ Stage 1: Workspace Prep & Local Copy ]
 └────────┬────────┘
          │
          ├──► [ Stage 2: SonarQube Static Code Analysis ]
          │
          ├──► [ Stage 3: Multi-Stage Docker Build (Gunicorn/WSGI) ]
          │
          ├──► [ Stage 4: Trivy Security Scan (HIGH / CRITICAL CVEs) ]
          │
          ├──► [ Stage 5: Push Image to Docker Hub Registry ]
          │
          └──► [ Stage 6: Helm Release Deployment to K8s Cluster ]
                                     │
                                     ▼
                      ┌─────────────────────────────┐
                      │    Kubernetes (kind)        │
                      │  ┌───────────────────────┐  │
                      │  │ Flask App (Gunicorn)  │  │
                      │  └──────────┬────────────┘  │
                      │             │               │
                      │  ┌──────────▼────────────┐  │
                      │  │  Redis Cache Pod      │  │
                      │  └───────────────────────┘  │
                      └─────────────────────────────┘

```
## ✨ Key Technical Highlights & Engineering Decisions

* **Persistent DevOps Infrastructure:** Deployed containerized **Jenkins** (`jenkins_home`) and **SonarQube** (`sonarqube_data`) using named Docker volumes to maintain configuration persistence across system reboots.
* **Docker-out-of-Docker (DooD) Execution:** Enabled docker socket sharing (`-v /var/run/docker.sock`) and assigned correct GID group access (`--group-add`) to allow Jenkins to build, scan, and push images natively without running unprivileged nested Docker.
* **Decoupled K8s Health Probes:** Reconfigured Helm deployment readiness/liveness probes from `/` to `/health` (returning HTTP 200 OK independently of Redis availability) to eliminate `CrashLoopBackOff` state during cold starts.
* **Cross-Bridge Network Binding:** Resolved x509 TLS certificate handshake failures between Jenkins containers and the local K8s control plane by joining the Jenkins container directly to the `kind` Docker bridge network.
* **Production-Grade Containerization:** Bound Gunicorn explicitly to `0.0.0.0:5000` with multiple worker processes, utilizing multi-stage builds to strip unnecessary compile dependencies.

## 🛠️ Tech Stack & Tools

* **Application Code:** Python 3.10+, Flask, Gunicorn WSGI, Redis Python Client
* **CI/CD Orchestration:** Jenkins (Containerized LTS)
* **Static Application Security Testing (SAST):** SonarQube Community Edition
* **Container Security (Vulnerability Scan):** Trivy CLI
* **Containerization & Registry:** Docker Engine, Docker Hub
* **Cluster Management & Orchestration:** Kubernetes (`kind`), Helm v3
* **OS & Runtime:** Ubuntu WSL2

---

## 📁 Repository Structure
```
.
├── app/
│   ├── app.py              # Flask REST API & Redis connection logic
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Multi-stage production container build
├── helm-chart/             # Helm chart definitions
│   ├── Chart.yaml          # Helm metadata
│   ├── values.yaml         # Configuration values (probes, image tags)
│   └── templates/          # K8s manifests (Deployment, Service, Redis)
├── Jenkinsfile             # Declarative CI/CD pipeline definition
└── README.md               # Project documentation

```

## ⚡ Quick Start & Deployment Guide
### Prerequisites
Docker Engine installed and running

kubectl and helm installed on your local host

A local kind Kubernetes cluster active (kind create cluster --name dev-cluster)

1. Clone the Repository
```bash
git clone [https://github.com/TSPARIHAR/Cloud-Native-DevSecOps-Pipeline.git](https://github.com/TSPARIHAR/Cloud-Native-DevSecOps-Pipeline.git)
cd devsecops-flask-redis
```
2. Local Kubernetes Deployment (Via Helm)
```bash
helm upgrade --install flask-app ./helm-chart -n default
```
3. Verify Pod Health
```Bash
kubectl get pods -l app.kubernetes.io/instance=flask-app
```
4. Access the Application
Forward container port 5000 to port 9090 on your local IPv4 loopback:

```Bash
POD_NAME=$(kubectl get pods -n default -l "app.kubernetes.io/instance=flask-app" --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}')

kubectl port-forward pod/$POD_NAME --address 127.0.0.1 9090:5000 -n default
```
Test the endpoint in a separate terminal:

```Bash
curl -i [http://127.0.0.1:9090/health](http://127.0.0.1:9090/health)
```
Expected Response:

```HTTP
HTTP/1.1 200 OK
Server: gunicorn
Content-Type: application/json
{"service":"flask-redis-api","status":"healthy"}
```
## 🛡 DevSecOps Pipeline Stages
Checkout: Clones source code and verifies workspace directory structure.

Static Code Analysis: Executes SonarQube scanning for code smells, bugs, and security vulnerabilities.

Container Build: Uses a multi-stage Dockerfile with explicit non-root bindings (0.0.0.0:5000).

CVE Scanning: Runs Trivy against built images to detect HIGH and CRITICAL vulnerabilities.

Registry Push: Authenticates and pushes tagged images to Docker Hub.

Kubernetes Rollout: Performs continuous deployment to kind via Helm upgrades.

## 📝 License
Distributed under the MIT License. See LICENSE for details.


---

### Step-by-Step Instructions to Push to GitHub

1. **Create the files locally in your project folder:**
   ```bash
   cd ~/devsecops_project
   nano README.md    # Paste the text above and save
Initialize Git and verify your .gitignore:

```bash
git init
Ensure .gitignore contains:
```

```.gitignore
__pycache__/
*.pyc
.env
*.log
Stage, Commit, and Push to GitHub:
```
```bash
git add .
git commit -m "feat: complete devsecops pipeline for flask-redis on kubernetes"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/devsecops-flask-redis.git
git push -u origin main
```
