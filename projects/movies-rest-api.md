# Movies REST API

## Overview

A Python and Flask REST API backed by SQLite for storing movies and related reviews.

## What I built

- Movie and review data models with primary-key and relationship handling
- CRUD routes for creating, reading, updating, and deleting movies
- Review lookup through a related-resource endpoint
- Input validation and clear error responses
- Duplicate-title protection
- Parameterized SQL queries for user-supplied values
- Persistence checks after closing and reopening the database
- API verification through Postman, command-line requests, and expected HTTP status codes

## Quality and API evidence

The project covers `200`, `201`, `204`, `400`, `404`, and `409` behavior. I tested normal requests, missing fields, unknown IDs, duplicate records, restart persistence, and SQL-injection-style input to confirm that user input was treated as data rather than executable SQL.

## Tools

`Python` · `Flask` · `SQLite` · `SQL` · `REST` · `JSON` · `Postman` · `Swagger/OpenAPI` · `curl`

## What this project demonstrates

This project shows that I can connect backend implementation with QA thinking: define expected behavior, test both successful and failing paths, inspect data relationships, and document results in a way another developer can reproduce.

