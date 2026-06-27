# Application Service

Application Service manages freelancer proposals for jobs and coordinates the acceptance workflow between Job Service, Message Service, and Notification Service.

## Responsibilities

- Let freelancers apply to open jobs.
- Let freelancers list and withdraw their own applications.
- Let job-owning clients view, accept, or reject applications.
- Update job status when an application is accepted.
- Create a chat room for the accepted client/freelancer pair.
- Provide internal application data and statistics to Admin Service and Job Service.

## Features

- Job validation against Job Service before application creation.
- One application per freelancer per job through a model uniqueness constraint.
- Atomic acceptance workflow: lock application, update job to `in_progress`, create chat room, accept one proposal, and reject remaining pending proposals.
- Notification events for application received, proposal accepted, and proposal rejected.

## API Endpoints

Base path: `/api/`

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `applications/create/` | Freelancer JWT | Apply to an open job. |
| `GET` | `applications/my/` | Freelancer JWT | List the authenticated freelancer's applications. |
| `PATCH` | `applications/<application_id>/withdraw/` | Freelancer JWT | Withdraw a pending application owned by the freelancer. |
| `GET` | `applications/jobs/<job_id>/applications/` | Owning client JWT | List applications for a job after verifying ownership with Job Service. |
| `PATCH` | `applications/<application_id>/accept/` | Owning client JWT | Accept a pending application and start the job/chat workflow. |
| `PATCH` | `applications/<application_id>/reject/` | Owning client JWT | Reject a pending application. |

## Internal Service Endpoints

Internal endpoints use `X-Service-Key: <SERVICE_API_KEY>`.

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `internal/jobs/<job_id>/freelancer/` | Return the freelancer id from the first application found for a job. |
| `GET` | `internal/applications/` | Return paginated application summaries. |
| `GET` | `internal/applications/stats/` | Return application counts by status. |
| `GET` | `internal/applications/<application_id>/` | Return one application summary. |

## Authentication

User APIs use `myapp.authentication.CustomJWTAuthentication` and role permissions for clients/freelancers. Internal endpoints use `X-Service-Key`.

## Environment Variables

| Variable | Purpose |
| --- | --- |
| `DJANGO_SECRET_KEY` | Django secret key. |
| `DEBUG` | Enables debug mode when set to `1`, `true`, or `yes`. |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts. Defaults to `*`. |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | MySQL database configuration. |
| `JWT_PUBLIC_KEY_PATH` | Public key used to verify Auth Service JWTs. |
| `SERVICE_API_KEY` | Shared key for internal calls. |
| `JOB_SERVICE_URL` | Used to verify jobs and update job status. |
| `MESSAGE_SERVICE_URL` | Used to create chat rooms after acceptance. |
| `NOTIFICATION_SERVICE_URL` | Used by the shared notification client. |
| `*_SERVICE_URL` | Additional service URL settings loaded by settings. |

## Setup

```bash
cd ApplicationService_labora
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8007
```

## Service Architecture

- Django project: `ApplicationService`
- App: `myapp`
- Authentication: `myapp.authentication.CustomJWTAuthentication`
- Role permissions: `myapp.role_permissions`
- Internal permission: `myapp.permissions.internal_service.IsInternalService`
- Outbound dependencies: Job Service, Message Service, and Notification Service

## Database Models

- `Application`: stores `job_id`, `client_id`, `freelancer_id`, cover letter, proposed amount, delivery time, status, and timestamps.
- `ProposalMessage`: stores messages linked to an application. No API currently exposes proposal-message CRUD.

## Notification/Event Flow

- Creating an application sends `application_received` to the client.
- Accepting an application sends `proposal_accepted` to the freelancer after job/chat workflow succeeds.
- Rejecting an application sends `proposal_rejected` to the freelancer.
