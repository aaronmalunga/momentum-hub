# Storage & Persistence Design

## Overview

This codebase implements storage and persistence primarily using SQLite as the reliable and robust backend for data management. The persistent data is stored in the `momentum.db` SQLite database file.

While JSON was initially embraced for its simplicity, readability, and alignment with a CLI-first development approach in early stages or configuration, the current implementation uses SQLite for full persistence and data integrity.

## Storage Layer Responsibilities

The storage layer, encapsulated mainly in the `momentum_db.py` module, handles the following core responsibilities:

- **Serialization and Deserialization**
  Transforms `Habit`, `Completion`, `Category`, and `Goal` objects to and from database rows by converting Python objects to SQLite compatible fields (e.g., ISO-formatted timestamps as strings) and vice versa.

- **Data Persistence**
  Ensures that habit and event log data persist reliably between sessions by performing CRUD operations directly on the SQLite database.

- **Schema Integrity and Migrations**
  Manages the creation of required tables (`habits`, `completions`, `categories`, `goals`) with appropriate columns and constraints, including foreign key constraints.
  Supports database schema migrations by checking for missing columns and adding them when necessary (e.g., `reactivated_at` and `category_id` fields).

- **Soft Deletes for Historical Integrity**
  Implements soft delete functionality by using `is_active` flags to allow data deactivation without permanent deletion, preserving historical records for analysis.

## Extensibility & Clean Architecture

The codebase follows clean architecture principles by decoupling the storage layer from the business logic, which makes it straightforward to replace or extend the storage backend without affecting core application logic.

This design supports future extensibility, for example, by enabling migration or integration with SQLite or alternative storage mechanisms without major refactoring of business rules.

## Data Model Schema

The SQLite data model schema used by the application is as follows:

### habits Table

| Column             | Type     | Description                              |
|--------------------|----------|------------------------------------------|
| id                 | INTEGER  | Primary key, autoincrement               |
| name               | TEXT     | Name of the habit (not null)             |
| frequency          | TEXT     | Frequency of habit (e.g., daily, weekly) |
| notes              | TEXT     | Optional notes                           |
| reminder_time      | TEXT     | Optional reminder time                   |
| evening_reminder_time | TEXT   | Optional evening reminder time           |
| streak             | INTEGER  | Current streak count (default 0)        |
| created_at         | TEXT     | Habit creation timestamp (ISO format)   |
| last_completed     | TEXT     | Timestamp of last completion (ISO)      |
| is_active          | INTEGER  | Soft delete flag (1=active, 0=inactive) |
| reactivated_at     | TEXT     | Timestamp if habit was reactivated       |
| category_id        | INTEGER  | Foreign key to categories table          |

### completions Table

| Column    | Type    | Description                              |
|-----------|---------|------------------------------------------|
| id        | INTEGER | Primary key, autoincrement               |
| habit_id  | INTEGER | Foreign key to `habits.id` (not null)   |
| date      | TEXT    | Timestamp of habit completion (ISO format) |

Other tables include `categories` and `goals`, each with their respective fields and foreign key relationships.

## Summary

- The application uses SQLite as the primary persistent storage system.
- Serialization and deserialization between Python objects and SQLite tables ensure data consistency.
- Soft deletes and schema migrations support data integrity and evolutionary development.
- Clean architecture allows easy future substitution or extension of the storage layer.
- JSON remains a valued data format for simplicity and CLI-related tasks but is not the primary persistence mechanism.

This approach balances simplicity, structure, and extendibility to support the application's goal of managing habit tracking and event logging effectively.
