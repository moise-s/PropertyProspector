# PropertyProspector

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.13+-blue.svg" alt="Python 3.13+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT">
</div>

A comprehensive tool that allows real estate websites scraping, builds a centralized property database, and leverages data analytics to guide your search for your next perfect home.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [License](#license)

## 🏠 Overview

PropertyProspector is a real estate data collection and designed to help you find your ideal property. It allows the scrape of multiple real estate websites, normalizing the data into a consistent format, and storing it in a centralized database for easy querying and analysis.

## ✨ Features

- **Asynchronous Web Scraping**: Efficiently scrapes property listings using asynchronous programming;
- **Modular Architecture**: Easily extendable to support additional real estate websites;
- **Persistent Storage**: Stores all property data in a SQLite database;
- **Data Deduplication**: Updates existing listings and adds new ones;
- **Structured Data Model**: Consistent property representation across different sources;

## 🏗️ Architecture

### Core Components

#### BaseScraper Class

The `BaseScraper` abstract class is the foundation of PropertyProspector's scraping architecture. It defines a consistent interface that all website-specific scrapers must implement:

```python
class BaseScraper(ABC):
    @abstractmethod
    async def scrape(self) -> str:
        pass

    @abstractmethod
    async def parse(self, raw_data: str) -> List[PropertyListing]:
        pass

    def upload(self, listings: List[PropertyListing]) -> None:
        # Implementation for database operations
        pass

    async def run(self):
        raw_data = await self.scrape()
        listings = await self.parse(raw_data)
        self.upload(listings)
```

This design is crucial for several reasons:

1. **Standardization**: Ensures all scrapers follow the same workflow (scrape → parse → upload)
2. **Separation of Concerns**: Each method has a single responsibility
3. **Extensibility**: Makes it easy to add new website scrapers
4. **Code Reuse**: Common functionality (like database operations) is implemented once

#### Asynchronous Execution

The main application uses `asyncio` to run all scrapers concurrently:

```python
async def main():
    scrapers = [
        ImovelWebScraper(),
        # Future scrapers will be added here
    ]

    # Run all scraper tasks concurrently
    await asyncio.gather(*(scraper.run() for scraper in scrapers))
```

This approach allows PropertyProspector to efficiently scrape multiple websites simultaneously, significantly reducing the total execution time.

#### Data Models

PropertyProspector uses two complementary data models:

1. **Pydantic Models** (`PropertyListing`): For data validation and transformation
2. **SQLAlchemy Models** (`Listing`): For database operations

This dual-model approach ensures data integrity throughout the application.

## 🚀 Installation

### Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) - A fast Python package installer and resolver

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/PropertyProspector.git
   cd PropertyProspector
   ```

2. Install dependencies using uv (make sure you have `uv` installed):
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

## 🖥️ Usage

Run the application:

```bash
uv run main.py
```

This will:
1. Scrape property listings from configured websites;
2. Parse the raw data into structured property listings;
3. Store the listings in the database (`db/database.db`);
4. Print a summary of added and updated listings;

## 🧪 Testing

PropertyProspector uses a comprehensive testing strategy to ensure its reliability and correctness, which includes:

### Test Framework

-   **pytest:** `pytest` is used, a powerful and flexible testing framework, to write and execute our tests.

### How to Run Tests

1. **Run all tests**:
    ```bash
    uv run pytest
    ```

## 🔮 Future Improvements

- **Additional Websites**: Support for more real estate websites will be added;
- **Pagination Support**: ImovelWeb scraper will be enhanced to scrape all pages of results (currently only scrapes the first page);
- **Price Change Tracking**: Explicit tracking of properties with price changes;
- **Data Analytics**: Advanced filtering and recommendation features;
- **User Interface**: Web or desktop interface for easier interaction;

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
