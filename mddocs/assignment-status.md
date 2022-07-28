## Assignment Status

Decisions and progress made on the original [assignment](original-assignment.md).

### Decisions

I chose FastAPI and SQLAlchemy since those seem to be used by originators of the assignment.  I also haven't worked with them much so I thought it would be good to learn.

I used SQLite to originally try out FastAPI/SQLAlchemy and work locally.  I used Cloud SQL with Postgres for the deployment.

For the data set I chose the Netflix data but labled the model and API as such and could add other models or an combination model in the future.

### Progress 

#### Main objectivies
- [x] Create API and documentation - API created with Fast API which has built-in API documentation for Netflix title information.  Utilized the built-in OpenAPI-based documentation which is listed on the site /docs folder.

- [x] Rows of data with search, filter, sorting, and pagination - Pagination comes with Fast API.  I implemented a basic search for now based on title and description.  For filtering I used fastapi-filter which is easy to add quick filtering but has some limitations (no apparent support for date/datetime ranges).

- [ ] Aggregated summary data.  Not sure exactly what this is meant to cover, but for now no count, max, min etc. options opened up through the API.  Filtering and then counting, measuring locally, etc. would be a current option.  I looked for tooling for this sort of thing but didn't find anything in the time searching.  Would like circle back to this.

- [x] Modify data in the database - PUT and PATCH methods implemented for Netflix titles.

- [x] Use Flask/FastAPI Python for any back-end code if necessary.  Chose FastAPI.

- [x] Push data into a database of your choice.  Chose Postgres through SQLAlchemy and loaded Netflix data through POST API.

- [x] Check in the code to your personal GitHub account. Done.

- [x] Deploy the application in Google Cloud (Use free tier with new account setup).  Preferably you can use managed services (App Engine, Cloud Run, CloudSQL, etc.).  Done using Cloud Run and Cloud SQL primarily.

#### Extra Points
- [ ] Unit Testing implemented.  I haven't added any unit testing though I do have scripts used to test end points.
- [x] Continuous Integration/Continuous Deployment features set up (CI/CD) E.g. CircleCI, Travis, GCP Cloud Build, Github Actions, etc. Not a full CI/CD flow but a simple solution for now for deployments integrating github to Cloud Build where a tag with "release" automatically gets built and deployed.
- [ ] Authentication implemented so that only authenticated users are capable of accessing the API.  Currently working on this.  May start with a simple token needed for API.