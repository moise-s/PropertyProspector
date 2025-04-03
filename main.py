import asyncio
from PropertyProspector.websites.imovel_web import ImovelWebScraper
from PropertyProspector.websites.zap_imoveis import ZapImoveisScraper


async def main():
    scrapers = [
        ImovelWebScraper(),
        ZapImoveisScraper(),
    ]

    # Run all scraper tasks concurrently.
    await asyncio.gather(*(scraper.run() for scraper in scrapers))


if __name__ == "__main__":
    asyncio.run(main())
