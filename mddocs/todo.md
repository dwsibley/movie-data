To-do list for ideas, improvements etc.

- [ ] More filters - ranges for integers, ranges for dates.
- [ ] Folder and module layout.  I like to a differenet folder/module layout that is more modular and extensible to add other models, sets of end points etc.  Consider versioning.
- [ ] Code Cleanup.  Dry opportunities...starting with crud.py file, etc.
- [ ] API versioning.
- [ ] Add authentication. Just API token first then user/pass driven for API.
- [ ] Authorization - set up permission levels.
- [ ] Working user model and maybe even user registration flow.
- [ ] Try migrations with SQLAlchemy.  Look into Alembic.
- [ ] Consider simplifying or having multiple response schemas.  For example respond list values can be simple strings as in POST instead of including id, name object.
- [ ] Work on some simple UI elements and look into any hosting solutions in GCP (object storage hosting like AWS an option?).
- [ ] Try NoSQL data options in GCP.
- [ ] Extend CI/CD to include testing and possible deployment manual step.
- [ ] Add some testing. Reference: https://fastapi.tiangolo.com/tutorial/testing/