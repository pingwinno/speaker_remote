import logging

if __name__ == "__main__":
    import uvicorn
    import web_app

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    uvicorn.run(web_app.get_web_app(), host="0.0.0.0", port=8000)
