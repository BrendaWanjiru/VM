A virtual machine management platform with automation, role-based access control, and payment integration.

Project: VM Management Platform with Role-Based Access and Automation

Objective: Using the programming languages and frameworks you're most familiar with, create a simplified web-based virtual machine (VM) management platform. The platform should allow users/customers to manage their Virtual machines (VMs), including creating backups, performing basic automation tasks like starting/stopping/, and handling payments for services. 
Security features such as Single Sign-On (SSO) and role-based access control should be integrated, along with CI/CD automation for deployment on a Kubernetes cluster.


Project Requirements
1. User Management and Role-Based Access:

        Build a basic user management system that allows for multiple roles (e.g., Admin, Standard User, and Guest).
        Admin users can create, update, and delete VMs, move VMs between users, and track user activities.
        Standard Users can manage their own VMs, create backups, and view billing information.
        Guest users can view the available services but cannot perform any actions.

2. VM Management Automation:

        Implement a simple VM management interface where users can create and delete virtual machines.
        Add the ability to move VMs between users, with notifications sent to the original and new users, including an audit log of the action.
        Create a backup and snapshot feature where users can back up their VMs and get real-time pricing based on the disk size selected.

3. Payment System Integration:

        Integrate a mock payment system where users must pay to access certain features, such as creating additional VMs or backing up existing ones.
        Include a simple admin panel for tracking payments and suspending user accounts if payments are not received.
        For the purpose of this exercise, mock payments and implement a simple Test Mode where a transaction always succeeds.

4. Security and Single Sign-On (SSO):

        Implement Single Sign-On (SSO) using any available authentication provider (e.g., Google, GitHub).
        Secure the platform by implementing Role-Based Access Control (RBAC) and ensuring only authorized users can access certain features.
        Use secure API endpoints and ensure that sensitive data is protected using best practices (e.g., JWTs, OAuth2).

5. Rate Plans and Subscription Management:

        Add Rate Plans (e.g., Platinum, Gold, Silver, Bronze) that limit the number of VMs or backups users can create.
        Implement a system where users can upgrade or downgrade their subscription plans.
        Multi-client accounts should be allowed, where a parent client can manage multiple users under a single billing account.

6. Kubernetes Deployment:

        Containerize the application using Docker or Cloud Native Buildpacks.
        Deploy the application to a Kubernetes cluster (single-node or multi-node setup on your VM).
        Configure SSL for secure communication.
        Set up a CI/CD pipeline using GitHub Actions that automates testing, building, and deployment to the Kubernetes cluster.

7. Documentation and Testing:

        Provide a README file with instructions on how to set up and run the application.
        Include unit tests for key features (e.g., VM creation, role-based access control, payment handling).
        Ensure detailed documentation of how the CI/CD pipeline is set up and how the deployment works in the Kubernetes environment.


Skills Being Tested:
        Frontend Development: Creating a user-friendly interface with role-based access and user management.
        Backend Development: Building APIs to handle VM management, user roles, payments, and backups.
        Automation & CI/CD: Setting up GitHub Actions to automate testing, building, and deploying the containerized application to a Kubernetes cluster.
        Security: Implementing SSO, secure API endpoints, and role-based access control.
        Containerization & Kubernetes: Deploying the application on a Kubernetes cluster, ensuring it's accessible and secure.


### Background tasks
Background tasks handle notifications such as:

- Sharing the transfer of virtual machines between users.
- Activation and deactivation of an account by an administrator

  ## Docker
  docker-compose -f docker-compose.local.yml build
docker-compose -f docker-compose.local.yml up
  
### KUBERNETES

~~~bash
kubectl apply -f compose/kubernetes/namespaces/production.yaml
kubectl apply -f compose/kubernetes/configmaps/.
kubectl apply -f compose/kubernetes/secrets/.
kubectl apply -f compose/kubernetes/persistence_volumes/storage_classes/.
kubectl apply -f compose/kubernetes/persistence_volumes/.
~~~

To add traefik as ingress controller:

1. create traefik services: `kubectl apply -f compose/kubernetes/ingress/traefik-service.yaml`
2. Get the external IP address and assign a domain name to the IP address.
3. Make sure traefik's ConfigMaps are created: `kubectl apply -f compose/kubernetes/configmaps/.`
3. After DNS records have been updated, create the traefik controller: `kubectl apply -f compose/kubernetes/ingress/traefik-controller.yaml`
